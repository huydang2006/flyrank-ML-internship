from __future__ import annotations

import getpass
import json
import os
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "work" / "outputs"
FEATURE_START, FEATURE_END = "2026-01-01", "2026-03-31"
LABEL_START, LABEL_END = "2026-04-01", "2026-04-30"
MIN_IMPRESSIONS = 100
LOW_CTR_THRESHOLD = 0.5
RANDOM_STATE = 42

FACT = (
    "read_parquet("
    "'hf://datasets/FlyRank/internship-warehouse/"
    "fact_content_daily_performance/**/*.parquet')"
)


def connect() -> duckdb.DuckDBPyConnection:
    token = os.environ.get("HF_TOKEN") or getpass.getpass(
        "Paste your HuggingFace READ token: "
    )
    connection = duckdb.connect()
    escaped_token = token.replace("'", "''")
    connection.execute(
        f"CREATE OR REPLACE SECRET hf (TYPE huggingface, TOKEN '{escaped_token}')"
    )
    connection.execute("SET http_retries = 10")
    connection.execute("SET http_timeout = 120")
    connection.execute("SET enable_http_metadata_cache = false")
    return connection


def load_contract(connection: duckdb.DuckDBPyConnection) -> tuple[pd.DataFrame, pd.DataFrame]:
    source = connection.sql(
        f"SELECT COUNT(*) AS rows, MIN(report_date) AS min_date, "
        f"MAX(report_date) AS max_date FROM {FACT}"
    ).df()
    assert int(source.loc[0, "rows"]) > 0
    assert str(source.loc[0, "min_date"])[:10] <= "2025-01-27"
    assert str(source.loc[0, "max_date"])[:10] >= "2026-06-30"

    duplicate_daily_grains = connection.sql(
        f"""
        SELECT COUNT(*) AS duplicate_grains
        FROM (
            SELECT report_date, client_hash_id, content_hash_id
            FROM {FACT}
            WHERE report_date BETWEEN DATE '{FEATURE_START}' AND DATE '{FEATURE_END}'
            GROUP BY 1, 2, 3
            HAVING COUNT(*) > 1
        )
        """
    ).df()
    assert int(duplicate_daily_grains.loc[0, "duplicate_grains"]) == 0

    connection.sql(
        f"""
        CREATE OR REPLACE TEMP VIEW feature_base AS
        SELECT
            client_hash_id,
            content_hash_id,
            SUM(CASE WHEN gsc_data_available IS TRUE
                THEN COALESCE(gsc_impressions, 0) ELSE 0 END) AS impressions_90d,
            SUM(CASE WHEN gsc_data_available IS TRUE
                THEN COALESCE(gsc_clicks, 0) ELSE 0 END) AS clicks_90d,
            SUM(CASE WHEN ga4_data_available IS TRUE
                THEN COALESCE(ga4_sessions, 0) ELSE 0 END) AS sessions_90d,
            SUM(CASE WHEN ga4_data_available IS TRUE
                THEN COALESCE(ga4_engaged_sessions, 0) ELSE 0 END)
                AS engaged_sessions_90d,
            SUM(CASE WHEN gsc_data_available IS TRUE
                AND COALESCE(gsc_impressions, 0) > 0
                THEN COALESCE(gsc_sum_position, 0) ELSE 0 END)
                AS position_weighted_sum,
            SUM(CASE WHEN gsc_data_available IS TRUE
                AND COALESCE(gsc_impressions, 0) > 0
                THEN gsc_impressions ELSE 0 END) AS positioned_impressions,
            MAX(CASE WHEN ga4_data_available IS TRUE THEN 1 ELSE 0 END)
                AS ga4_available_90d
        FROM {FACT}
        WHERE report_date BETWEEN DATE '{FEATURE_START}' AND DATE '{FEATURE_END}'
        GROUP BY 1, 2
        """
    )
    connection.sql(
        f"""
        CREATE OR REPLACE TEMP VIEW tier_rates AS
        SELECT
            CASE
                WHEN impressions_90d < {MIN_IMPRESSIONS}
                    OR positioned_impressions <= 0 THEN 'no_position_or_volume'
                WHEN position_weighted_sum / impressions_90d <= 3 THEN 'top_3'
                WHEN position_weighted_sum / impressions_90d <= 10 THEN 'page_1'
                WHEN position_weighted_sum / impressions_90d <= 20 THEN 'striking'
                WHEN position_weighted_sum / impressions_90d <= 50 THEN 'page_3_5'
                ELSE 'deep'
            END AS position_tier,
            SUM(clicks_90d) / NULLIF(SUM(impressions_90d), 0) * 100
                AS expected_ctr_feature
        FROM feature_base
        WHERE impressions_90d >= {MIN_IMPRESSIONS}
        GROUP BY 1
        """
    )
    features = connection.sql(
        f"""
        SELECT
            b.*,
            b.clicks_90d / NULLIF(b.impressions_90d, 0) * 100 AS ctr_feature,
            b.position_weighted_sum / NULLIF(b.positioned_impressions, 0)
                AS avg_position_feature,
            b.engaged_sessions_90d / NULLIF(b.sessions_90d, 0) * 100
                AS engagement_rate_feature,
            CASE
                WHEN b.impressions_90d < {MIN_IMPRESSIONS}
                    OR b.positioned_impressions <= 0 THEN 'no_position_or_volume'
                WHEN b.position_weighted_sum / b.impressions_90d <= 3 THEN 'top_3'
                WHEN b.position_weighted_sum / b.impressions_90d <= 10 THEN 'page_1'
                WHEN b.position_weighted_sum / b.impressions_90d <= 20 THEN 'striking'
                WHEN b.position_weighted_sum / b.impressions_90d <= 50 THEN 'page_3_5'
                ELSE 'deep'
            END AS position_tier,
            t.expected_ctr_feature
        FROM feature_base b
        LEFT JOIN tier_rates t
          ON t.position_tier = CASE
                WHEN b.impressions_90d < {MIN_IMPRESSIONS}
                    OR b.positioned_impressions <= 0 THEN 'no_position_or_volume'
                WHEN b.position_weighted_sum / b.impressions_90d <= 3 THEN 'top_3'
                WHEN b.position_weighted_sum / b.impressions_90d <= 10 THEN 'page_1'
                WHEN b.position_weighted_sum / b.impressions_90d <= 20 THEN 'striking'
                WHEN b.position_weighted_sum / b.impressions_90d <= 50 THEN 'page_3_5'
                ELSE 'deep'
            END
        """
    ).df()
    labels = connection.sql(
        f"""
        SELECT
            client_hash_id,
            content_hash_id,
            SUM(CASE WHEN gsc_data_available IS TRUE
                THEN COALESCE(gsc_impressions, 0) ELSE 0 END)
                AS impressions_next30d,
            SUM(CASE WHEN gsc_data_available IS TRUE
                THEN COALESCE(gsc_clicks, 0) ELSE 0 END) AS clicks_next30d
        FROM {FACT}
        WHERE report_date BETWEEN DATE '{LABEL_START}' AND DATE '{LABEL_END}'
        GROUP BY 1, 2
        """
    ).df()
    labels["ctr_next30d"] = (
        labels["clicks_next30d"]
        / labels["impressions_next30d"].replace(0, np.nan)
        * 100
    )
    data = features.merge(labels, on=["client_hash_id", "content_hash_id"], how="left")
    data["feature_eligible"] = data["impressions_90d"] >= MIN_IMPRESSIONS
    data["label_eligible"] = data["impressions_next30d"] >= MIN_IMPRESSIONS
    data["known_tier"] = data["position_tier"].ne("no_position_or_volume")
    data["baseline_score"] = np.where(
        data["feature_eligible"]
        & data["known_tier"]
        & (data["ctr_feature"] < LOW_CTR_THRESHOLD),
        data["impressions_90d"],
        0.0,
    )
    data["target"] = (
        data["feature_eligible"]
        & data["label_eligible"]
        & data["known_tier"]
        & (data["ctr_next30d"] < data["expected_ctr_feature"] * 0.5)
    ).astype(int)
    eligible = data[
        data["feature_eligible"] & data["label_eligible"] & data["known_tier"]
    ].copy()
    assert len(eligible) > 0 and eligible["target"].nunique() == 2
    assert not eligible[["client_hash_id", "content_hash_id"]].duplicated().any()
    assert FEATURE_END < LABEL_START
    return data, eligible


