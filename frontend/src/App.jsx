import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { DashboardPage } from './pages/DashboardPage'
import { ComparisonPage } from './pages/ComparisonPage'
import { RankingsPage } from './pages/RankingsPage'

function Navbar() {
  const base = "px-4 py-2 text-sm font-medium rounded-lg transition"
  const active = `${base} bg-blue-600 text-white`
  const inactive = `${base} text-gray-600 hover:bg-gray-100`

  return (
    <nav className="bg-white border-b px-6 py-2 flex gap-2" dir="rtl">
      <NavLink to="/" className={({ isActive }) => isActive ? active : inactive} end>דשבורד</NavLink>
      <NavLink to="/compare" className={({ isActive }) => isActive ? active : inactive}>השוואה</NavLink>
      <NavLink to="/rankings" className={({ isActive }) => isActive ? active : inactive}>דירוגים</NavLink>
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/compare" element={<ComparisonPage />} />
        <Route path="/rankings" element={<RankingsPage />} />
      </Routes>
    </BrowserRouter>
  )
}
