import { NavLink } from 'react-router-dom'
import {
  House,
  ChartLineUp,
  ClockCounterClockwise,
  Crown,
  Gear,
} from '@phosphor-icons/react'
import { useSession } from '../lib/auth'

const baseTabs = [
  { to: '/', label: 'Inicio', icon: House, end: true },
  { to: '/pronosticos', label: 'Pronóst.', icon: ChartLineUp },
  { to: '/historial', label: 'Historial', icon: ClockCounterClockwise },
  { to: '/premium', label: 'Premium', icon: Crown },
]

export function BottomNav() {
  const { admin } = useSession()

  const tabs = admin
    ? [...baseTabs, { to: '/admin', label: 'Admin', icon: Gear, end: false }]
    : baseTabs

  return (
    <nav className="bottom-nav">
      {tabs.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) =>
            `bottom-nav-item ${isActive ? 'active' : ''}`
          }
        >
          <Icon size={20} weight="regular" />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  )
}
