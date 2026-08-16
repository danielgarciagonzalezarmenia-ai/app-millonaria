import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../lib/auth'
import { api, type Prediction } from '../lib/api'
import { Trash, Pencil, Plus, X, Warning } from '@phosphor-icons/react'

const MARKETS = [
  { value: 'home_win', label: 'Gana el local' },
  { value: 'away_win', label: 'Gana el visitante' },
  { value: 'btts', label: 'Ambos marcan' },
  { value: 'over_2_5', label: 'Más de 2.5 goles' },
  { value: 'home_or_draw', label: 'Local gana o empata (1X)' },
  { value: 'away_or_draw', label: 'Visitante gana o empata (X2)' },
]

function selectionFromMarket(mt: string): string {
  const map: Record<string, string> = {
    home_win: 'local_gana',
    away_win: 'visitante_gana',
    btts: 'ambos_marcan',
    over_2_5: 'mas_de_2_5',
    home_or_draw: 'local_gana_o_empata',
    away_or_draw: 'visitante_gana_o_empata',
  }
  return map[mt] || 'other'
}

function marketLabel(mt: string): string {
  return MARKETS.find((m) => m.value === mt)?.label || mt
}

interface FormState {
  match_id: string
  league: string
  home_team: string
  away_team: string
  kickoff: string
  market_type: string
  odds: string
  confidence: string
  basis_label: string
  premium: boolean
}

const EMPTY_FORM: FormState = {
  match_id: '',
  league: '',
  home_team: '',
  away_team: '',
  kickoff: '',
  market_type: 'home_win',
  odds: '',
  confidence: '0.8',
  basis_label: '',
  premium: false,
}

