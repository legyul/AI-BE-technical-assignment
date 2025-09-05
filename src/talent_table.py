import os
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import Json
import hashlib
import numpy as np
from logger_utils import logger

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": os.getenv("POSTGRES_USER", "searchright"),
    "password": os.getenv("POSTGRES_PASSWORD", "searchright"),
    "database": os.getenv("POSTGRES_DB", "searchright"),
}

def connect_to_db():
    """데이터베이스에 연결"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info(f"[INFO] 성공적으로 {DB_CONFIG['database']} 데이터베이스에 연결했습니다.")
        return conn
    except psycopg2.Error as e:
        print(f'ERROR: {e}')
        logger.error(f"[ERROR] 데이터베이스 연결 오류: {e}")
        raise

def create_talent_table(conn):
    """Talent 테이블 생성 (존재하지 않을 경우)"""
    try:
        with conn.cursor() as cursor:
            # 테이블이 존재하는지 확인
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'talent'
                );
            """
            )
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                logger.info(
                    "[INFO] company 테이블이 존재하지 않습니다. 새로운 테이블을 생성합니다."
                )
                cursor.execute(
                    """
                    CREATE TABLE talent (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        profile TEXT,
                        tags JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """
                )
                logger.info("[INFO] company 테이블이 성공적으로 생성되었습니다.")
            else:
                logger.info(
                    "[INFO] company 테이블이 이미 존재합니다. 테이블 생성을 건너뜁니다."
                )
    except psycopg2.Error as e:
        logger.error(f"[ERROR] 테이블 생성 오류: {e}")
        raise


def insert_talent_data(conn, name: str, summary: str, tags: list[dict], embeddings: list[float]):
    """Insert the talent data to the talent table"""
    try:
        with conn.cursor() as cursor:
            # 이미 존재하는지 확인
            cursor.execute("SELECT COUNT(*) FROM talent WHERE name = %s", (name,))
            count = cursor.fetchone()[0]

            if count > 0:
                logger.info(
                    f"[INFO] 회사 '{name}'의 데이터가 이미 존재합니다. 삽입을 건너뜁니다."
                )
                return False

            # Insert data
            cursor.execute(
                "INSERT INTO talent (name, profile, tags, embedding) VALUES (%s, %s, %s, %s)",
                (name, summary, tags, embeddings),
            )
            conn.commit()
            logger.info(f"[INFO] 회사 '{name}'의 데이터가 성공적으로 삽입되었습니다.")
            return True
    except psycopg2.Error as e:
        logger.error(f"[ERROR] 데이터 삽입 오류: {e}")
        conn.rollback()
        return False

def generate_anon_name(real_name: str) -> str:
    """Anonymous name processing using hash"""
    hashed = hashlib.sha256(real_name.encode()).hexdigest()
    return f"talent-{hashed[:10]}"

def table_main(name: str, profile: str, tags: list[dict], embeddings: list[float]):
    conn = connect_to_db()
    create_talent_table(conn)

    hashed_name = generate_anon_name(name)
    inserted = insert_talent_data(conn, hashed_name, profile, embeddings)

    if inserted:
        print(f"{name} save completed")
    else:
        print(f"{name} already exists")

def find_similar_talent(conn, new_embedding: np.ndarray, threshold: float = 0.85):
    """
    Find the most similar talent with a new talent based on pgvector

    Parameters
        - new_embedding (numpy ndarray): The embedding vector of the new talent
        - threshold (float): The similarity threshold (default = 0.85) (If it is lower than this, return None)

    Return
        - similarity_result ((talent_id, similarity)): The most similarity id and its score, or None
    """

    with conn.cursor() as cursor:
        # Use cosine distance to get similarity
        cursor.execute("""
        SELECT id, 1 - (embedding <-> %s::vector) AS similarity
        FROM talent
        ORDER BY embedding <-> %s::vector ASC
        LIMIT 1;
        """, (new_embedding, new_embedding))

        result = cursor.fetchone()

        if result:
            talent_id, similarity = result
            if similarity >= threshold:
                similarity_result = (talent_id, similarity)
                
                return similarity_result
        
        return None