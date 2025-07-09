import json
import logging
import os
import time
from datetime import datetime
from typing import Optional, Any, Dict

import numpy as np
import psycopg2

# Metrics logger
llmops_logger = logging.getLogger("llmops")
llmops_logger.setLevel(logging.INFO)
# Info messages logger
info_logger = logging.getLogger("Info")
info_logger.setLevel(logging.INFO)


def safe_json(obj):
    if isinstance(obj, dict):
        return {k: safe_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_json(v) for v in obj]
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    elif obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    # fallback for other types
    else:
        return str(obj)


def log_info_message(message: str):
    info_logger.info(message)


def log_metrics(
        component: str,
        *,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        latency: Optional[float] = None,
        cost_usd: Optional[float] = None,
        **extra: Any,
):
    if latency is None:
        # compute elapsed based on a passed _start_ key, if provided
        latency = extra.pop("_start_", None)
        if latency:
            latency = round(time.time() - latency, 3)

    metrics: Dict[str, Any] = {
        "component": component,
        "latency_s": latency,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost_usd, 6) if cost_usd is not None else None,
    }
    metrics.update(extra)
    metrics = {k: v for k, v in metrics.items() if v is not None}
    llmops_logger.info(f"[METRICS] {json.dumps(metrics, default=safe_json)}")


def save_to_db(filename: str, result: dict):
    if all(
            result["safety"].get(lang).get("is_safe")
            for lang in ["en", "fr", "de"]
    ):
        conn = psycopg2.connect(
            dbname="image_metadata",
            user="dbadmin",
            password="password123.",
            host="my-postgres-server-9e7eb9.postgres.database.azure.com",
            port=5432,
            sslmode="require"
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO product_images (
            product_id,
            image_path,
            alt_en,
            alt_fr,
            alt_de,
            safety_en,
            safety_fr,
            safety_de,
            status,
            last_updated
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            os.path.splitext(os.path.basename(filename))[0],
            filename,
            result["captions"].get("en"),
            result["captions"].get("fr"),
            result["captions"].get("de"),
            json.dumps(result["safety"].get("en")),
            json.dumps(result["safety"].get("fr")),
            json.dumps(result["safety"].get("de")),
            "complete",
            datetime.utcnow()
        ))
        conn.commit()
        cur.close()
        conn.close()
