import json
import re
import sys
import requests

BACKEND_URL = "http://127.0.0.1:8000"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b" 

def obtener_leads_nuevos():
    """Obtiene todos los leads del backend y filtra los que tienen estatus 'New'."""
    try:
        response = requests.get(f"{BACKEND_URL}/leads/")
        response.raise_for_status()
        todos_los_leads = response.json()
        leads_nuevos = [lead for lead in todos_los_leads if lead.get("status") == "New"]
        return leads_nuevos
    except Exception as e:
        print(f"[ERROR] No se pudieron obtener los leads del backend: {e}")
        return []

def analizar_mensaje_con_ia(mensaje):
    """
    Envía el mensaje del lead a Ollama para calificarlo.
    Retorna un diccionario con: budget, budget_tier y lead_score.
    """
    system_prompt = (
        "Actúa como un calificador de leads altamente riguroso. "
        "Analiza el mensaje del usuario para estimar su presupuesto (budget), "
        "clasificar su nivel de presupuesto (budget_tier: 'Bajo', 'Medio' o 'Alto') "
        "y asignar un puntaje de lead (lead_score: entero de 0 a 100) según su intención de compra y viabilidad. "
        "Debes responder ÚNICAMENTE un objeto JSON válido con el siguiente formato, sin texto adicional, "
        "sin explicaciones y sin bloques de código markdown:\n"
        '{"budget": float_o_null, "budget_tier": "Bajo"|"Medio"|"Alto", "lead_score": int_0_100}'
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": f"System: {system_prompt}\n\nUser Message: {mensaje}\n\nResponse:",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        resultado = response.json()
        texto_ia = resultado.get("response", "").strip()

        # Limpieza robusta para extraer el JSON en caso de que la IA incluya texto extra o markdown
        match = re.search(r"\{.*\}", texto_ia, re.DOTALL)
        if match:
            json_clean = match.group(0)
        else:
            json_clean = texto_ia

        datos_ia = json.loads(json_clean)

        return {
            "budget": datos_ia.get("budget"),
            "budget_tier": datos_ia.get("budget_tier", "Bajo"),
            "lead_score": int(datos_ia.get("lead_score", 0))
        }
    except Exception as e:
        print(f"[ERROR] Error al procesar con IA o parsear el JSON. Detalle: {e}")
        return {
            "budget": None,
            "budget_tier": "Bajo",
            "lead_score": 0
        }

def actualizar_lead_en_backend(lead_id, name, email, phone, raw_message, budget, budget_tier, lead_score):
    """Envía una petición PUT para actualizar el lead con los datos calificados y estatus 'Qualified'."""
    payload = {
        "name": name,
        "email": email,
        "phone": phone,
        "raw_message": raw_message,
        "status": "Qualified",
        "budget": budget,
        "budget_tier": budget_tier,
        "lead_score": lead_score
    }
    
    response = None
    try:
        response = requests.put(f"{BACKEND_URL}/leads/{lead_id}", json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo actualizar el lead {lead_id} en el backend: {e}")
        if response is not None:
            print(f"[DETALLE VALIDACIÓN BACKEND] -> {response.text}")
        return False

def ejecutar_orquestacion():
    """Función principal que coordina el flujo de automatización."""
    print("[LOG] Iniciando proceso de orquestación de leads...")
    leads_nuevos = obtener_leads_nuevos()

    if not leads_nuevos:
        print("[LOG] Sin leads nuevos por procesar.")
        return

    print(f"[LOG] Se encontraron {len(leads_nuevos)} leads nuevos para procesar.")

    for lead in leads_nuevos:
        lead_id = lead["id"]
        name = lead["name"]
        email = lead["email"]
        phone = lead.get("phone")
        mensaje = lead.get("raw_message", "")

        print(f"\n[LOG] Procesando lead ID {lead_id}: {name} ({email})...")

        # Analizar con IA
        analisis = analizar_mensaje_con_ia(mensaje)
        budget = analisis["budget"]
        budget_tier = analisis["budget_tier"]
        lead_score = analisis["lead_score"]

        print(f"[LOG] Análisis de IA completado -> Score: {lead_score}, Tier: {budget_tier}, Presupuesto: {budget}")

        # Actualizar backend
        exito = actualizar_lead_en_backend(
            lead_id=lead_id,
            name=name,
            email=email,
            phone=phone,
            raw_message=mensaje,
            budget=budget,
            budget_tier=budget_tier,
            lead_score=lead_score
        )

        if exito:
            print(f"[LOG] Lead {lead_id} actualizado exitosamente a 'Qualified'.")
            if lead_score >= 70:
                print(f"[ALERTA - LEADS CALIENTES] ¡Lead de alta prioridad calificado! Enviando notificación automática a WhatsApp y Correo para: {email}")
        else:
            print(f"[ERROR] Falló la actualización del lead {lead_id}.")

if __name__ == '__main__':
    ejecutar_orquestacion()