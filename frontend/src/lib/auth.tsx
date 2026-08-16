import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
  type User,
} from 'firebase/auth'
import { auth } from './firebase'
import { api } from './api'

export interface SessionState {
  user: User | null
  loading: boolean
  premium: boolean
  premiumUntil: string | null
  admin: boolean
  signInWithGoogle: () => Promise<void>
  signOutUser: () => Promise<void>
  refreshSession: () => Promise<void>
}

const SessionContext = createContext<SessionState | undefined>(undefined)

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [claims, setClaims] = useState<{
    premium: boolean
    premium_until?: string
    admin: boolean
  }>({ premium: false, admin: false })

  useEffect(() => {
    if (!auth) {
      setLoading(false)
      return
    }
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser)
      setLoading(false)
      if (firebaseUser) {
        try {
          setClaims(await api.refreshClaims())
        } catch {
          setClaims({ premium: false, admin: false })
        }
      } else {
        setClaims({ premium: false, admin: false })
      }
    })
    return unsubscribe
  }, [])

  const signInWithGoogle = useCallback(async () => {
    if (!auth) {
      // Sin Firebase configurado solo hay modo demo (no hay login real).
      console.warn('Firebase no configurado: el login se activa al rellenar .env')
      return
    }
    const provider = new GoogleAuthProvider()
    await signInWithPopup(auth, provider)
  }, [])

  const signOutUser = useCallback(async () => {
    setClaims({ premium: false, admin: false })
    if (auth) {
      await signOut(auth)
    }
  }, [])

  const refreshSession = useCallback(async () => {
    if (!auth?.currentUser) return
    setClaims(await api.refreshClaims())
  }, [])

  const value = useMemo<SessionState>(
    () => ({
      user,
      loading,
      premium: claims.premium,
      premiumUntil: claims.premium_until ?? null,
      admin: claims.admin,
      signInWithGoogle,
      signOutUser,
      refreshSession,
    }),
    [user, loading, claims, signInWithGoogle, signOutUser, refreshSession],
  )

  return (
    <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
  )
}

export function useSession(): SessionState {
  const ctx = useContext(SessionContext)
  if (!ctx) throw new Error('useSession debe usarse dentro de <SessionProvider>')
  return ctx
}