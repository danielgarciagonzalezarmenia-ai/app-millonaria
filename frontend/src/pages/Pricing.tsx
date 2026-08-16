import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Check, Lightning, LockKey } from '@phosphor-icons/react'
import { api } from '../lib/api'
import { useSession } from '../lib/auth'

const features = [
  'Todos los pronósticos del día',
  'Cuota y confianza exacta',
  'Detalle de tendencias que respaldan',
  'Activación automática del pago',
]

export function Pricing() {
  const { user, premium, signInWithGoogle } = useSession()
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const buy = async () => {
    setError(null)
    if (!user) {
      await signInWithGoogle()
      return
    }
    setProcessing(true)
    try {
      const intent = await api.purchaseIntent()
      // Abrimos el link de pago de TipsterPage con la referencia única.
      window.location.href = intent.payment_url
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al iniciar el pago.')
      setProcessing(false)
    }
  }

  if (premium) {
    return (
      <div className="container section" style={{ textAlign: 'center' }}>
        <span className="eyebrow-pill">
          <LockKey size={13} weight="bold" style={{ color: 'var(--amber)' }} />
          Ya eres premium
        </span>
        <h1 className="title-display" style={{ fontSize: 'clamp(1.8rem, 3vw, 2.4rem)', marginTop: '1rem' }}>
          Tu suscripción está <span className="title-gradient">activa</span>
        </h1>
        <p className="subtitle" style={{ marginInline: 'auto', marginTop: '1rem' }}>
          Disfruta de todos los pronósticos con cuota, confianza y tendencias.
        </p>
        <div className="flex gap-2" style={{ justifyContent: 'center', marginTop: '2rem' }}>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/pronosticos')}>
            Ver pronósticos premium
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container section">
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <span className="eyebrow-pill">
          <Lightning size={13} weight="bold" style={{ color: 'var(--amber)' }} />
          Suscripción
        </span>
        <h1 className="title-display" style={{ marginTop: '1rem' }}>
          Hazte <span className="title-gradient">Premium</span>
        </h1>
        <p className="subtitle" style={{ marginInline: 'auto', marginTop: '1rem' }}>
          Pago único por mes vía link de TipsterPage. Al confirmarse el pago,
          tu cuenta se activa automáticamente.
        </p>
      </div>

      <div className="bezel bezel-premium" style={{ maxWidth: 420, marginInline: 'auto' }}>
        <div className="core" style={{ padding: '2.25rem', textAlign: 'center' }}>
          <span className="badge badge-premium" style={{ marginBottom: '1.25rem' }}>
            <Lightning size={12} weight="fill" style={{ color: 'var(--amber)' }} />
            Premium Mensual
          </span>
          <div style={{ fontSize: '3.2rem', fontWeight: 800, letterSpacing: '-0.045em', fontFamily: 'var(--font-display)' }}>
            <span className="title-gradient">$9</span>
            <span className="title-gradient">.99</span>
            <span className="text-mute" style={{ fontSize: '1rem', fontWeight: 500 }}> / mes</span>
          </div>

          <ul
            style={{
              listStyle: 'none',
              padding: 0,
              margin: '1.75rem 0',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.85rem',
              textAlign: 'left',
            }}
          >
            {features.map((f) => (
              <li key={f} className="flex gap-2" style={{ alignItems: 'center' }}>
                <span
                  style={{
                    width: 20, height: 20, borderRadius: 999, display: 'grid', placeItems: 'center',
                    background: 'rgba(52,211,153,.12)', color: 'var(--green)',
                  }}
                >
                  <Check size={12} weight="bold" />
                </span>
                <span style={{ fontSize: '0.95rem' }}>{f}</span>
              </li>
            ))}
          </ul>

          <button
            className="btn btn-primary btn-lg"
            style={{ width: '100%' }}
            onClick={() => void buy()}
            disabled={processing}
          >
            <LockKey size={16} weight="bold" />
            {processing ? 'Preparando pago…' : user ? 'Pagar ahora' : 'Entrar y pagar'}
          </button>
          {error && (
            <p className="text-soft" style={{ marginTop: '1rem', fontSize: '0.88rem' }}>
              {error}
            </p>
          )}
          <p className="text-mute" style={{ marginTop: '1rem', fontSize: '0.78rem' }}>
            Al pagar serás redirigido a TipsterPage. Recuerda entrar con el mismo
            Google con el que estás registrado.
          </p>
        </div>
      </div>
    </div>
  )
}