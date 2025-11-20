from src.colegal.agents.agent_base import BaseAgent, AgentContext, AgentResult
from src.colegal.agents.ingestor import IngestorAgent
from src.colegal.agents.llm_prevalidator import LLMPreValidatorAgent
from src.colegal.agents.validator import ValidatorAgent
from src.colegal.agents.formatter import FormatterAgent

import os
import inspect
import time  # ⬅ NUEVO: para medir tiempos


class CoordinatorAgent(BaseAgent):
    name = "coordinator"

    def __init__(self):

        # Obtener ruta de este archivo
        current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        template_dir = os.path.join(current_dir, "..", "templates")

        # Ruta final de la plantilla base
        PLANTILLA_PATH = os.path.join(template_dir, "contrato_base.docx")
        print(f"\n[CoordinatorAgent] Ruta de plantilla configurada: {PLANTILLA_PATH}\n")

        # Inicializar agentes
        self.agents = [
            IngestorAgent(),
            LLMPreValidatorAgent(),
            ValidatorAgent(),
            FormatterAgent(template_path=PLANTILLA_PATH)
        ]

    def run(self, ctx: AgentContext) -> AgentResult:

        print("\n==============================")
        print(" INICIO DEL PIPELINE COLEGAL ")
        print("==============================\n")

        self.log(ctx, f"Iniciando coordinación para caso {ctx.case_id}")

        try:
            for agent in self.agents:

                print(f"\n➡ Ejecutando agente: {agent.name}")
                ctx.data["current_agent"] = agent.name

                # ⏱ inicio del tiempo
                start_time = time.time()

                # ---------------------------
                #   FORMATTER (último paso)
                # ---------------------------
                if agent.name == "formatter":

                    print("   [Formatter] Preparando archivo...")

                    os.makedirs("data/generated", exist_ok=True)

                    filename = f"contrato_{ctx.case_id}.docx"
                    output_path = os.path.join("data", "generated", filename)

                    agent.generate_contract(ctx.data, output_path)

                    if not os.path.exists(output_path):
                        print(f"❌ ERROR: El archivo NO se generó: {output_path}")
                        return AgentResult(
                            success=False,
                            issues=[f"No se pudo generar el archivo: {output_path}"]
                        )

                    ctx.data["generated_file"] = filename
                    print(f"   ✔ Archivo generado correctamente: {filename}")

                    elapsed = round(time.time() - start_time, 3)

                    # REGISTRAR EN PIPELINE
                    ctx.data.setdefault("pipeline", []).append({
                        "agent": agent.name,
                        "status": "completed",
                        "time": elapsed
                    })

                    continue

                # ---------------------------
                #   AGENTES NORMALES
                # ---------------------------
                result = agent.run(ctx)

                print(f"   → Resultado {agent.name}: success={result.success}")

                if not result.success:
                    print(f"❌ ERROR en {agent.name}: {result.issues}\n")
                    ctx.data["status"] = "error"
                    return result

                if result.outputs:
                    ctx.data.update(result.outputs)
                    print(f"   ✔ Outputs recibidos: {list(result.outputs.keys())}")

                # Capturar análisis del LLM
                if agent.name == "llm_prevalidator":
                    llm_text = (
                        result.outputs.get("analysis")
                        or result.outputs.get("assistant_feedback")
                        or result.outputs.get("llm_analysis")
                        or result.outputs.get("text")
                        or ""
                    )
                    ctx.data["llm_analysis"] = llm_text
                    print("   ✔ Análisis del LLM capturado.")

                elapsed = round(time.time() - start_time, 3)

                # REGISTRAR AGENTE EN PIPELINE
                ctx.data.setdefault("pipeline", []).append({
                    "agent": agent.name,
                    "status": "completed",
                    "time": elapsed
                })

            # ---------------------------
            #   PIPELINE COMPLETO
            # ---------------------------
            print("\n✔ Pipeline completado sin errores.")
            ctx.data["status"] = "success"

            return AgentResult(success=True, outputs=ctx.data)

        except Exception as e:
            print("\n❌ EXCEPCIÓN CRÍTICA:")
            print(str(e))
            print("Agente donde se rompió:", ctx.data.get("current_agent"))

            return AgentResult(
                success=False,
                issues=[f"Error inesperado: {str(e)}"]
            )
