# LIBRI-Tutor — prototipo funcional

Se conserva el diseño y contenido del HTML original. El chat utiliza un backend Flask y Gemini. La clave de Gemini permanece en el servidor.

## Archivos
- `index.html`: frontend para GitHub Pages.
- `backend/app.py`: API Flask y prompt socrático.
- `backend/requirements.txt`: dependencias.
- `backend/.env.example`: variables de entorno.

## 1. Crear una clave Gemini
1. Ve a https://aistudio.google.com/app/apikey
2. Crea una API Key.
3. Guárdala como variable privada del backend. Nunca la pegues en el HTML ni en GitHub.

Consulta precios, tratamiento de datos y límites vigentes:
- https://ai.google.dev/gemini-api/docs/pricing/
- https://ai.google.dev/gemini-api/docs/rate-limits

## 2. Desplegar el backend
Usa un servicio compatible con Python/Flask (por ejemplo, Render):
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

Variables de entorno:
- `GEMINI_API_KEY`: tu clave privada.
- `GEMINI_MODEL`: `gemini-3.8-flash`.
- `ALLOWED_ORIGINS`: URL exacta de GitHub Pages, por ejemplo `https://USUARIO.github.io`.

Prueba `https://TU-SERVICIO.onrender.com/api/health`.

## 3. Publicar frontend en GitHub Pages
En `index.html`, cambia:
`const API_BASE = 'https://TU-SERVICIO.onrender.com';`
por la URL real del backend, sin `/` al final.

Sube `index.html` a tu repositorio y activa GitHub Pages en Settings → Pages.

## 4. Prueba local
Dentro de `backend`, crea un entorno virtual, instala `requirements.txt`, copia `.env.example` a `.env`, agrega tu clave y ejecuta `python app.py`.
Sirve `index.html` con Live Server y añade su origen (por ejemplo `http://127.0.0.1:5500`) a `ALLOWED_ORIGINS`.

## Consideraciones
- GitHub Pages no ejecuta Flask: el backend se aloja por separado.
- El nivel gratuito puede tener límites y condiciones cambiantes.
- Este prototipo no incluye autenticación, cuotas por estudiante ni protección avanzada contra abuso. No lo abras a uso masivo hasta añadir esos controles.
- El historial vive en memoria del navegador; no se guarda en una base de datos.
- El prompt socrático original se conserva en `backend/app.py`.
