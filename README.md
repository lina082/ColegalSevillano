# COLEGAL SEVILLANO
Sistema multiagente para generación automática de contratos de compraventa usando FastAPI + OpenAI.

## Descripción
Colegal Sevillano es un backend en Python que implementa un flujo multiagente para redactar, validar y formatear contratos legales de bienes inmuebles.  
Incluye autenticación, dashboard de seguimiento, exportación de documentos y trazabilidad completa vía base de datos.

##  Arquitectura principal
FastAPI Backend
├── Coordinator Agent
│ ├── Ingestor
│ ├── Retriever
│ ├── Generator (OpenAI GPT-4o-mini)
│ ├── Validator
│ └── Formatter
├── SQLite DB (sessions, agent_logs, errors)
└── Dashboard (Jinja2 + Bootstrap)

## Tecnologías

Python 3.10+

FastAPI + Uvicorn

OpenAI GPT-4o-mini

SQLite

Bootstrap 5

Jinja2 Templates
 
## Funcionalidades

Generación automática de contratos (.docx)

Sistema multiagente orquestado por CoordinatorAgent

Validación y formateo de cláusulas

Dashboard de seguimiento (no técnico)

Autenticación con cookies

Logs y auditoría de procesos

## Estructuras de Datos usadas

Diccionarios (JSON) para inputs y contexto

Listas dinámicas para logs temporales

Cola lógica (pipeline de agentes)

Pila (stacktrace)

Modelo relacional (árbol 1→N) en SQLite

##  Autora
Lina Serna
Estudiante de Ingeniería en Ciencia de Datos
Institución Tecnológica de Medellín – ITM


## Licencia

Este proyecto es de uso académico y personal.# ColegalSevillano
