import sqlite3
import os

DB_PATH = "colegal.db"

AGENT_ORDER = [
    "ingestor",
    "llm_prevalidator",
    "validator",
    "formatter"
]

#   CONEXIÓN SEGURA A SQLITE (PRODUCCIÓN)
def get_connection():

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    # Optimización y seguridad
    conn.execute("PRAGMA journal_mode=WAL;")       # Mejor rendimiento
    conn.execute("PRAGMA synchronous=NORMAL;")     # Más rápido, seguro
    conn.execute("PRAGMA foreign_keys=ON;")        # Integridad referencial

    conn.row_factory = sqlite3.Row
    return conn


#   CARGAR UNA SESIÓN COMPLETA
def load_session_from_db(session_uuid: str):
    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM sessions WHERE uuid = ?",
        (session_uuid,)
    ).fetchone()

    if not row:
        conn.close()
        return None

    session_data = dict(row)

    logs = conn.execute(
        "SELECT agent_name, event_type FROM agent_logs WHERE session_uuid = ?",
        (session_uuid,)
    ).fetchall()

    conn.close()

    logs = [dict(r) for r in logs]

    agent_status = {}

    for agent in AGENT_ORDER:
        agent_logs = [l for l in logs if l["agent_name"] == agent]

        if not agent_logs:
            agent_status[agent] = "pending"
        else:
            last = agent_logs[-1]["event_type"]
            if last == "success":
                agent_status[agent] = "done"
            elif last == "error":
                agent_status[agent] = "error"
            else:
                agent_status[agent] = "running"

    session_data["agent_status"] = agent_status

    # Estado general
    errors = [a for a, st in agent_status.items() if st == "error"]

    if errors:
        session_data["current_agent"] = errors[0]
        session_data["status"] = "error"

    elif all(st == "done" for st in agent_status.values()):
        session_data["current_agent"] = None
        session_data["status"] = "success"

    else:
        pending = [a for a, st in agent_status.items() if st == "pending"]
        session_data["current_agent"] = pending[0] if pending else None
        session_data["status"] = "running"

    return session_data



#   CARGAR TODOS LOS LOGS DE UNA SESIÓN
def load_logs_from_db(session_uuid: str):
    conn = get_connection()

    rows = conn.execute(
        "SELECT * FROM agent_logs WHERE session_uuid = ? ORDER BY created_at ASC",
        (session_uuid,)
    ).fetchall()

    conn.close()
    return [dict(r) for r in rows]
