# Guía Paso a Paso — Crear tu Custom GPT en ChatGPT

## Requisitos Previos
- Cuenta de ChatGPT **Plus** (necesaria para crear GPTs personalizados)
- Acceso a: https://chat.openai.com/gpts

---

## Paso 1: Crear el GPT

1. Ve a **https://chat.openai.com/gpts**
2. Haz clic en **"Create a GPT"** (Crear un GPT)
3. Se abrirá el editor con dos pestañas: **"Create"** (conversacional) y **"Configure"** (manual)

---

## Paso 2: Configurar el Nombre y Descripción

En la pestaña **"Configure"**:

- **Name**: `AppMillonaria AI`
- **Description**: `Analista deportivo experto en pronósticos de fútbol basados en tendencias y datos reales. Analiza partidos, mercados y cuotas para dar pronósticos de alto valor con metodología estricta.`
- **Instructions**: *(Copia todo el contenido del archivo `01-instrucciones-sistema.md`)*

---

## Paso 3: Subir Archivos de Conocimiento

En la sección **"Knowledge"** (Conocimiento):

1. Haz clic en **"+ Upload files"**
2. Sube estos archivos **uno por uno**:
   - `01-instrucciones-sistema.md` ← (también van como instrucciones)
   - `02-guia-mercados.md` ← Guía de mercados de fútbol
   - `03-tendencias-datos.md` ← Tendencias y fuentes de datos
   - `04-ejemplos-conversacion.md` ← Ejemplos de cómo responder

> Los archivos de conocimiento le dan al GPT contexto extra que las instrucciones solas no cubren.

---

## Paso 4: Configurar Capacidades

En **"Capabilities"** (Capacidades):

- ✅ **Web Browsing** → Actívalo para que pueda buscar datos en tiempo real
- ❌ **DALL-E** → No lo necesitas
- ❌ **Code Interpreter** → No lo necesitas

---

## Paso 5: Configurar Acciones (Opcional pero Recomendado)

Si quieres que el GPT pueda consultar datos del backend de tu app:

1. Haz clic en **"Create new action"**
2. En **Schema**, pega:

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "AppMillonaria API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://app-millonaria-backend.onrender.com"
    }
  ],
  "paths": {
    "/api/predictions": {
      "get": {
        "operationId": "getPredictions",
        "summary": "Obtener pronósticos del día",
        "responses": {
          "200": {
            "description": "Lista de pronósticos"
          }
        }
      }
    },
    "/api/predictions/history": {
      "get": {
        "operationId": "getHistory",
        "summary": "Obtener historial de pronósticos",
        "responses": {
          "200": {
            "description": "Historial de pronósticos"
          }
        }
      }
    }
  }
}
```

3. En **Authentication**, selecciona **None** (los endpoints son públicos)

> Esto le permite al GPT consultar tus pronósticos reales y comparar con su análisis.

---

## Paso 6: Configurar el Intro Message

En **"Conversation starters"** (Iniciadores de conversación):

1. `⚽ Analiza River Plate vs Boca Juniors`
2. `📊 ¿Cuáles son los mejores pronósticos de hoy?`
3. `🔥 ¿Qué tendencias estás viendo en la Premier League?`
4. `💡 Explícame tu metodología de análisis`

---

## Paso 7: Probar y Publicar

1. **Prueba** el GPT en el panel derecho con preguntas como:
   - "Analizame el partido X vs Y"
   - "¿Por qué el BTTS es mejor que el resultado exacto?"
   - "Dame un pronóstico con alta confianza"

2. Si las respuestas son correctas, haz clic en **"Update"** → **"Confirm"**

3. **Configura la visibilidad**:
   - **"Only me"** → Solo tú lo usas
   - **"Anyone with the link"** → Compartes el link y cualquiera lo usa
   - **"Public"** → Aparece en el GPT Store

4. **Recomendación**: Públicalo como **"Anyone with the link"** para compartirlo en tus redes y con usuarios de la app.

---

## Paso 8: Compartir

Una vez publicado, obtienes un link como:
```
https://chat.openai.com/g/g-XXXXXXXXX-appmillonaria-ai
```

### Dónde compartirlo:
- En la sección **Premium** de tu app web (como bonus)
- En redes sociales (Twitter, Instagram, TikTok)
- En tu perfil de TipsterPage
- En grupos de pronósticos de fútbol

---

## Tips para Mejorar el GPT

### Iterar con el "Create" tab
Si algo no funciona bien, ve a la pestaña **"Create"** y dale instrucciones en lenguaje natural:
- "Haz que siempre pregunte la cuota disponible antes de dar un pronóstico"
- "Si el usuario no da datos, busca en la web tendencias recientes"
- "Agrega siempre el disclamer de responsabilidad"

### Actualizar conocimiento regularmente
- Cada 2-4 semanas, sube archivos actualizados con:
  - Nuevas tendencias de ligas
  - Cambios en mercados
  - Mejoras en metodología
  - Ejemplos de pronósticos acertados

### Monitorear calidad
- Revisa las conversaciones periódicamente
- Si el GPT da malos pronósticos, ajusta las instrucciones
- Si es demasiado conservador, baja el umbral de confianza a 60%
