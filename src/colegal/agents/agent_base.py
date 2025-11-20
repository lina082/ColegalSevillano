from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class AgentContext:
    """Contexto compartido entre los agentes"""
    case_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)

@dataclass
class AgentResult:
    success: bool
    outputs: Dict[str, Any] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)

class BaseAgent(ABC):
    """Clase base para todos los agentes"""
    name: str = "base_agent"

    def log(self, ctx: AgentContext, msg: str):
        ctx.logs.append(f"[{self.name}] {msg}")

    @abstractmethod
    def run(self, ctx: AgentContext) -> AgentResult:
        pass
