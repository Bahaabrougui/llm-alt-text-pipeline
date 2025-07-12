import os
import threading
import logging
from psycopg2.pool import SimpleConnectionPool
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


logger = logging.getLogger("db_pool")
logger.setLevel(logging.INFO)


class DBPool:
    _pool = None
    _lock = threading.Lock()

    @classmethod
    def _get_secret(cls, secret_name: str) -> str:
        logger.info(f"Fetching secret '{secret_name}' from Key Vault...")
        vault_url = os.environ["KEY_VAULT_URL"]
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)  # type: ignore
        secret = client.get_secret(secret_name).value
        logger.info(f"Successfully retrieved secret '{secret_name}'")
        return secret

    @classmethod
    def _initialize_pool(cls):
        if cls._pool is None:
            with cls._lock:
                if cls._pool is None:
                    logger.info("Initializing PostgreSQL connection pool...")
                    cls._pool = SimpleConnectionPool(
                        minconn=1,
                        maxconn=10,
                        dbname=os.getenv("DB_NAME", "image_metadata"),
                        user=os.getenv("DB_USER", "dbadmin"),
                        password=cls._get_secret("db-password"),
                        host=os.getenv("DB_HOST"),
                        port=5432,
                        sslmode="require",
                    )
                    logger.info("PostgreSQL connection pool initialized.")

    @classmethod
    def get_conn(cls):
        cls._initialize_pool()
        try:
            conn = cls._pool.getconn()
            logger.debug("Connection checked out from pool.")
            return conn
        except Exception as e:
            logger.exception("Failed to get connection from pool")
            raise

    @classmethod
    def put_conn(cls, conn):
        try:
            if cls._pool:
                cls._pool.putconn(conn)
                logger.debug("Connection returned to pool.")
        except Exception as e:
            logger.warning(f"Failed to return connection to pool: {e}")
