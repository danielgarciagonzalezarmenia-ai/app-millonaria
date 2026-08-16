import { auth } from './firebase'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface Prediction {
  match_id: string
  league: string
  home_team: string
  away_team: string
  kickoff: string | null
  market: string
  market_type: string
  selection: string
  odds: number
  confidence: number
  basis: { label: string; side: string; value: string }[]
  premium: boolean
  created_at: string
}

export interface ApiError extends Error {
  status: number
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let idToken: string | null = null
  if (auth?.currentUser) {
    idToken = await auth.currentUser.getIdToken(true)
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  }
  if (idToken) headers.Authorization = `Bearer ${idToken}`

  const res = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (!res.ok) {
    let detail = 'Error del servidor'
    try {
      const body = await res.json()
      detail = body.detail ?? detail
    } catch {
      /* ignore */
    }
    const err = new Error(detail) as ApiError
    err.status = res.status
    throw err
  }
  return res.json() as Promise<T>
}

export const api = {
  getPredictions: () => request<Prediction[]>('/api/predictions'),
  getToday: () => request<Prediction[]>('/api/predictions/today'),
  getHistory: () => request<Prediction[]>('/api/predictions/history'),
  getPrediction: (matchId: string, selection: string) =>
    request<Prediction>(`/api/predictions/${matchId}/${selection}`),
  me: () => request<{ uid: string; email: string | null; premium: boolean; premium_until?: string }>('/api/me', { method: 'POST' }),
  refreshClaims: () =>
    request<{ premium: boolean; premium_until?: string; admin: boolean }>('/api/refresh-claims', { method: 'POST' }),
  purchaseIntent: (productId = 'premium_monthly') =>
    request<{ order_id: string; payment_url: string; amount: number; currency: string }>(
      '/api/purchase/intent',
      { method: 'POST', body: JSON.stringify({ product_id: productId }) },
    ),

  // Admin
  adminListPredictions: () => request<Prediction[]>('/api/admin/predictions'),
  adminCreatePrediction: (pred: Omit<Prediction, 'created_at'>) =>
    request<Prediction>('/api/admin/predictions', {
      method: 'POST',
      body: JSON.stringify(pred),
    }),
  adminUpdatePrediction: (docId: string, pred: Omit<Prediction, 'created_at'>) =>
    request<Prediction>(`/api/admin/predictions/${docId}`, {
      method: 'PUT',
      body: JSON.stringify(pred),
    }),
  adminDeletePrediction: (docId: string) =>
    request<{ detail: string; doc_id: string }>(`/api/admin/predictions/${docId}`, {
      method: 'DELETE',
    }),
}