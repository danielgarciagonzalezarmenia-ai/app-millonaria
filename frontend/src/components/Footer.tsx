import { Link } from 'react-router-dom'

export function Footer() {
  return (
    <footer
      style={{
        borderTop: '1px solid var(--border)',
        marginTop: '5rem',
        background: 'linear-gradient(180deg, rgba(17,17,24,0) 0%, rgba(13,13,18,1) 100%)',
      }}
    >
      <div className="container" style={{ padding: '3rem 0', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
        <Link to="/" className="logo" style={{ fontSize: '0.95rem' }}>
          App Millonaria
        </Link>
        <p className="text-mute" style={{ fontSize: '0.85rem' }}>
          Los pronósticos son informativos. Apuesta con responsabilidad.
        </p>
      </div>
    </footer>
  )
}