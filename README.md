# App Millonaria ⚽

Web de pronósticos deportivos que analiza las **tendencias calientes (fuego)** de
cada partido de fútbol y publica los pronósticos que cumplen el filtro de
negocio:

- Tendencias **positivas** (a favor) marcadas con **fuego/llama**
- Mercados que **involucran a ambos equipos**: más de 2.5, ambos marcan (BTTS),
  gana el local, gana o empata (1X / X2)
- **Cuota ≥ 1.70**

## Arquitectura

```
├── frontend/          React + Vite + TypeScript (web estilo IA)
├── backend/           FastAPI + Python (scraping, API, webhook de pagos)
├── firebase/          firestore.rules + índices
└── .github/           workflow de scraping automático (GitHub Actions)
```

| Pieza | Tecnología |
|---|---|
| Frontend | React + Vite + TypeScript |
| Backend | Python FastAPI |
| Base de datos | Firebase Firestore (solo vía backend) |
| Autenticación | Firebase Auth (Google) |
| Pagos | TipsterPage (webhook firmado + referencia única) |
| Scraping automático | GitHub Actions (cron diario a las 1 AM hora de Colombia) |

## Política de pronósticos por día

Cada día el scraper publica los pronósticos detectados y se aplica la regla de
gratis/premium automáticamente:

- **Con pocos pronósticos** (por debajo del umbral) se regala **1**.
- **Con bastantes** (igual o más que el umbral) se regalan **2**.
- El cupo gratis lo ocupan los pronósticos **más sólidos** (mayor confianza y
  cuota), que es donde la app demuestra su valor.
- El resto del día es **Premium** (requiere suscripción activa).
- Las ligas listadas en `PREMIUM_LEAGUES` siempre son premium (nunca ocupan el
  cupo gratis).

Configurables en `backend/.env`:

```ini
FREE_PREDICTIONS_WHEN_FEW=1
FREE_PREDICTIONS_WHEN_MANY=2
FREE_PREDICTIONS_THRESHOLD=5
```

- **Hoy** (`/api/predictions/today`): solo los del día calendario de Colombia.
- **Historial** (`/api/predictions/history`): los días anteriores quedan
  guardados y visibles en la sección **Historial** de la web (`/historial`).

## Seguridad (aplicada desde el día 1)

- **Firestore:** `deny all` por defecto; la web nunca escribe directo (todo pasa
  por el backend con el Admin SDK).
- **Pronósticos premium:** solo los lee el backend para usuarios con
  `custom claim premium`; además el navegador bloquea visualmente el contenido.
- **Webhook de pagos:** firma HMAC-SHA256 verificada; el pago se vincula al usuario
  por referencia única de compra (nunca por texto libre).
- **Secrets:** nunca en código; todo en `.env` (ignorado por git) o en secrets
  de GitHub.
- **Headers de seguridad, rate limiting y CORS restringido** en el backend.

## Guía rápida (desarrollo)

### 1. Backend

```bash
cd backend
cp .env.example .env       # y rellénalo
cd ..
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r backend\requirements.txt
uvicorn app.main:app --reload --port 8000   # desde backend/
```

Comprueba: http://localhost:8000/api/health

### 2. Frontend

```bash
cd frontend
cp .env.example .env       # rellena con tu config de Firebase
npm install
npm run dev
```

Web en http://localhost:5173

### 3. Firebase

1. Crea el proyecto en https://console.firebase.google.com
2. **Authentication → Sign-in method → Google** → habilítalo.
3. **Firestore Database** → crea la base en modo producción.
4. **Configuración del proyecto → Cuentas de servicio → Firebase Admin SDK →
   Generar clave privada** → guarda el JSON y pónlo en tu `.env`
   (`FIREBASE_SERVICE_ACCOUNT_PATH`).
5. Despliega las reglas:
   ```bash
   cd firebase
   firebase login
   firebase deploy --only firestore:rules,firestore:indexes
   ```

