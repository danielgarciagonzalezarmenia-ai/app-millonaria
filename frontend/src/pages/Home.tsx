import { Link } from 'react-router-dom'
import {
  ArrowUpRight,
  Fire,
  Sword,
  ShieldCheck,
  ChartLineUp,
  TrendUp,
} from '@phosphor-icons/react'
import { useSession } from '../lib/auth'
import { useReveal } from '../lib/useReveal'
import { PredictionCard } from '../components/PredictionCard'
import { DEMO_PREDICTIONS } from '../lib/demo'

const features = [
  {
    icon: Fire,
    title: 'Tendencias calientes',
    body: 'Filtramos las tendencias marcadas con llama en la fuente: solo las que corroboran ambos lados del partido.',
    grad: 'linear-gradient(135deg,#f59e0b,#fbbf24)',
  },
  {
    icon: Sword,
    title: 'Mercados globales',
    body: 'Ambos marcan, más de 2.5, gana o empata. Nada de apuestas sueltas: mercados que involucran a los dos equipos.',
    grad: 'linear-gradient(135deg,#6f5bff,#9a4dff)',
  },
  {
    icon: ShieldCheck,
    title: 'Cuota 1.70+',
    body: 'Solo publicamos pronósticos con cuota mínima establecida, para mantener el valor real de cada jugada.',
    grad: 'linear-gradient(135deg,#10b981,#34d399)',
  },
]

const stats = [
  { num: '1.70+', lbl: 'Cuota mínima' },
  { num: '2', lbl: 'Lados que corroboran' },
  { num: '24/7', lbl: 'Scraping automático' },
  { num: '+180', lbl: 'Ligas cubiertas' },
]

export function Home() {
  const { user, signInWithGoogle } = useSession()
  const reveal = useReveal<HTMLElement>()

  const featured = DEMO_PREDICTIONS[0]

  return (
    <div className="container">
      <section className="hero">
        <div>
          <span className="eyebrow-pill reveal visible">
            <TrendUp size={13} weight="bold" style={{ color: 'var(--brand-2)' }} />
            Datos + tendencias de partido
          </span>
          <h1 className="title-display" style={{ marginTop: '1.3rem' }}>
            Pronósticos construidos sobre{' '}
            <span className="title-gradient">tendencias reales</span>
          </h1>
          <p className="subtitle">
            Analizamos en vivo las tendencias destacadas de cada partido — las que
            llevan llama — y publicamos solo las mejores: ambos marcan, más de 2.5
            goles, victorias y dobles oportunidades con cuota desde 1.70.
          </p>
          <div className="hero-cta">
            <Link to="/pronosticos" className="btn btn-primary btn-lg">
              Ver pronósticos de hoy
              <span className="btn-icon">
                <ArrowUpRight size={15} weight="bold" />
              </span>
            </Link>
            {!user && (
              <button className="btn btn-ghost btn-lg" onClick={() => void signInWithGoogle()}>
                Entrar con Google
              </button>
            )}
          </div>

          <div className="stats-bar reveal" style={{ marginTop: '3.4rem' }}>
            {stats.map((s) => (
              <div key={s.lbl} className="bezel">
                <div className="core stat">
                  <div className="num title-gradient">{s.num}</div>
                  <div className="lbl">{s.lbl}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="live-card reveal">
          <div className="flex gap-2" style={{ alignItems: 'center', marginBottom: '1rem' }}>
            <span className="live-dot" />
            <span
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.14em',
                color: 'var(--text-soft)',
              }}
            >
              Pronóstico destacado de hoy
            </span>
          </div>
          <PredictionCard prediction={featured} />
          <div className="bezel" style={{ marginTop: '1.25rem' }}>
            <div className="core" style={{ padding: '1.1rem 1.3rem' }}>
              <div className="between">
                <span className="flex gap-2" style={{ alignItems: 'center' }}>
                  <ChartLineUp size={17} weight="bold" style={{ color: 'var(--cyan)' }} />
                  <span className="text-soft" style={{ fontSize: '0.9rem' }}>
                    Actualizado automáticamente
                  </span>
                </span>
                <Link to="/pronosticos" className="btn btn-ghost btn-sm">
                  Ver todos
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }} ref={reveal}>
        <div className="between" style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: 'clamp(1.8rem, 3.4vw, 2.5rem)' }}>
            Por qué confiar
          </h2>
          <span className="eyebrow-pill">Metodología</span>
        </div>

        <div className="bento">
          {features.map((f) => (
            <div key={f.title} className={`bento-normal reveal`}>
              <div className="bezel" style={{ height: '100%' }}>
                <div className="core" style={{ padding: '1.9rem 1.8rem', height: '100%' }}>
                  <span
                    className="feature-ic"
                    style={{ background: f.grad, boxShadow: '0 12px 32px -10px rgba(0,0,0,.6)' }}
                  >
                    <f.icon size={22} weight="bold" />
                  </span>
                  <h3 style={{ fontSize: '1.2rem', marginBottom: '0.6rem' }}>{f.title}</h3>
                  <p className="text-soft" style={{ fontSize: '0.95rem', lineHeight: 1.65 }}>
                    {f.body}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}