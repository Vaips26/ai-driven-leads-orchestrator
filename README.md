# AI-Driven Leads Orchestrator

Sistema de arquitectura desacoplada para la ingesta, calificación inteligente y distribución automatizada de clientes potenciales (leads). El sistema integra un servidor API asíncrono, un microservicio de procesamiento semántico utilizando modelos de lenguaje locales (LLM) y un panel de control interactivo para la visualización de métricas de negocio.

## Estructura del Directorio del Proyecto

El ecosistema se divide de forma modular en tres componentes independientes:

ai-driven-leads-orchestrator/
├── backend/          # Servidor API de alto rendimiento (FastAPI & SQLAlchemy)
├── frontend/         # Panel de administración interactivo (React & Tailwind)
└── automation/       # Orquestador asíncrono de Inteligencia Artificial (Ollama API)

---

## Módulos del Sistema

### 1. Servidor de Persistencia (backend/)
Desarrollado con FastAPI y SQLAlchemy. Actúa como la fuente única de verdad (Single Source of Truth) para la persistencia de datos.
*   API REST: Expone endpoints seguros para el ingreso (POST /leads/), consulta estructurada (GET /leads/) y actualización de estados (PUT /leads/{id}).
*   Base de Datos: Base de datos relacional integrada (SQLite/PostgreSQL) encargada de almacenar de forma consistente la información de contacto y los metadatos analizados por la IA.
*   CORS: Configuración de middleware para habilitar de forma segura peticiones cruzadas desde orígenes desacoplados (Frontend).

### 2. Capa de Automatización e IA (automation/)
Script en Python encargado del procesamiento de datos en segundo plano sin intervención humana.
*   Análisis Semántico Local: Consume la API local de Ollama utilizando el modelo qwen2.5:7b para analizar el mensaje original del prospecto de forma contextual.
*   Extracción de JSON: Implementa un motor de filtrado por expresiones regulares para asegurar la extracción limpia de un objeto JSON estructurado que define el presupuesto estimado, categoría de presupuesto e índice de calidad del lead (0-100).
*   Orquestación de Alertas: Dispara hilos lógicos condicionales que detectan prospectos prioritarios (Score >= 70) para simular el despacho inmediato de notificaciones hacia servicios externos.

### 3. Panel de Administración (frontend/)
Interfaz gráfica de usuario desarrollada con React y Vite.
*   Métricas Operativas (KPIs): Calcula en tiempo real indicadores clave como la tasa de calificación de la IA, el promedio de calidad general y el total de leads calientes en el embudo.
*   Ingesta Integrada: Cuenta con un panel de simulación de formularios para realizar pruebas de estrés de forma directa a la API.

---

## Guía de Configuración Local

### Requisitos Previos:
*   Python 3.12 instalado en el sistema.
*   Node.js 18+ instalado.
*   Servicio de Ollama activo localmente con el modelo qwen2.5:7b descargado.

### Configuración del Servidor (Puerto 8000):
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

### Configuración del Orquestador de IA:
cd automation
pip install -r requirements.txt
python ai_orchestrator.py

### Configuración del Dashboard (Puerto 5173):
cd frontend
npm install
npm run dev