### 4. Scraper (manual)

```bash
python run_scraper.py --dry   # desde backend/, sin publicar
python run_scraper.py         # publica en Firestore
```

### 5. Scraper automático (1 AM hora de Colombia) — gratis

El repositorio incluye un **workflow de GitHub Actions**
(`.github/workflows/daily-scrape.yml`) que ejecuta el scraper todos los días a
las **1:00 AM hora de Colombia** (06:00 UTC), gratis en GitHub.

Para activarlo:

1. Sube el repo a GitHub (público o privado).
2. Ve a **Settings → Secrets and variables → Actions** y añade:
   - `FIREBASE_PROJECT_ID` → tu ID de proyecto Firebase.
   - `FIREBASE_SERVICE_ACCOUNT_BASE64` → el JSON del service account de Firebase
     **codificado en base64**. Genera el valor en PowerShell:
     ```powershell
     $json = Get-Content "ruta\service-account.json" -Raw
     $b64  = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))
     $b64  # cópialo y pégalo en el secret
     ```
   También puedes usar tu propio cron de confianza (cualquier servidor que
   ejecute `python run_scraper.py` a la 1 AM) — el comando es el mismo.

> Nota: el daily scrape sobreescribe los pronósticos del mismo `match_id` del día
> (merge) y deja intactos los de días anteriores para el historial.

### 6. Pagos con TipsterPage

1. Crea el producto (suscripción premium) en https://app.tipsterpage.com y copia
   su link en `TIPSTERPAGE_PRODUCT_URL`.
2. En TipsterPage configura un webhook que apunte a
   `TU_BACKEND/api/webhooks/tipsterpage` con el secreto `TIPSTERPAGE_WEBHOOK_SECRET`.
3. El usuario paga desde la web → se crea una orden con `ref=<order_id>` →
   TipsterPage no notifica la venta → el backend valida firma, localiza la orden
   por referencia/email y activa premium automáticamente.
4. Fallback: endpoint `POST /api/purchase/admin/grant` (solo admin) para subir
   premium manualmente si el webhook falla.

## Endpoints

| Método | Path | Descripción |
|---|---|---|
| GET | `/api/predictions` | Pronósticos (free; premium si estás suscrito) |
| GET | `/api/predictions/today` | Pronósticos del día (hora Colombia) |
| GET | `/api/predictions/history` | Historial: días anteriores |
| GET | `/api/predictions/{match}/{selection}` | Detalle |
| POST | `/api/purchase/intent` | Crea orden + link de pago único (auth) |
| POST | `/api/refresh-claims` | Estado premium al fresco (auth) |
| POST | `/api/webhooks/tipsterpage` | Webhook firmado de pagos |
| POST | `/api/purchase/admin/grant` | Premium manual (admin) |

## Estado del proyecto

- [x] Fase 1 — Scaffolding (frontend + backend + Firebase rules)
- [x] Fase 2 — Scraper 365scores (API `/web/games/` + `/web/trends/`) + filtro de pronósticos (tests incluidos)
- [x] Fase 3 — API (auth JWT, pronósticos free/premium, rate limit) + reglas Firestore
- [x] Fase 4 — Interfaz (tema IA, login Google, pronósticos con gating, precios, perfil)
- [x] Fase 5 — Webhook de pagos TipsterPage (firma HMAC, activación premium idempotente, fallback admin)
- [x] Fase 6 — Política 1-2 gratis/día + sección Historial + logo limpio
- [x] Scraping automático diario 1 AM Colombia (workflow GitHub Actions)
- [ ] Paso usuario: crear proyecto Firebase + credenciales + desplegar reglas
- [ ] Paso usuario: subir repo a GitHub + añadir secrets del workflow
- [ ] Validación en vivo: scraper real, login y premium de prueba

> Los pronósticos son informativos. Apuesta con responsabilidad.