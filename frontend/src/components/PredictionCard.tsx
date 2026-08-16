import {
  Fire,
  LockKey,
  ChartLineUp,
  ShieldChevron,
} from '@phosphor-icons/react'
import type { Prediction } from '../lib/api'

interface Props {
  prediction: Prediction
  locked?: boolean
  featured?: boolean
}

const GRADIENTS = [
  'linear-gradient(135deg,#6f5bff,#9a4dff)',
  'linear-gradient(135deg,#0ea5e9,#2fd6e9)',
  'linear-gradient(135deg,#d94fb8,#f472b6)',
  'linear-gradient(135deg,#f59e0b,#fbbf24)',
  'linear-gradient(135deg,#10b981,#34d399)',
]

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase()
}

function gradientFor(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) >>> 0
  return GRADIENTS[hash % GRADIENTS.length]
}

export function PredictionCard({ prediction, locked = false, featured = false }: Props) {
  const confidence = Math.round(prediction.confidence * 100)
  const home = prediction.home_team || 'Local'
  const away = prediction.away_team || 'Visitante'

  return (
    <div className={`bezel ${prediction.premium ? 'bezel-premium' : ''}`}>
      <div className={`core pred-card ${featured ? 'pred-card-featured' : ''}`}>
        <div className="pred-head">
          <span className="league">{prediction.league}</span>
          <span className="fire-chip">
            <Fire size={13} weight="fill" /> caliente
          </span>
        </div>

        <div className="flex" style={{ flexDirection: 'column', gap: '0.45rem' }}>
          <div className="team-row">
            <span className="team-badge" style={{ background: gradientFor(home), boxShadow: '0 8px 22px -8px rgba(124,107,255,.5)' }}>
              {initials(home)}
            </span>
            <span className="team-name">{home}</span>
          </div>
          <div className="team-vs" style={{ paddingLeft: '0.7rem' }}>vs</div>
          <div className="team-row">
            <span className="team-badge" style={{ background: gradientFor(away), boxShadow: '0 8px 22px -8px rgba(47,214,233,.5)' }}>
              {initials(away)}
            </span>
            <span className="team-name">{away}</span>
          </div>
        </div>

        <div className="flex gap-2" style={{ alignItems: 'center', flexWrap: 'wrap' }}>
          <span className="market-tag">
            <ChartLineUp size={15} weight="bold" />
            {prediction.market}
          </span>
          {prediction.premium && (
            <span className="basis-chip">
              <ShieldChevron size={13} weight="bold" />
              Premium
            </span>
          )}
        </div>

        {prediction.basis && prediction.basis.length > 0 && (
          <div className="trend-basis">
            {prediction.basis.slice(0, 2).map((b, i) => (
              <span key={i} className="basis-chip">
                <Fire size={11} weight="fill" style={{ color: 'var(--amber)' }} />
                {b.label}
              </span>
            ))}
          </div>
        )}

        <div>
          <div className="between" style={{ marginBottom: '0.45rem' }}>
            <span className="odds-label" style={{ textTransform: 'none', letterSpacing: '0' }}>
              Confianza
            </span>
            <span className="mono" style={{ color: 'var(--text-soft)', fontSize: '0.85rem', fontWeight: 600 }}>
              {locked ? '•••' : `${confidence}%`}
            </span>
          </div>
          <div className="conf-track">
            <div
              className="conf-fill"
              style={{ width: locked ? '20%' : `${confidence}%`, opacity: locked ? 0.4 : 1 }}
            />
          </div>
        </div>

        <div className="odds-row">
          <span className="odds-label">Cuota</span>
          <span className="odds-chip">{locked ? '—' : prediction.odds.toFixed(2)}</span>
        </div>

        {locked && (
          <div className="lock-scrim">
            <div className="bezel btn-primary" style={{ width: '82%' }}>
              <div className="core" style={{ borderRadius: 'calc(1.75rem - 3px)', padding: '1 1', background: 'rgba(12,12,18,.95)' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.8rem', padding: '1.6rem 1.2rem', textAlign: 'center' }}>
                  <span
                    style={{
                      width: 46, height: 46, borderRadius: 999, display: 'grid', placeItems: 'center',
                      background: 'var(--grad-brand)', color: '#fff', boxShadow: '0 14px 36px -10px rgba(154,77,255,.7)',
                    }}
                  >
                    <LockKey size={22} weight="bold" />
                  </span>
                  <div>
                    <p style={{ fontWeight: 700, fontFamily: 'var(--font-display)', fontSize: '1.05rem', marginBottom: '0.3rem' }}>
                      Contenido premium
                    </p>
                    <p className="text-soft" style={{ fontSize: '0.85rem' }}>
                      {prediction.market} — cuota y confianza exacta al activar Premium.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}