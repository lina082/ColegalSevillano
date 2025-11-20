import re
from src.colegal.agents.agent_base import BaseAgent, AgentResult, AgentContext

class ValidatorAgent(BaseAgent):
    """
    Valida TODAS las variables esenciales del contrato:
    - Campos obligatorios
    - Formato numérico
    - Cédulas
    - Fechas
    - Referencia catastral
    - Texto básico
    """

    name = "validator"

    MESES_VALIDOS = {
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    }

    def run(self, ctx: AgentContext) -> AgentResult:
        data = ctx.data
        issues = []

        # ========= 1. CAMPOS OBLIGATORIOS =========
        required_fields = [
            "vendedor_name", "vendedor_cedula", "vendedor_ciudad",
            "comprador_name", "comprador_cedula", "comprador_ciudad",
            "anio_posesion", "objeto",
            "referencia_catastral", "direccion_inmueble", "ubicacion_inmueble",
            "documento_tradicion", "vendedor_anterior_name", "vendedor_anterior_cedula",
            "valor_contrato", "forma_pago",
            "dia_firma", "mes_firma", "anio_firma"
        ]

        for field in required_fields:
            if not data.get(field) or str(data[field]).strip() == "":
                issues.append(f"⚠ Falta el campo obligatorio: {field}")

        # Si faltan campos, salimos temprano
        if issues:
            return AgentResult(success=False, issues=issues)

        # ========= 2. VALIDAR NOMBRES =========
        name_fields = [
            "vendedor_name",
            "comprador_name",
            "vendedor_anterior_name"
        ]

        for field in name_fields:
            if re.search(r"\d", data[field]):
                issues.append(f"❌ El nombre '{data[field]}' contiene números, revise el dato.")

        # ========= 3. VALIDAR CÉDULAS =========
        cedulas = {
            "vendedor_cedula": data["vendedor_cedula"],
            "comprador_cedula": data["comprador_cedula"],
            "vendedor_anterior_cedula": data["vendedor_anterior_cedula"],
        }

        for name, ced in cedulas.items():
            if not ced.isdigit() or len(ced) < 6:
                issues.append(f"❌ La cédula en '{name}' no es válida: {ced}")

        # ========= 4. VALIDAR AÑOS =========
        for year_field in ["anio_posesion", "anio_firma"]:
            year = str(data[year_field])
            if not year.isdigit() or len(year) != 4:
                issues.append(f"❌ Año inválido en '{year_field}': {year}")

        # Coherencia entre años
        if data["anio_posesion"].isdigit() and data["anio_firma"].isdigit():
            if int(data["anio_posesion"]) > int(data["anio_firma"]):
                issues.append("⚠ El año de posesión no puede ser mayor al año de firma del contrato.")

        # ========= 5. VALIDAR DÍA =========
        dia = data["dia_firma"]
        if not dia.isdigit() or not (1 <= int(dia) <= 31):
            issues.append("❌ El día de firma no es válido (1–31).")

        # ========= 6. VALIDAR MES =========
        mes = data["mes_firma"].strip().lower()
        if mes not in self.MESES_VALIDOS:
            issues.append(f"❌ Mes inválido: '{data['mes_firma']}' (debe ser nombre en español)")

        # ========= 7. VALIDAR VALOR =========
        valor = data["valor_contrato"]
        if not valor.isdigit():
            issues.append(f"❌ El valor del contrato debe ser un número sin comas ni puntos: '{valor}'")

        # ========= 8. VALIDAR REFERENCIA CATASTRAL =========
        # Formato típico: 01-01-00-00-0456-0045-0-00-00-0000
        if not re.match(r"^[0-9\-]+$", data["referencia_catastral"]):
            issues.append("❌ La referencia catastral solo puede contener números y guiones.")

        if len(data["referencia_catastral"]) < 10:
            issues.append("❌ La referencia catastral es demasiado corta.")

        # ========= 9. VALIDAR FORMA DE PAGO =========
        if len(data["forma_pago"].strip()) < 5:
            issues.append("❌ La forma de pago es demasiado corta. Debe describir cómo se realizará.")

        # ========= RESULTADO FINAL =========
        if issues:
            self.log(ctx, f"Errores encontrados: {issues}")
            return AgentResult(success=False, issues=issues)

        self.log(ctx, "Validación completada exitosamente.")
        return AgentResult(success=True, outputs=data)