def precision_at_k(y_true: np.ndarray, scores: np.ndarray, k: int) -> float:
    order = np.argsort(-np.asarray(scores), kind="mergesort")[:k]
    return float(np.asarray(y_true)[order].mean()) if len(order) else 0.0


def ranking_metrics(y_true: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    scores = np.clip(np.asarray(scores, dtype=float), 0, 1)
    y_true = np.asarray(y_true, dtype=int)
    order = np.argsort(-scores, kind="mergesort")
    top_50 = order[: min(50, len(order))]
    metrics = {
        "precision_at_10": precision_at_k(y_true, scores, 10),
        "precision_at_20": precision_at_k(y_true, scores, 20),
        "precision_at_50": precision_at_k(y_true, scores, 50),
        "precision_at_100": precision_at_k(y_true, scores, 100),
        "correct_at_50": float(y_true[top_50].sum()),
        "coverage_at_50": float(len(top_50) / len(y_true)) if len(y_true) else 0.0,
    }
    if np.unique(y_true).size == 2:
        metrics["average_precision"] = float(average_precision_score(y_true, scores))
        metrics["roc_auc"] = float(roc_auc_score(y_true, scores))
    else:
        metrics["average_precision"] = 0.0
        metrics["roc_auc"] = 0.0
    return metrics


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
