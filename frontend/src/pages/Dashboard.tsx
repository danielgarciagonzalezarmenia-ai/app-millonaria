import { ArrowsClockwise, ShieldCheck } from '@phosphor-icons/react'
import { useSession } from '../lib/auth'

export function Dashboard() {
  const { user, premium, premiumUntil, admin, signInWithGoogle, refreshSession } = useSession()

  if (!user) {
    return (
      <div className="container section" style={{ textAlign: 'center' }}>
        <h1 className="title-display" style={{ fontSize: 'clamp(1.8rem, 3vw, 2.4rem)' }}>
          Tu cuenta
        </h1>
        <p className="subtitle" style={{ marginInline: 'auto', marginTop: '1rem' }}>
          Entra con tu Google para ver tu estado premium.
        </p>
        <div className="mt-3">
          <button className="btn btn-primary btn-lg" onClick={() => void signInWithGoogle()}>
            Entrar con Google
          </button>
        </div>
      </div>
    )
  }

  const until = premiumUntil
    ? new Date(premiumUntil).toLocaleDateString('es', { year: 'numeric', month: 'long', day: 'numeric' })
    : null

  return (
    <div className="container section">
      <div style={{ maxWidth: 560, marginInline: 'auto' }}>
        <div className="bezel">
          <div className="core" style={{ padding: '2.25rem' }}>
            <div className="between" style={{ marginBottom: '1.5rem' }}>
              <h1 className="title-display" style={{ fontSize: '1.6rem' }}>
                Mi cuenta
              </h1>
              {admin && <span className="badge badge-mute">Admin</span>}
            </div>

            <div className="flex gap-3" style={{ alignItems: 'center', marginBottom: '1.5rem' }}>
              <span className="avatar" style={{ width: 54, height: 54 }}>
                {user.photoURL ? (
                  <img src={user.photoURL} alt={user.displayName ?? 'Cuenta'} />
                ) : (
                  <span style={{ display: 'grid', placeItems: 'center', width: '100%', height: '100%', fontSize: '1.1rem', fontWeight: 700 }}>
                    {(user.displayName ?? user.email ?? 'U').slice(0, 1)}
                  </span>
                )}
              </span>
              <div>
                <p style={{ fontWeight: 600 }}>{user.displayName ?? 'Usuario'}</p>
                <p className="text-soft" style={{ fontSize: '0.88rem' }}>{user.email}</p>
              </div>
            </div>

            <div className="bezel" style={{ padding: 0 }}>
              <div className="core" style={{ padding: '1.2rem', borderRadius: 'var(--radius-md)' }}>
                <div className="between">
                <span className="flex gap-2" style={{ alignItems: 'center' }}>
                  <ShieldCheck size={16} weight="duotone" style={{ color: 'var(--cyan)' }} />
                  <span className="text-soft">Suscripción</span>
                </span>
                {premium ? (
                  <span className="badge badge-premium">Premium activo</span>
                ) : (
                  <span className="badge badge-mute">Gratis</span>
                )}
              </div>
              {premium && (
                <p className="text-mute" style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>
                  Válido hasta: <span className="mono">{until ?? '—'}</span>
                </p>
              )}
              </div>
            </div>

            <button
              className="btn btn-outline"
              style={{ marginTop: '1.5rem', width: '100%' }}
              onClick={() => void refreshSession()}
            >
              <ArrowsClockwise size={15} weight="bold" />
              Refrescar estado premium
            </button>
            <p className="text-mute" style={{ marginTop: '0.75rem', fontSize: '0.78rem' }}>
              Si acabas de pagar, refresca aquí para actualizar tu estado.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}