from src.colegal.agents.agent_base import BaseAgent, AgentResult, AgentContext

class IngestorAgent(BaseAgent):
    """
    Ingestor limpio y moderno:
    - Limpia texto (espacios, capitalización)
    - Normaliza números
    - Prepara datos para el validator
    """

    name = "ingestor"

    @staticmethod
    def clean_text(value):
        if not value:
            return value
        return " ".join(value.strip().split())

    @staticmethod
    def clean_number(value):
        if not value:
            return value
        return value.replace(".", "").replace(",", "").strip()

    def run(self, ctx: AgentContext) -> AgentResult:
        data = ctx.data

        self.log(ctx, "Ingestor: limpiando datos...")

        cleaned = {}

        # Campos que solo necesitan limpieza básica
        text_fields = [
            "vendedor_name", "vendedor_ciudad",
            "comprador_name", "comprador_ciudad",
            "objeto", "direccion_inmueble", "ubicacion_inmueble",
            "documento_tradicion", "vendedor_anterior_name"
        ]

        for field in text_fields:
            cleaned[field] = self.clean_text(data.get(field, ""))

        # Cédulas (limpieza numérica)
        id_fields = [
            "vendedor_cedula",
            "comprador_cedula",
            "vendedor_anterior_cedula"
        ]

        for field in id_fields:
            cleaned[field] = self.clean_number(data.get(field, ""))

        # Números grandes: valor contrato
        cleaned["valor_contrato"] = self.clean_number(data.get("valor_contrato", ""))

        # Año, días, etc.
        cleaned["anio_posesion"] = self.clean_number(data.get("anio_posesion", ""))
        cleaned["dia_firma"] = self.clean_number(data.get("dia_firma", ""))
        cleaned["anio_firma"] = self.clean_number(data.get("anio_firma", ""))

        # Mes firma → texto
        cleaned["mes_firma"] = self.clean_text(data.get("mes_firma", ""))

        # Forma de pago → texto limpio
        cleaned["forma_pago"] = self.clean_text(data.get("forma_pago", ""))

        # Guardar datos limpios en ctx
        ctx.data.update(cleaned)

        self.log(ctx, "Ingestor completado.")

        return AgentResult(success=True, outputs=ctx.data)
