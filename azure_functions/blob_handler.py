import logging
import os
import azure.functions as func
from app.pipeline import AltTextPipeline
import psycopg2
from datetime import datetime


pipeline = None
app = func.FunctionApp()


def get_pipeline():
    global pipeline
    if pipeline is None:
        logging.info("✅ Initializing pipeline and loading models")
        pipeline = AltTextPipeline()
    return pipeline


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


@app.blob_trigger(
    arg_name="myblob",
    path="data/images/{image}",
    connection="BlobStorageConnectionString",
)
def main(myblob: func.InputStream):
    logging.info(f"Processing blob: {myblob.name} ({myblob.length} bytes)")
    local_path = f"/tmp/{os.path.basename(myblob.name)}"
    with open(local_path, "wb") as fp:
        fp.write(myblob.read())

    pipe = get_pipeline()
    result = pipe.process_image(local_path)
    logging.info(f"Result: {result['captions']} | Safety: {result['safety']}")

    save_to_db(myblob.name, result)
