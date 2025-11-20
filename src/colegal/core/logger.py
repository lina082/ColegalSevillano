import json
from datetime import datetime
from src.colegal.core.database import get_connection


# ===========================================
#   PREVENCIÓN: Limitar textos muy grandes
# ===========================================
def safe_text(value, max_len=2000):
    """
    Previene que textos muy grandes dañen SQLite.
    No afecta al contrato porque solo se usa en logs.
    """
    if value is None:
        return None
    value = str(value)
    return value[:max_len]


# ===========================================
#   LOG DE EVENTOS DEL SISTEMA
# ===========================================
def log_event(session_uuid, agent_name, event_type,
              prompt=None, response=None, tokens_in=0, tokens_out=0):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO agent_logs (
            session_uuid, agent_name, event_type,
            prompt, response, tokens_input, tokens_output, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_uuid,
        safe_text(agent_name),
        safe_text(event_type),
        safe_text(prompt),
        safe_text(response),
        tokens_in,
        tokens_out,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


# ===========================================
#   LOG DE ERRORES DEL SISTEMA
# ===========================================
def log_error(session_uuid, agent_name, message, stacktrace=""):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO errors (
            session_uuid, agent_name, error_message, stacktrace, created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        session_uuid,
        safe_text(agent_name),
        safe_text(message),
        safe_text(stacktrace),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


# ===========================================
#   CREAR NUEVA SESIÓN DE GENERACIÓN
# ===========================================
def create_session(input_data):
    from uuid import uuid4
    session_id = str(uuid4())

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sessions (uuid, status, input_json, created_at)
        VALUES (?, 'iniciado', ?, ?)
    """, (
        session_id,
        safe_text(json.dumps(input_data)),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    return session_id


# ===========================================
#   ACTUALIZAR SESIÓN (ÉXITO O ERROR)
# ===========================================
def update_session(session_uuid, status, final_output=None):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET status = ?, final_output = ?, updated_at = ?
        WHERE uuid = ?
    """, (
        safe_text(status),
        safe_text(final_output),
        datetime.utcnow().isoformat(),
        session_uuid
    ))

    conn.commit()
    conn.close()

