from app.pipeline import AltTextPipeline
import psycopg2
from datetime import datetime


def process_batch(n=10):
    pipeline = AltTextPipeline()

    conn = psycopg2.connect(
        dbname="image_metadata",
        user="dbadmin",
        password="password123.",
        host="my-postgres-server.postgres.database.azure.com",
        port=5432,
        sslmode="require"
    )
    cur = conn.cursor()

    cur.execute("""
        SELECT id, image_path FROM product_images
        WHERE status = 'pending'
        LIMIT %s
    """, (n,))

    rows = cur.fetchall()

    for row in rows:
        img_id, img_path = row
        print(f"📷 Processing {img_path}")
        try:
            result = pipeline.process_image(img_path)
            cur.execute("""
                UPDATE product_images
                SET alt_en = %s,
                    alt_fr = %s,
                    alt_de = %s,
                    safety_en = %s
                    safety_fr = %s
                    safety_de = %s
                    status = 'complete',
                    last_updated = %s
                WHERE id = %s
            """, (
                result["captions"].get("en"),
                result["captions"].get("fr"),
                result["captions"].get("de"),
                result["safety"].get("en"),
                result["safety"].get("fr"),
                result["safety"].get("de"),
                datetime.now(),
                img_id
            ))
            conn.commit()
        except Exception as e:
            print(f"❌ Error processing {img_path}: {e}")
            cur.execute(
                "UPDATE product_images SET status = 'failed' WHERE id = %s",
                (img_id,))
            conn.commit()

    cur.close()
    conn.close()
    print("✅ Done processing.")


# function/altTextPipelineTrigger/__init__.py

import logging
import os
import azure.functions as func
from app.pipeline import AltTextPipeline
import psycopg2
from datetime import datetime


pipeline = None


def get_pipeline():
    global pipeline
    if pipeline is None:
        logging.info("✅ Initializing pipeline and loading models")
        pipeline = AltTextPipeline()
    return pipeline


def save_to_db(filename: str, result: dict):
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
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


def main(myblob: func.InputStream):
    logging.info(f"Processing blob: {myblob.name} ({myblob.length} bytes)")
    local_path = f"/tmp/{os.path.basename(myblob.name)}"
    with open(local_path, "wb") as fp:
        fp.write(myblob.read())

    pipe = get_pipeline()
    result = pipe.process_image(local_path)
    logging.info(f"Result: {result['captions']} | Safety: {result['safety']}")

    save_to_db(myblob.name, result)

    return func.HttpResponse(f"Processed: {myblob.name}", status_code=200)