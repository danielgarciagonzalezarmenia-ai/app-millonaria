import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { LockKey } from '@phosphor-icons/react'
import { api, type Prediction } from '../lib/api'
import { useSession } from '../lib/auth'
import { configReady } from '../lib/firebase'
import { DEMO_PREDICTIONS } from '../lib/demo'
import { PredictionCard } from '../components/PredictionCard'
import { useReveal } from '../lib/useReveal'

export function Predictions() {
  const { premium } = useSession()
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [isDemo, setIsDemo] = useState(false)
  const reveal = useReveal<HTMLDivElement>()

  useEffect(() => {
    setIsDemo(!configReady)
    void (async () => {
      try {
        setPredictions(await api.getToday())
      } catch (err) {
        if (!configReady) {
          // Vistazo sin backend/Firebase: datos de ejemplo reales del scraper.
          setIsDemo(true)
          setPredictions(DEMO_PREDICTIONS)
        } else {
          setError(err instanceof Error ? err.message : 'No se pudieron cargar los pronósticos.')
        }
      } finally {
        setLoading(false)
      }
    })()
  }, [premium])

  const freeCount = predictions.filter((p) => !p.premium).length
  const premiumCount = predictions.length - freeCount

  return (
    <div className="container section" ref={reveal}>
      <div className="between" style={{ marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <span className="eyebrow-pill">
            <LockKey size={13} weight="bold" />
            Analizados hoy
          </span>
          <h1 className="title-display" style={{ fontSize: 'clamp(1.8rem, 3vw, 2.6rem)', marginTop: '1rem' }}>
            Pronósticos del día
          </h1>
          <p className="subtitle" style={{ fontSize: '0.98rem' }}>
            {freeCount} gratis hoy · {premiumCount} premium
            {!premium && ' · entra con Google para ver los premium'}
            {premium && ' · suscripción activa'}
          </p>
        </div>
        {isDemo && <span className="badge badge-mute">vista de demostración</span>}
      </div>

      {loading && <p className="text-soft">Cargando pronósticos…</p>}
      {error && (
        <div className="bezel" style={{ padding: 0 }}>
          <div className="core" style={{ padding: '1.5rem' }}>
            <p className="text-soft">{error}</p>
            <p className="text-mute" style={{ fontSize: '0.85rem', marginTop: '0.6rem' }}>
              Comprueba que el backend esté corriendo y las claves de Firebase estén configuradas.
            </p>
          </div>
        </div>
      )}

      {!loading && !error && predictions.length === 0 && (
        <div className="bezel" style={{ padding: 0 }}>
          <div className="core" style={{ padding: '2rem', textAlign: 'center' }}>
            <p className="text-soft">Aún no hay pronósticos publicados para hoy.</p>
            <p className="text-mute" style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
              El scraper corre cada día para alimentar esta sección.
            </p>
          </div>
        </div>
      )}

      {!loading && !error && predictions.length > 0 && (
        <div className="bento">
          {predictions.map((p, i) => {
            const isPremiumPred = p.premium
            const locked = isPremiumPred && !premium
            return (
              <div
                key={`${p.match_id}_${p.selection}`}
                className={`${i === 0 ? 'bento-featured' : 'bento-normal'} reveal`}
                style={{ position: 'relative' }}
              >
                <PredictionCard prediction={p} locked={locked} featured={i === 0} />
                {locked && (
                  <div className="lock-scrim">
                    <div className="lock-shell">
                      <div className="bezel" style={{ padding: 0 }}>
                        <div className="core" style={{ padding: '1.6rem', textAlign: 'center' }}>
                        <p style={{ fontWeight: 700, fontFamily: 'var(--font-display)', marginBottom: '0.4rem' }}>
                          Pronóstico premium
                        </p>
                        <p className="text-soft" style={{ fontSize: '0.88rem', marginBottom: '1rem' }}>
                          Hazte premium para ver la cuota y la confianza exacta.
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
      )}

      {!premium && (
        <div className="bezel bezel-premium" style={{ marginTop: '3rem' }}>
          <div className="core" style={{ padding: '2rem', textAlign: 'center' }}>
            <h3 style={{ marginBottom: '0.5rem' }}>Desbloquea todos los pronósticos</h3>
            <p className="text-soft" style={{ marginBottom: '1.2rem' }}>
              Los pronósticos premium incluyen cuota, confianza y el detalle de las
              tendencias que los respaldan.
            </p>
            <Link to="/premium" className="btn btn-primary">
              Ir a Premium
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}