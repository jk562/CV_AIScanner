import os
import pymysql
import pymysql.cursors

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DB = os.environ.get("MYSQL_DB", "resume_screener")


def get_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_by INT,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id INT,
            filename TEXT NOT NULL,
            extracted_text LONGTEXT,
            match_score FLOAT,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)

    conn.commit()
    conn.close()


def add_job(title, description, user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO jobs (title, description, created_by) VALUES (%s, %s, %s)",
                (title, description, user_id))
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return job_id


def add_candidate(job_id, filename, extracted_text, score):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO candidates (job_id, filename, extracted_text, match_score)
                   VALUES (%s, %s, %s, %s)""", (job_id, filename, extracted_text, score))
    conn.commit()
    conn.close()


def get_ranked_candidates(job_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT filename, match_score, extracted_text FROM candidates
                   WHERE job_id = %s ORDER BY match_score DESC""", (job_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_jobs_for_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM jobs WHERE created_by = %s ORDER BY id DESC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_job(job_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description FROM jobs WHERE id = %s", (job_id,))
    row = cur.fetchone()
    conn.close()
    return row
