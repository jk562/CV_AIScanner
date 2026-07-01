import sqlite3
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resume_screener.db")

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            filename TEXT NOT NULL,
            extracted_text TEXT,
            match_score REAL,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)

    conn.commit()
    conn.close()

def add_job(title, description, user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO jobs (title, description, created_by) VALUES (?, ?, ?)",
                (title, description, user_id))
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return job_id

def add_candidate(job_id, filename, extracted_text, score):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO candidates (job_id, filename, extracted_text, match_score)
                   VALUES (?, ?, ?, ?)""", (job_id, filename, extracted_text, score))
    conn.commit()
    conn.close()

def get_ranked_candidates(job_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT filename, match_score, extracted_text FROM candidates
                   WHERE job_id = ? ORDER BY match_score DESC""", (job_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_jobs_for_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM jobs WHERE created_by = ? ORDER BY id DESC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_job(job_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description FROM jobs WHERE id = ?", (job_id,))
    row = cur.fetchone()
    conn.close()
    return row