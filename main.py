from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os, uuid, json

# Seguridad Nivel 2
import jwt
import bcrypt
from datetime import datetime, timedelta

# Agentes
from src.colegal.agents.agent_base import AgentContext
from src.colegal.agents.coordinator import CoordinatorAgent

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
HASHED_PASSWORD = os.getenv("HASHED_PASSWORD")

if not JWT_SECRET or not HASHED_PASSWORD:
    raise ValueError("⚠️ ERROR: No se encontraron JWT_SECRET o HASHED_PASSWORD en el .env")

HASHED_PASSWORD = HASHED_PASSWORD.encode()
JWT_ALGO = "HS256"

FAILED_LOGINS = {}
MAX_LOGIN_ATTEMPTS = 5
BLOCK_TIME_MINUTES = 10

# ============================================================
#   CONFIGURACIÓN INICIAL
# ============================================================
app = FastAPI(title="COLEGAL SEVILLANO")

app.mount("/static", StaticFiles(directory="src/colegal/static"), name="static")
templates = Jinja2Templates(directory="src/colegal/templates")


# ============================================================
# 🚑 HEALTH CHECK (Evita el error 502 en Render)
# ============================================================
@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "COLEGAL Sevilano", "code": 200}


# ============================================================
#   VALIDAR TOKEN
# ============================================================
def validar_token(request: Request):
    token = request.cookies.get("session")
    if not token:
        return False
    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return True
    except:
        return False


# ============================================================
#   MIDDLEWARE DE AUTENTICACIÓN
# ============================================================
@app.middleware("http")
async def auth_middleware(request: Request, call_next):

    path = request.url.path

    # Agregar "/" como endpoint público
    PUBLIC_ENDPOINTS = ("/", "/login", "/static", "/generate")

    # Permitir descargas de archivos
    if path.startswith("/download/"):
        return await call_next(request)

    # Permitir rutas públicas
    if any(path.startswith(p) for p in PUBLIC_ENDPOINTS):
        return await call_next(request)

    # Verificar sesión
    token = request.cookies.get("session")
    if not token:
        return RedirectResponse("/login", status_code=303)

    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except:
        return RedirectResponse("/login", status_code=303)

    return await call_next(request)


# ============================================================
#   LOGIN
# ============================================================
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": False})


@app.post("/login")
async def login(request: Request, password: str = Form(...)):

    ip = request.client.host

    if ip in FAILED_LOGINS and FAILED_LOGINS[ip]["count"] >= MAX_LOGIN_ATTEMPTS:
        if datetime.now() < FAILED_LOGINS[ip]["block_until"]:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Demasiados intentos. Inténtelo más tarde."}
            )
        else:
            FAILED_LOGINS[ip] = {"count": 0}

    if not bcrypt.checkpw(password.encode("utf-8"), HASHED_PASSWORD):
        FAILED_LOGINS.setdefault(ip, {"count": 0})
        FAILED_LOGINS[ip]["count"] += 1

        if FAILED_LOGINS[ip]["count"] >= MAX_LOGIN_ATTEMPTS:
            FAILED_LOGINS[ip]["block_until"] = datetime.now() + timedelta(minutes=BLOCK_TIME_MINUTES)

        return templates.TemplateResponse("login.html", {"request": request, "error": True})

    token = jwt.encode(
        {"user": "admin", "exp": datetime.utcnow() + timedelta(hours=2)},
        JWT_SECRET,
        algorithm=JWT_ALGO
    )

    response = RedirectResponse(url="/home", status_code=303)

    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/"
    )

    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("session", path="/")
    return response


# ============================================================
#   HOME
# ============================================================
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    if not validar_token(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("home.html", {"request": request})


# ============================================================
#   DASHBOARD
# ============================================================
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    last_case_path = os.path.join("data", "last_case.json")
    case = None

    if os.path.exists(last_case_path):
        try:
            if os.path.getsize(last_case_path) > 0:
                with open(last_case_path, "r", encoding="utf-8") as f:
                    case = json.load(f)
        except:
            case = None

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "case": case}
    )


# ============================================================
#   FORMULARIO
# ============================================================
@app.get("/contrato", response_class=HTMLResponse)
async def show_form(request: Request):
    if not validar_token(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("form.html", {"request": request})


# ============================================================
#   GENERAR CONTRATO
# ============================================================
@app.post("/generate", response_class=HTMLResponse)
async def generate_contract(
    request: Request,
    vendedor_name: str = Form(...),
    vendedor_cedula: str = Form(...),
    vendedor_ciudad: str = Form(...),

    comprador_name: str = Form(...),
    comprador_cedula: str = Form(...),
    comprador_ciudad: str = Form(...),

    anio_posesion: str = Form(...),
    objeto: str = Form(...),
    referencia_catastral: str = Form(...),
    direccion_inmueble: str = Form(...),
    ubicacion_inmueble: str = Form(...),

    documento_tradicion: str = Form(...),
    vendedor_anterior_name: str = Form(...),
    vendedor_anterior_cedula: str = Form(...),

    valor_contrato: str = Form(...),
    forma_pago: str = Form(...),

    dia_firma: str = Form(...),
    mes_firma: str = Form(...),
    anio_firma: str = Form(...),
):

    unique_id = str(uuid.uuid4())[:8]

    ctx = AgentContext(
        case_id=unique_id,
        data={
            "vendedor_name": vendedor_name,
            "vendedor_cedula": vendedor_cedula,
            "vendedor_ciudad": vendedor_ciudad,

            "comprador_name": comprador_name,
            "comprador_cedula": comprador_cedula,
            "comprador_ciudad": comprador_ciudad,

            "anio_posesion": anio_posesion,
            "objeto": objeto,
            "referencia_catastral": referencia_catastral,
            "direccion_inmueble": direccion_inmueble,
            "ubicacion_inmueble": ubicacion_inmueble,

            "documento_tradicion": documento_tradicion,
            "vendedor_anterior_name": vendedor_anterior_name,
            "vendedor_anterior_cedula": vendedor_anterior_cedula,

            "valor_contrato": valor_contrato,
            "forma_pago": forma_pago,

            "dia_firma": dia_firma,
            "mes_firma": mes_firma,
            "anio_firma": anio_firma,

            "fecha_contrato": f"{dia_firma} de {mes_firma} de {anio_firma}",
        }
    )

    result = CoordinatorAgent().run(ctx)

    if not result.success:
        return templates.TemplateResponse(
            "review.html",
            {
                "request": request,
                "file_name": None,
                "llm_analysis": ctx.data.get("llm_analysis", ""),
                "errors": result.issues
            }
        )

    file_name = ctx.data.get("generated_file")

    os.makedirs("data", exist_ok=True)
    last_case_path = os.path.join("data", "last_case.json")

    with open(last_case_path, "w", encoding="utf-8") as f:
        json.dump({
            "id": unique_id,
            "file": file_name,
            "vendedor": vendedor_name,
            "comprador": comprador_name,
            "fecha": ctx.data.get("fecha_contrato"),
            "pipeline": ctx.data.get("pipeline", []),
        }, f, indent=4, ensure_ascii=False)

    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "file_name": file_name,
            "llm_analysis": ctx.data.get("llm_analysis", "")
        }
    )


# ============================================================
#   DESCARGA DE CONTRATOS
# ============================================================
@app.get("/download/{filename}")
async def download_file(filename: str):
    path = os.path.join("data", "generated", filename)

    if not os.path.exists(path):
        return HTMLResponse(f"<h3>Error: El archivo no existe → {path}</h3>", status_code=404)

    return FileResponse(
        path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
