import os
from datetime import datetime

import psycopg2


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
