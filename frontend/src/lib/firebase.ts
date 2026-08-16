import { initializeApp, type FirebaseApp } from 'firebase/app'
import { getAuth, type Auth } from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

/**
 * La web funciona incluso sin Firebase configurado (modo demo con datos de
 * ejemplo). Una vez tengas el proyecto Firebase y rellenes .env, esto
 * se activa solo.
 */
export const configReady = Boolean(
  firebaseConfig.apiKey &&
    firebaseConfig.authDomain &&
    firebaseConfig.projectId &&
    firebaseConfig.apiKey !== 'cambia' &&
    firebaseConfig.projectId !== 'cambia',
)

export const app: FirebaseApp | null = configReady ? initializeApp(firebaseConfig) : null
export const auth: Auth | null = configReady && app ? getAuth(app) : null