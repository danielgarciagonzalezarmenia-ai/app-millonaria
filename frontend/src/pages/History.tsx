import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { CalendarBlank } from '@phosphor-icons/react'
import { api, type Prediction } from '../lib/api'
import { useSession } from '../lib/auth'
import { configReady } from '../lib/firebase'
import { DEMO_HISTORY } from '../lib/demo'
import { PredictionCard } from '../components/PredictionCard'
import { useReveal } from '../lib/useReveal'

function dayKey(iso: string): string {
  return new Date(iso).toLocaleDateString('es-AR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export function History() {
  const { premium } = useSession()
  const [items, setItems] = useState<Prediction[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [isDemo, setIsDemo] = useState(false)
  const reveal = useReveal<HTMLDivElement>()

  useEffect(() => {
    setIsDemo(!configReady)
    void (async () => {
      try {
        setItems(await api.getHistory())
      } catch (err) {
        if (!configReady) {
          setIsDemo(true)
          setItems(DEMO_HISTORY)
        } else {
          setError(err instanceof Error ? err.message : 'No se pudo cargar el historial.')
        }
      } finally {
        setLoading(false)
      }
    })()
  }, [premium])

  const grouped = useMemo(() => {
    const map = new Map<string, Prediction[]>()
    for (const p of items) {
      const k = dayKey(p.created_at)
      const arr = map.get(k) ?? []
      arr.push(p)
      map.set(k, arr)
    }
    return Array.from(map.entries())
  }, [items])

  return (
    <div className="container section" ref={reveal}>
      <div className="between" style={{ marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <span className="eyebrow-pill">
            <CalendarBlank size={13} weight="bold" />
            Días anteriores
          </span>
          <h1 className="title-display" style={{ fontSize: 'clamp(1.8rem, 3vw, 2.6rem)', marginTop: '1rem' }}>
            Historial de pronósticos
          </h1>
          <p className="subtitle" style={{ fontSize: '0.98rem' }}>
            {items.length} guardados · los premium solo se ven con suscripción activa
          </p>
        </div>
        {isDemo && <span className="badge badge-mute">vista de demostración</span>}
      </div>

      {loading && <p className="text-soft">Cargando historial…</p>}
      {error && (
        <div className="bezel" style={{ padding: 0 }}>
          <div className="core" style={{ padding: '1.5rem' }}>
            <p className="text-soft">{error}</p>
          </div>
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="bezel" style={{ padding: 0 }}>
          <div className="core" style={{ padding: '2rem', textAlign: 'center' }}>
            <p className="text-soft">Aún no hay pronósticos guardados de días anteriores.</p>
            <p className="text-mute" style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
              Cada día los pronósticos del día se archivan aquí.
            </p>
          </div>
        </div>
      )}

      {!loading && !error && grouped.map(([day, preds]) => (
        <section key={day} style={{ marginBottom: '2.5rem' }}>
          <h2
            style={{
              fontSize: '1rem',
              color: 'var(--text-soft)',
              textTransform: 'capitalize',
              letterSpacing: '0.02em',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            <span className="live-dot" style={{ width: 6, height: 6 }} />
            {day}
          </h2>
          <div className="bento">
            {preds.map((p, i) => {
              const locked = p.premium && !premium
              return (
                <div
                  key={`${p.match_id}_${p.selection}`}
                  className="bento-normal"
                  style={{ position: 'relative' }}
                >
                  <PredictionCard prediction={p} locked={p.premium && !premium} featured={i === 0} />
                  {locked && (
                    <div className="lock-scrim">
                      <div className="lock-shell">
                        <div className="bezel" style={{ padding: 0 }}>
                          <div className="core" style={{ padding: '1.6rem', textAlign: 'center' }}>
                            <p style={{ fontWeight: 700, fontFamily: 'var(--font-display)', marginBottom: '0.4rem' }}>
                              Pronóstico premium
                            </p>
                            <p className="text-soft" style={{ fontSize: '0.88rem', marginBottom: '1rem' }}>
                              Desbloquea el historial premium con tu suscripción.
                            </p>
                            <Link to="/premium" className="btn btn-primary btn-sm">
                              Ver planes
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </section>
      ))}
    </div>
  )
}