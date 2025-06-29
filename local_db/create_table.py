import psycopg2

conn = psycopg2.connect(
    dbname="image_metadata",
    user="dbadmin",
    password="password123.",
    host="my-postgres-server-9e7eb9.postgres.database.azure.com",
    port=5432,
    sslmode="require"
)
cur = conn.cursor()
with open("./init.sql", "r") as sql_file:
    sql_code = sql_file.read()
cur.execute(f"""
    {sql_code}
""")
conn.commit()
cur.close()
conn.close()
