import json
import logging
import os
import time
from datetime import datetime
from typing import Optional, Any, Dict

import psycopg2

logger = logging.getLogger("llmops")
logger.setLevel(logging.INFO)


def log_metrics(
        component: str,
        *,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        latency: Optional[float] = None,
        cost_usd: Optional[float] = None,
        safety_score: Optional[float] = None,
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
        "safety_score": safety_score,
    }
    metrics.update(extra)
    metrics = {k: v for k, v in metrics.items() if v is not None}
    logger.info(f"[METRICS] {json.dumps(metrics)}")


def save_to_db(filename: str, result: dict):
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
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (
        os.path.splitext(os.path.basename(filename))[0],
        filename,
        result["captions"].get("en"),
        result["captions"].get("fr"),
        result["captions"].get("de"),
        result["safety"].get("en"),
        result["safety"].get("fr"),
        result["safety"].get("de"),
        "complete",
        datetime.utcnow()
    ))
    conn.commit()
    cur.close()
    conn.close()
