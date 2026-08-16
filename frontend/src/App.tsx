import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { SessionProvider } from './lib/auth'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
import { Predictions } from './pages/Predictions'
import { History } from './pages/History'
import { Pricing } from './pages/Pricing'
import { Dashboard } from './pages/Dashboard'
import { Admin } from './pages/Admin'

export default function App() {
  return (
    <SessionProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/pronosticos" element={<Predictions />} />
            <Route path="/historial" element={<History />} />
            <Route path="/premium" element={<Pricing />} />
            <Route path="/perfil" element={<Dashboard />} />
            <Route path="/admin" element={<Admin />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </SessionProvider>
  )
}