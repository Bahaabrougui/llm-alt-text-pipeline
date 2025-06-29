# app/db/init_db.py
import os
import psycopg2
from datetime import datetime

def insert_images(folder="../data/imgs/"):
    conn = psycopg2.connect(
        dbname="image_metadata",
        user="user",
        password="password",
        host="localhost",
        port=5432
    )
    cur = conn.cursor()

    for file in os.listdir(folder):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder, file)
            product_id = os.path.splitext(file)[0]  # dummy
            cur.execute("""
                INSERT INTO product_images (product_id, image_path, status, last_updated)
                VALUES (%s, %s, %s, %s)
            """, (product_id, image_path, 'pending', datetime.now()))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Inserted images into database.")


if __name__ == "__main__":
    insert_images()
