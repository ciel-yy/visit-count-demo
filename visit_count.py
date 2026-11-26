import sqlite3
from fastapi import FastAPI, Request

app = FastAPI()
DB_PATH = "visit_count.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visit_counter (
            id INTEGER PRIMARY KEY,
            visit_num INTEGER NOT NULL DEFAULT 0
        )
    """)
    cur.execute("SELECT id FROM visit_counter WHERE id = 1")
    if cur.fetchone() is None:
        cur.execute("INSERT INTO visit_counter(id, visit_num) VALUES (1, 0)")
    conn.commit()
    conn.close()


init_db()

SKIP_PATHS = {"/docs", "/openapi.json", "/redoc"}


@app.middleware("http")
async def count_middleware(request: Request, call_next):
    path = request.url.path
    count = None

    if path not in SKIP_PATHS:
        conn = sqlite3.connect(DB_PATH, timeout=2)
        cur = conn.cursor()
        cur.execute(
            "UPDATE visit_counter SET visit_num = visit_num + 1 WHERE id = 1 RETURNING visit_num"
        )
        count = cur.fetchone()[0]
        conn.commit()
        conn.close()

    resp = await call_next(request)
    if count is not None:
        resp.headers["X-Visit-Count"] = str(count)
    return resp


@app.get("/")
def index():
    return {"message": "service running"}



