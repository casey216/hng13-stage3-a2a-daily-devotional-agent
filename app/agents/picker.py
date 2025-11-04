# app/agents/picker.py
from sqlalchemy import text
from app.database import BIBLE_ENGINE
from sqlalchemy.orm import Session

def pick_random_verse(topic: str | None = None):
    """
    Pick a random verse from the local bible DB.
    If topic provided, try to find a verse that contains the topic word(s).
    Expects a `verses` table with columns (id, book, chapter, verse, text).
    Returns (reference, text).
    """
    with Session(BIBLE_ENGINE) as session:
        if topic:
            # simple LIKE search; you can improve this with FTS or tags
            sql = text("""
                SELECT b.name AS book, v.chapter, v.verse, v.text
                FROM KJV_verses v
                JOIN KJV_books b ON v.book_id = b.id
                WHERE lower(v.text) LIKE :pat
                ORDER BY RANDOM()
                LIMIT 1
            """)
            row = session.execute(sql, {"pat": f"%{topic.lower()}%"}).first()
            if row:
                book, chapter, verse, text_val = row
                return f"{book} {chapter}:{verse}", text_val.strip()
        # fallback: pick any random verse
        sql = text("""
            SELECT b.name AS book, v.chapter, v.verse, v.text
            FROM KJV_verses v
            JOIN KJV_books b ON v.book_id = b.id
            ORDER BY RANDOM()
            LIMIT 1
        """)
        row = session.execute(sql).first()
        if not row:
            raise RuntimeError("No verses found in bible DB. Check that BIBLE_DB path and schema are correct.")
        book, chapter, verse, text_val = row
        return f"{book} {chapter}:{verse}", text_val.strip()
