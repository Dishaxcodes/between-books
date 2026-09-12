import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'library.db')


def get_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create the books table if it doesn't already exist. Call this once at app startup."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE,
            title TEXT NOT NULL,
            author TEXT,
            description TEXT,
            cover TEXT,
            link TEXT,
            emotion TEXT,
            search_count INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def find_book_by_title(title):
    """
    Search the local library for a book by title (case-insensitive, partial match).
    Returns the most-searched matching book as a dict, or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books
        WHERE LOWER(title) LIKE LOWER(?)
        ORDER BY search_count DESC
        LIMIT 1
    ''', (f'%{title}%',))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_book(book_info, google_id, emotion=None):
    """
    Save a newly-fetched book into the local library.
    If it already exists (matched by google_id), bump its search_count instead.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id, search_count FROM books WHERE google_id = ?', (google_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            'UPDATE books SET search_count = ? WHERE google_id = ?',
            (existing['search_count'] + 1, google_id)
        )
    else:
        cursor.execute('''
            INSERT INTO books (google_id, title, author, description, cover, link, emotion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            google_id,
            book_info.get('title'),
            book_info.get('author'),
            book_info.get('description'),
            book_info.get('cover'),
            book_info.get('link'),
            emotion
        ))

    conn.commit()
    conn.close()


def get_all_books():
    """Return every book in the local library, most recently added first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books ORDER BY added_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]