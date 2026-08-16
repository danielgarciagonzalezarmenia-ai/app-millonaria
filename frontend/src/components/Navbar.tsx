import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  SignOut,
  ChartLineUp,
  House,
  Crown,
  List,
  X,
  ClockCounterClockwise,
  Gear,
} from '@phosphor-icons/react'
import { useSession } from '../lib/auth'

const baseLinks = [
  { to: '/', label: 'Inicio', icon: House, end: true },
  { to: '/pronosticos', label: 'Pronósticos', icon: ChartLineUp },
  { to: '/historial', label: 'Historial', icon: ClockCounterClockwise },
  { to: '/premium', label: 'Premium', icon: Crown },
]

export function Navbar() {
  const { user, premium, admin, loading, signInWithGoogle, signOutUser } = useSession()
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()

  const links = admin
    ? [...baseLinks, { to: '/admin', label: 'Admin', icon: Gear, end: false }]
    : baseLinks

  const handleSignOut = () => {
    setOpen(false)
    void signOutUser().then(() => navigate('/'))
  }

  return (
    <>
      <header className="nav-island">
        <div className="nav-inner">
          <NavLink to="/" className="logo" onClick={() => setOpen(false)}>
            <span style={{ letterSpacing: '-0.01em' }}>
              App<span className="title-gradient">Millonaria</span>
            </span>
            {premium && (
              <span
                className="flex gap-1"
                style={{
                  alignItems: 'center',
                  fontSize: '0.62rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.12em',
                  color: 'var(--amber)',
                  background: 'rgba(245,181,68,.12)',
                  border: '1px solid rgba(245,181,68,.3)',
                  padding: '0.2rem 0.6rem',
                  borderRadius: 999,
                }}
              >
                <Crown size={11} weight="fill" /> Premium
              </span>
            )}
          </NavLink>

          <nav className="nav-links desktop-only">
            {links.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `nav-link ${isActive ? 'active' : ''}`
                }
              >
                <Icon size={15} weight="regular" />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="flex gap-2" style={{ alignItems: 'center' }}>
            {loading ? (
              <span className="text-mute" style={{ fontSize: '0.85rem' }}>
                …
              </span>
            ) : user ? (
              <>
                <NavLink to="/perfil" title={user.email ?? 'Mi cuenta'}>
                  <span className="avatar">
                    {user.photoURL ? (
                      <img src={user.photoURL} alt={user.displayName ?? 'Cuenta'} />
                    ) : (
                      <span style={{ fontSize: '0.8rem', fontWeight: 700 }}>
                        {(user.displayName ?? user.email ?? 'U').slice(0, 1).toUpperCase()}
                      </span>
                    )}
                  </span>
                </NavLink>
                <button
                  className="btn btn-ghost btn-sm desktop-only"
                  onClick={handleSignOut}
                >
                  <SignOut size={15} />
                  Salir
                </button>
              </>
            ) : (
              <button className="btn btn-primary btn-sm" onClick={() => void signInWithGoogle()}>
                Entrar
              </button>
            )}
            <button
              className="btn btn-ghost btn-sm"
              style={{ display: 'grid', placeItems: 'center', padding: '0.5rem' }}
              onClick={() => setOpen((v) => !v)}
              aria-label="Menú"
            >
              {open ? <X size={20} /> : <List size={20} />}
            </button>
          </div>
        </div>
      </header>

      {/* Menú móvil */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 99,
          background: 'rgba(6,6,8,.86)',
          backdropFilter: 'blur(24px)',
          WebkitBackdropFilter: 'blur(24px)',
          display: open ? 'grid' : 'none',
          placeItems: 'center',
          padding: '2rem',
        }}
      >
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'center' }}>
          {links.map(({ to, label, icon: Icon, end }, i) => (
            <div
              key={to}
              style={open ? { width: '100%' } : undefined}
            >
              <NavLink
                to={to}
                end={end}
                className={({ isActive }) =>
                  `nav-link ${isActive ? 'active' : ''}`
                }
                style={{
                  fontSize: '1.6rem',
                  padding: '0.9rem 2rem',
                  borderRadius: '1rem',
                  transitionDelay: open ? `${80 + i * 55}ms` : undefined,
                }}
                onClick={() => setOpen(false)}
              >
                <Icon size={22} />
                {label}
              </NavLink>
            </div>
          ))}
        </nav>
      </div>
    </>
  )
}
