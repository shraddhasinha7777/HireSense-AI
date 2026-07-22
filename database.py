import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="ats_database.db"):
        os.makedirs("database", exist_ok=True)
        self.db_name = os.path.join("database", db_name)
        self.initialize_database()

    def _get_connection(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def initialize_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # ⭐ UPGRADE: 4 New Columns added for Permanent AI Storage!
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    name TEXT,
                    role TEXT,
                    experience TEXT,
                    education TEXT,
                    location TEXT,
                    ats_score REAL,
                    jd_match REAL,
                    status TEXT,
                    matched_skills TEXT,
                    ai_summary TEXT,
                    swot TEXT,
                    interview_questions TEXT,
                    ai_recommendation TEXT,
                    created_at TEXT
                )
            """)
            conn.commit()

    def insert_candidate(self, data):
        # Type safety for skills
        raw_skills = data.get("matched_skills", [])
        if isinstance(raw_skills, str):
            skills_str = raw_skills
        elif isinstance(raw_skills, (list, set, tuple)):
            skills_str = ",".join([str(s).strip() for s in raw_skills if s])
        else:
            skills_str = ""

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # ⭐ PROFESSIONAL DUPLICATE CHECK
            email_val = data.get("email", "unknown@ats.com")
            cursor.execute("SELECT 1 FROM candidates WHERE email=?", (email_val,))
            if cursor.fetchone():
                return False

            cursor.execute("""
                INSERT INTO candidates
                (email, name, role, experience, education, location, ats_score,
                 jd_match, status, matched_skills, ai_summary, swot,
                 interview_questions, ai_recommendation, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                email_val,
                data.get("name", "Unknown"),
                data.get("role", "Unknown"),
                data.get("experience", "Fresher"),
                data.get("education", "Unknown"),
                data.get("location", "India"),
                data.get("ats_score", 0.0),
                data.get("jd_match", 0.0),
                data.get("status", "Review"),
                skills_str,
                data.get("ai_summary", ""),
                data.get("swot", "{}"),
                data.get("interview_questions", "[]"),
                data.get("ai_recommendation", ""),
                created_at
            ))

            conn.commit()
            return True

    def get_all_candidates(self):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *
                FROM candidates
                ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # ⭐ NEW FUNCTION - Returns candidate with highest ATS score
    def get_best_candidate(self):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT *
                FROM candidates
                ORDER BY ats_score DESC
                LIMIT 1
            """)

            row = cursor.fetchone()

            if row:
                return dict(row)

            return None

    def clear_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM candidates")
            conn.commit()