export function Admin() {
  const { user, admin, loading } = useSession()
  const navigate = useNavigate()
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [loadingList, setLoadingList] = useState(true)
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!loading && (!user || !admin)) {
      navigate('/')
    }
  }, [user, admin, loading, navigate])

  useEffect(() => {
    if (admin) {
      loadPredictions()
    }
  }, [admin])

  async function loadPredictions() {
    setLoadingList(true)
    try {
      setPredictions(await api.adminListPredictions())
    } catch {
      setError('Error al cargar pronósticos')
    }
    setLoadingList(false)
  }

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) {
    const { name, value, type } = e.target
    const checked = (e.target as HTMLInputElement).checked
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  function handleEdit(pred: Prediction) {
    setEditingId(`${pred.match_id}_${pred.selection}`)
    setForm({
      match_id: pred.match_id,
      league: pred.league,
      home_team: pred.home_team,
      away_team: pred.away_team,
      kickoff: pred.kickoff ? pred.kickoff.slice(0, 16) : '',
      market_type: pred.market_type,
      odds: String(pred.odds),
      confidence: String(pred.confidence),
      basis_label: pred.basis[0]?.value || '',
      premium: pred.premium,
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function handleCancel() {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setError('')
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setSaving(true)

    const match_id = form.match_id.trim() || `${form.home_team.trim()}_vs_${form.away_team.trim()}`.toLowerCase().replace(/\s+/g, '_')
    const selection = selectionFromMarket(form.market_type)

    const pred: Omit<Prediction, 'created_at'> = {
      match_id,
      league: form.league.trim(),
      home_team: form.home_team.trim(),
      away_team: form.away_team.trim(),
      kickoff: form.kickoff ? new Date(form.kickoff).toISOString() : null,
      market: marketLabel(form.market_type),
      market_type: form.market_type,
      selection,
      odds: parseFloat(form.odds) || 2.0,
      confidence: parseFloat(form.confidence) || 0.8,
      basis: form.basis_label.trim()
        ? [{ label: form.basis_label.trim(), side: 'for', value: form.basis_label.trim() }]
        : [],
      premium: form.premium,
    }

    try {
      if (editingId) {
        await api.adminUpdatePrediction(editingId, pred)
      } else {
        await api.adminCreatePrediction(pred)
      }
      handleCancel()
      await loadPredictions()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al guardar'
      setError(msg)
    }
    setSaving(false)
  }

  async function handleDelete(docId: string) {
    if (!confirm('¿Borrar este pronóstico?')) return
    try {
      await api.adminDeletePrediction(docId)
      await loadPredictions()
    } catch {
      setError('Error al borrar')
    }
  }

  if (loading || !admin) return null

  return (
    <div className="page-container" style={{ maxWidth: 900, margin: '0 auto', padding: '2rem 1rem' }}>
      <h1 style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: '1.5rem' }}>
        Panel Admin
      </h1>

      {/* Formulario */}
      <form
        onSubmit={handleSubmit}
        style={{
          background: 'rgba(255,255,255,.04)',
          border: '1px solid rgba(255,255,255,.08)',
          borderRadius: '1rem',
          padding: '1.5rem',
          marginBottom: '2rem',
        }}
      >
        <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>
          {editingId ? 'Editar pronóstico' : 'Nuevo pronóstico'}
        </h2>

        {error && (
          <div
            style={{
              background: 'rgba(239,68,68,.12)',
              border: '1px solid rgba(239,68,68,.3)',
              borderRadius: '0.5rem',
              padding: '0.7rem 1rem',
              marginBottom: '1rem',
              color: '#f87171',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            <Warning size={16} /> {error}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
          <Field label="Liga" name="league" value={form.league} onChange={handleChange} placeholder="ej: Premier League" />
          <Field label="Fecha/hora (UTC)" name="kickoff" value={form.kickoff} onChange={handleChange} type="datetime-local" />
          <Field label="Equipo local" name="home_team" value={form.home_team} onChange={handleChange} placeholder="ej: River Plate" required />
          <Field label="Equipo visitante" name="away_team" value={form.away_team} onChange={handleChange} placeholder="ej: Boca Juniors" required />
          <Field label="Cuota decimal" name="odds" value={form.odds} onChange={handleChange} type="number" step="0.01" min="1.01" placeholder="ej: 2.50" required />
          <Field label="Confianza (0-1)" name="confidence" value={form.confidence} onChange={handleChange} type="number" step="0.05" min="0" max="1" />
        </div>

        <div style={{ marginTop: '0.8rem' }}>
          <label style={labelStyle}>Mercado</label>
          <select name="market_type" value={form.market_type} onChange={handleChange} style={inputStyle}>
            {MARKETS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>

        <div style={{ marginTop: '0.8rem' }}>
          <Field
            label="Base / Tendencia (opcional)"
            name="basis_label"
            value={form.basis_label}
            onChange={handleChange}
            placeholder="ej: River ganó 5/5 últimos partidos"
          />
        </div>

        <div style={{ marginTop: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <input
            type="checkbox"
            name="premium"
            checked={form.premium}
            onChange={handleChange}
            id="premium-check"
            style={{ accentColor: 'var(--brand)' }}
          />
          <label htmlFor="premium-check" style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Marcar como Premium
          </label>
        </div>

        <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
          <button type="submit" className="btn btn-primary btn-sm" disabled={saving} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            {saving ? 'Guardando…' : editingId ? 'Actualizar' : 'Crear'}
          </button>
          {editingId && (
            <button type="button" className="btn btn-ghost btn-sm" onClick={handleCancel} style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <X size={14} /> Cancelar
            </button>
          )}
        </div>
      </form>

      {/* Lista */}
      <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.8rem' }}>
        Pronósticos ({predictions.length})
      </h2>
      {loadingList ? (
        <p className="text-mute">Cargando…</p>
      ) : predictions.length === 0 ? (
        <p className="text-mute">No hay pronósticos. Crea uno arriba.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {predictions.map((p) => {
            const docId = `${p.match_id}_${p.selection}`
            return (
              <div
                key={docId}
                style={{
                  background: 'rgba(255,255,255,.03)',
                  border: '1px solid rgba(255,255,255,.06)',
                  borderRadius: '0.7rem',
                  padding: '0.8rem 1rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '0.5rem',
                  flexWrap: 'wrap',
                }}
              >
                <div style={{ flex: 1, minWidth: 200 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{p.league}</div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                    {p.home_team} vs {p.away_team}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                    {p.market} · cuota {p.odds} · conf {Math.round(p.confidence * 100)}%
                    {p.premium && (
                      <span style={{ marginLeft: '0.5rem', color: 'var(--amber)', fontWeight: 600 }}>
                        PREMIUM
                      </span>
                    )}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.3rem' }}>
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => handleEdit(p)}
                    title="Editar"
                    style={{ padding: '0.4rem' }}
                  >
                    <Pencil size={15} />
                  </button>
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => handleDelete(docId)}
                    title="Borrar"
                    style={{ padding: '0.4rem', color: '#f87171' }}
                  >
                    <Trash size={15} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function Field({
  label,
  name,
  value,
  onChange,
  type = 'text',
  placeholder,
  required,
  step,
  min,
  max,
}: {
  label: string
  name: string
  value: string
  onChange: React.ChangeEventHandler
  type?: string
  placeholder?: string
  required?: boolean
  step?: string
  min?: string | number
  max?: string | number
}) {
  return (
    <div>
      <label style={labelStyle}>{label}</label>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        step={step}
        min={min}
        max={max}
        style={inputStyle}
      />
    </div>
  )
}

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '0.75rem',
  fontWeight: 600,
  color: 'var(--text-secondary)',
  marginBottom: '0.3rem',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.6rem 0.8rem',
  borderRadius: '0.5rem',
  border: '1px solid rgba(255,255,255,.1)',
  background: 'rgba(255,255,255,.05)',
  color: 'var(--text)',
  fontSize: '0.85rem',
  outline: 'none',
}
