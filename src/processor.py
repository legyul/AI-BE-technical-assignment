from .preprocess import parsing
from .summarize import talent_summary, summary
from .gpt import build_prompt, gen_tags, parse_gpt_tags, profile_embedding
from .talent_table import table_main, find_similar_talent
import os
import psycopg2
from logger_utils import logger


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": os.getenv("POSTGRES_USER", "searchright"),
    "password": os.getenv("POSTGRES_PASSWORD", "searchright"),
    "database": os.getenv("POSTGRES_DB", "searchright"),
}

conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
        )

def process_talent(talent_path: str, threshold: float = 0.85):
    """
    Main logic of the total process
    threshold (float): The similarity threshold (default = 0.85) (If it is lower than this, return None)
    """

    cursor = conn.cursor()

    # Load and summarize talent
    data = parsing.preprocessing_personal_info(talent_path)
    talent_name = data.get('name','')
    profile = talent_summary.profile_summary(data)

    # Summarize full content + get embedding
    summ = summary(conn, data, profile)
    embedding = profile_embedding(summ)

    # Check if similar talent exists
    similarity_result = find_similar_talent(conn, embedding, threshold)

    if similarity_result is None:
        # No similar talent, then use GPT tag
        logger.info("[INFO] There is no similar talent. Use GPT model to get tags")

        prompt = build_prompt(summ)
        response = gen_tags(prompt)     # Get tag from the GPT model

        converted_tag = parse_gpt_tags(response)

        # Insert talent informations and tags to the talent table
        table_main(talent_name, summ, converted_tag, embedding)
        logger.info("[INFO] Completed insert 'talent' table")

        cursor.close()
        conn.close()

        return converted_tag
    else:
        # Similar talent exists, then use similar talent's tags
        logger.info("[INFO] Similar talent exists. Use its tags.")

        similar_talent_id = similarity_result[0]

        cursor.execute("SELECT id, tags FROM talent WHERE id = %s;", (similar_talent_id,))
        row = cursor.fetchone()

        if row:
            tags_list = row[1]
            tag = [tag_dict['tag'] for tag_dict in tags_list]

            # Insert talent informations and tags to the talent table
            table_main(talent_name, summ, tag, embedding)
            logger.info("[INFO] Completed insert 'talent' table")

            cursor.close()
            conn.close()

            return tag
