# Tendencias y Fuentes de Datos — Para AppMillonaria AI

## Fuentes de Datos Principales

### 1. 365scores (webws.365scores.com)
- **Qué ofrece**: Tendencias de partidos, estadísticas en tiempo real, datos históricos.
- **Cómo identificar tendencias "calientes"**:
  - Ícono de llama 🔥 junto a la tendencia
  - Tendencia activa en los últimos 5-10 partidos
  - Consistencia > 60% en la dirección de la tendencia
- **Ejemplo de tendencia válida**:
  - "River Plate — Ambos marcan: Sí en 7 de los últimos 8 partidos" 🔥
  - Esto es una tendencia caliente porque: alta frecuencia + ambos lados relevantes

### 2. SofaScore
- **Qué ofrece**: Ratings de jugadores, estadísticas avanzadas, xG (expected goals).
- **Dato clave**: xG (goles esperados) — si un equipo promedia xG > 1.5 por partido, su ofensiva es sólida.

### 3. FlashScore
- **Qué ofrece**: H2H (head-to-head), forma reciente, comparativas.
- **Dato clave**: Historial de enfrentamientos directos — especialmente útil para derbies.

### 4. Transfermarkt
- **Qué ofrece**: Valor de plantel, lesiones, fichajes.
- **Dato clave**: Lesiones de jugadores clave pueden cambiar completamente un pronóstico.

## Tipos de Tendencias y Cómo Interpretarlas

### Tendencia de Gol
```
Ejemplo: "Barcelona — Over 2.5 goles en 8/10 últimos partidos de Liga"
→ Interpretación: Alta frecuencia, mercado Over 2.5 viable
→ Confianza boost: +8%
```

### Tendencia de BTTS (Ambos Marcan)
```
Ejemplo: "Arsenal vs Chelsea — BTTS Sí en 6/7 últimos enfrentamientos"
→ Interpretación: Ambos equipos marcan consistentemente entre sí
→ Confianza boost: +10% (H2H tiene más peso)
```

### Tendencia de Localía
```
Ejemplo: "Real Madrid gana en casa: 9/10 últimos en La Liga"
→ Interpretación: Ventaja de localía muy fuerte
→ Confianza boost: +7%
```

### Tendencia Negativa (evitar)
```
Ejemplo: "PSG — Under 2.5 en 5/6 últimos"
→ Interpretación: PSG está anotando menos, tendencia defensiva
→ Acción: NO apostar Over 2.5 en sus partidos
```

## Pesos de las Tendencias

| Tipo de Tendencia | Peso en Confianza | Razón |
|-------------------|-------------------|-------|
| H2H (enfrentamientos directos) | 35% | Los equipos tienen historial entre sí |
| Forma reciente (5-10 partidos) | 30% | Refleja el estado actual |
| Localía/Visitante | 20% | Factor contextual importante |
| Estadísticas avanzadas (xG) | 15% | Datos objetivos de rendimiento |

## Errores Comunes en Análisis

### ❌ Muestra pequeña
- "Ganó 3 de 3" suena bien, pero 3 partidos no son muestra suficiente.
- **Mínimo**: 5 partidos para tendencia, 7+ para confianza alta.

### ❌ Ignorar el contexto
- Un equipo puede estar en racha porque jugó contra equipos débiles.
- Siempre considerar la CALIDAD del rival.

### ❌ Tendencia sin direction
- "Empató 3 de 5" no te dice nada útil. ¿Es buen dato o malo?
- Las tendencias deben ser.directionales: "Gana", "Anota 2+", "BTTS Sí".

### ❌ Overfitting
- Si encontraste una tendencia perfecta en 100 partidos, probablemente es casualidad.
- Las tendencias más confiables son las simples y consistentes.

## Factores Contextuales a Evaluar

### 1. Motivación
- ¿Es final, semifinal, liguilla, o fecha regular?
- ¿El equipo necesita puntos para no descender/o clasificar?
- **Impacto**: ±10% en confianza

### 2. Lesiones
- ¿Falta el goleador principal? El titular del mediocampo?
- **Impacto**: -5% a -20% según importancia del jugador

### 3. Rivalidad (Derbies)
- En clásicos, las estadísticas pesan menos. El factor emocional domina.
- **Impacto**: Reducir confianza un 10-15% automáticamente

### 4. Fatiga / Calendario
- ¿El equipo jugó hace 3 días? ¿Tiene Champions la próxima semana?
- **Impacto**: -5% si hay fatiga evidente

### 5. Clima / Cancha
- Lluvia, calor extremo, altura (en Sudamérica) afectan el juego.
- **Impacto**: -3% a -8% según severidad

## Flujo de Análisis Recomendado

1. **Identificar el partido** → Equipos, liga, fecha/hora
2. **Buscar tendencias** → 365scores, SofaScore, historial H2H
3. **Filtrar mercados** → ¿Cuáles cumplen los 4 filtros?
4. **Calcular confianza** → Usar la fórmula
5. **Evaluar contexto** → Lesiones, motivación, rivalidad
6. **Decidir publicar** → ¿Confianza ≥ 65%? ¿Cuota ≥ 1.70?
7. **Generar pronóstico** → Formato estándar AppMillonaria
