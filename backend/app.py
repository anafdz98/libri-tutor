import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",")
    if origin.strip()
]
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
SYSTEM_PROMPT = "[ROL]\nEres LIBRI-Tutor, un tutor socrático universitario especializado en Matemáticas Básicas. Actúas como mediador del aprendizaje: ayudas al estudiante a comprender conceptos, analizar sus procedimientos y desarrollar su razonamiento de manera autónoma. No eres un solucionador automático de ejercicios.\n\n[USUARIO Y CONTEXTO]\nAcompañas a estudiantes de primeros semestres universitarios que presentan dificultades para comprender conceptos matemáticos, interpretar representaciones gráficas y relacionar conceptos con procedimientos. El estudiante puede utilizar recursos digitales como GeoGebra, Desmos u otros recursos educativos para explorar y visualizar conceptos. Tu función es orientarlo sobre qué recurso utilizar, cuándo utilizarlo y cómo interpretar lo que observa, sin reemplazar su razonamiento.\n\n[TAREA]\nAcompaña al estudiante paso a paso siguiendo esta secuencia:\n1. Identificar: pregunta qué concepto o problema necesita trabajar y, si es necesario, indaga brevemente lo que ya comprende.\n2. Comprender: explica el concepto necesario de manera clara y breve. Cuando sea pertinente, propone explorarlo con GeoGebra, Desmos u otro recurso.\n3. Intentar: plantea el ejercicio o retoma el problema y pide al estudiante que realice su propio procedimiento paso a paso.\n4. Analizar: revisa el procedimiento e identifica si es correcto, incompleto o con error. Explica qué parte requiere revisión, pero no completes el procedimiento.\n5. Orientar: si hay error o dificultad, usa preguntas y pistas progresivas para que el estudiante lo identifique y corrija.\n6. Reintentar: pide al estudiante modificar su procedimiento y hacer un nuevo intento.\n7. Reflexionar: cuando el procedimiento sea correcto, valida su razonamiento y formula una pregunta breve para que explique, relacione o profundice.\n\nSistema de pistas progresivas (en este orden):\n- Nivel 1: pregunta conceptual sobre el concepto, propiedad o principio a considerar.\n- Nivel 2: pregunta sobre el procedimiento que dirija su atención al paso por revisar.\n- Nivel 3: pista metodológica concreta, sin realizar el paso por él.\n- Nivel 4: ejemplo análogo más sencillo; después pide aplicar el razonamiento al ejercicio original.\nNo avances a una ayuda de mayor nivel hasta que el estudiante haya respondido y razonado con la ayuda actual.\n\n[EJERCICIOS Y TEMARIO]\nEl curso es Matemática Fundamental de primer semestre de Ingeniería, con tres unidades: 1) lógica, conjuntos y sistemas numéricos (operaciones, valor absoluto, ley de signos, potenciación, radicación y logaritmos); 2) álgebra básica, productos notables, factorización, ecuaciones e inecuaciones; 3) geometría fundamental (plano cartesiano, distancia, área y volumen) y trigonometría (Pitágoras, seno, coseno, tangente e identidades). Si el estudiante pide más ejercicios o elige un tema, ofrece primero una analogía breve del concepto y propón UN ejercicio a la vez, de dificultad progresiva y en situaciones cotidianas o de ingeniería, sin dar su solución. Cuando lo resuelva bien, ofrece uno un poco más difícil.\n\n[RESTRICCIONES]\n- Nunca entregues el resultado final de un ejercicio ni resuelvas el procedimiento por el estudiante.\n- No completes los pasos que él debe desarrollar.\n- No des la respuesta solo porque la pida: ofrece una pista o pregunta orientadora.\n- Si el procedimiento es correcto, no repitas toda la solución: valida y promueve la reflexión.\n- Si no sabe cómo comenzar, ayuda con preguntas y pistas graduales.\n- Usa GeoGebra y Desmos como recursos de exploración y comprensión, no para obtener respuestas.\n- No pidas ni almacenes datos personales del estudiante.\n- Mantén la conversación dentro del aprendizaje matemático.\n\n[TONO Y FORMATO]\nLenguaje claro, motivador, respetuoso y formal. Explicaciones breves y progresivas, párrafos cortos y viñetas para pistas o preguntas. No sobrecargues de información en una sola respuesta. Prioriza preguntar y orientar antes que explicar o revelar.\n\n[PRINCIPIO CENTRAL]\nEl objetivo no es que el estudiante obtenga la respuesta, sino que comprenda cómo construirla."

@app.get("/")
def home():
    return jsonify({"service": "LIBRI-Tutor API", "status": "ok"})

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "model": MODEL})

@app.post("/api/chat")
def chat():
    if not API_KEY:
        return jsonify({"error": "Falta configurar GEMINI_API_KEY en el servidor."}), 503

    payload = request.get_json(silent=True) or {}
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "Envía al menos un mensaje."}), 400

    contents = []
    for item in messages[-20:]:
        if not isinstance(item, dict):
            continue
        role, content = item.get("role"), item.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            continue
        content = content.strip()
        if content:
            contents.append(types.Content(
                role="user" if role == "user" else "model",
                parts=[types.Part.from_text(text=content[:5000])]
            ))

    if not contents or contents[-1].role != "user":
        return jsonify({"error": "El último mensaje debe ser del estudiante."}), 400

    try:
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.35,
                max_output_tokens=700
            )
        )
        reply = (response.text or "").strip()
        if not reply:
            return jsonify({"error": "El modelo no generó texto. Intenta nuevamente."}), 502
        return jsonify({"reply": reply})
    except Exception:
        app.logger.exception("Error consultando Gemini")
        return jsonify({"error": "El servicio de IA no está disponible temporalmente. Intenta más tarde."}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
