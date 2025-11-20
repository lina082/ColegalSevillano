import sqlite3

DB_PATH = "colegal.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # =============================
    #  OPCIONES DE CALIDAD
    # =============================
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")

    # =============================
    #   TABLA sessions
    # =============================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            uuid TEXT PRIMARY KEY,
            status TEXT,
            input_json TEXT,
            final_output TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)

    # =============================
    #   TABLA agent_logs
    # =============================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_uuid TEXT NOT NULL,
            agent_name TEXT,
            event_type TEXT,
            prompt TEXT,
            response TEXT,
            tokens_input INTEGER,
            tokens_output INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(session_uuid) REFERENCES sessions(uuid)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    """)

    # =============================
    #   TABLA errors
    # =============================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_uuid TEXT NOT NULL,
            agent_name TEXT,
            error_message TEXT,
            stacktrace TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(session_uuid) REFERENCES sessions(uuid)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    """)


    #   ÍNDICES (PERFORMANCE)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_session ON agent_logs(session_uuid);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_errors_session ON errors(session_uuid);")

    conn.commit()
    conn.close()

    print("✔ Base de datos inicializada CORRECTAMENTE (versión PRO).")


if __name__ == "__main__":
    init_db()
