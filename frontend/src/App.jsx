import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Component } from 'react'

class RouteErrorBoundary extends Component {
  state = { error: null }
  static getDerivedStateFromError(error) { return { error } }
  render() {
    if (this.state.error) {
      return (
        <div className="p-8 text-center text-red-600" dir="rtl">
          <p className="font-bold">שגיאה בטעינת הדף</p>
          <p className="text-sm text-gray-500 mt-1">{this.state.error.message}</p>
          <button className="mt-3 text-blue-500 text-sm" onClick={() => this.setState({ error: null })}>
            נסה שוב
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
import { LandingPage } from './pages/LandingPage'
import { DashboardPage } from './pages/DashboardPage'
import { ComparisonPage } from './pages/ComparisonPage'
import { AIQueryPage } from './pages/AIQueryPage'
import { MapPage } from './pages/MapPage'

function Navbar() {
  const base = "px-4 py-2 text-sm font-medium rounded-lg transition"
  const active = `${base} bg-blue-600 text-white`
  const inactive = `${base} text-gray-600 hover:bg-gray-100`

  return (
    <nav className="bg-white border-b px-6 py-2 flex gap-2" dir="rtl">
      <NavLink to="/app" className={({ isActive }) => isActive ? active : inactive} end>דשבורד</NavLink>
      <NavLink to="/app/compare" className={({ isActive }) => isActive ? active : inactive}>השוואה</NavLink>
      <NavLink to="/app/map" className={({ isActive }) => isActive ? active : inactive}>מפה</NavLink>
      <NavLink to="/app/ai" className={({ isActive }) => isActive ? active : inactive}>שאל AI</NavLink>
    </nav>
  )
}

function AppLayout() {
  return (
    <>
      <Navbar />
      <RouteErrorBoundary>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/compare" element={<ComparisonPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/ai" element={<AIQueryPage />} />
        </Routes>
      </RouteErrorBoundary>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app/*" element={<AppLayout />} />
      </Routes>
    </BrowserRouter>
  )
}
