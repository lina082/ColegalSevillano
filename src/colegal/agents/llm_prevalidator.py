from src.colegal.agents.agent_base import BaseAgent, AgentResult, AgentContext
from src.colegal.llm.openai_client import call_llm
import json


class LLMPreValidatorAgent(BaseAgent):
    """
    Asesor jurídico previo:
    - Revisa los datos ingresados
    - Señala problemas y advertencias
    - NO bloquea la generación del contrato
    """
    name = "llm_prevalidator"

    def run(self, ctx: AgentContext) -> AgentResult:
        datos = ctx.data

        # Convertir los datos a JSON para evitar errores de formato
        datos_json = json.dumps(datos, ensure_ascii=False, indent=2)

        prompt = f"""
Eres un abogado asistente colombiano.

Te doy los datos con los que se va a llenar un contrato de compraventa (en formato JSON):

{datos_json}

Tu tarea:
1. Identifica problemas graves (datos faltantes, incoherencias obvias, campos incorrectos).
2. Señala advertencias (cosas sospechosas, formatos raros, valores que se deberían confirmar).
3. Usa un tono claro, preciso y respetuoso.
4. NO redactes cláusulas ni cambies el estilo del contrato.
5. NO sugieras cambios legales, solo revisa datos.
6. No edites no toques nadad del contrato deja que salga como se usa en el contrato base, solo verifica y se su ASISTENTE

Responde SIEMPRE EXACTAMENTE en este formato:

Problemas:
- descripcion

Advertencias:
- descripcion
"""

        respuesta = call_llm(prompt).strip()

        #  Guardamos el feedback con un nombre claro y consistente
        ctx.data["assistant_feedback"] = respuesta

        self.log(ctx, "LLMPreValidatorAgent completado. Feedback almacenado en 'assistant_feedback'.")

        #  Devolvemos SOLO lo que aporta este agente
        return AgentResult(
            success=True,
            outputs={"assistant_feedback": respuesta}
        )
