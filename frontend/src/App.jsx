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
import { AnalyticsPage } from './pages/AnalyticsPage'
import { AIQueryPage } from './pages/AIQueryPage'

function Navbar() {
  const base = "px-3 py-1 text-xs font-medium rounded-md transition"
  const active = `${base} bg-blue-600 text-white`
  const inactive = `${base} text-gray-600 hover:bg-gray-100`

  return (
    <nav className="bg-white border-b px-4 py-1 flex gap-1.5" dir="rtl">
      <NavLink to="/app" className={({ isActive }) => isActive ? active : inactive} end>דשבורד</NavLink>
      <NavLink to="/app/analytics" className={({ isActive }) => isActive ? active : inactive}>גרפים</NavLink>
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
          <Route path="/analytics" element={<AnalyticsPage />} />
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
