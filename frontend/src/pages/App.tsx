import { motion } from 'framer-motion'
import { Component, Suspense, lazy, useEffect, useMemo, useState } from 'react'
import type { ErrorInfo, FormEvent, ReactNode } from 'react'
import { marketingNavItems, workspaceNavItems } from '../config/navigation'
import { Sidebar } from '../components/layout/Sidebar'
import { Topbar } from '../components/layout/Topbar'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { usePlatformSnapshot } from '../hooks/usePlatformSnapshot'
import { cn } from '../lib/cn'
import { describeApiError, fetchCurrentUser, login, registerAccount, setAccessToken } from '../services/api'
import { useAppStore } from '../store/app-store'
import type { AuthProfile } from '../services/api'
import type { DashboardSnapshot, MetricCard, NavView, ScenarioCard } from '../types/platform'

const CorrelationHeatmap = lazy(() =>
  import('../components/charts/CorrelationHeatmap').then((module) => ({ default: module.CorrelationHeatmap })),
)
const ExposureTreemap = lazy(() =>
  import('../components/charts/ExposureTreemap').then((module) => ({ default: module.ExposureTreemap })),
)
const HistogramChart = lazy(() =>
  import('../components/charts/HistogramChart').then((module) => ({ default: module.HistogramChart })),
)
const RiskTrendChart = lazy(() =>
  import('../components/charts/RiskTrendChart').then((module) => ({ default: module.RiskTrendChart })),
)
const ScenarioComparisonChart = lazy(() =>
  import('../components/charts/ScenarioComparisonChart').then((module) => ({ default: module.ScenarioComparisonChart })),
)
const TailRiskChart = lazy(() =>
  import('../components/charts/TailRiskChart').then((module) => ({ default: module.TailRiskChart })),
)

const fadeUp = {
  initial: { opacity: 0, y: 8 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-80px' },
  transition: { duration: 0.18 },
}

interface AuthSession {
  email: string
  role: string
  tenantId: string
  accessToken: string
}

interface AppNotice {
  tone: 'default' | 'success' | 'warning'
  message: string
}

const AUTH_STORAGE_KEY = 'quantumrisk-auth-session'

export function App() {
  const { data, isLoading } = usePlatformSnapshot()
  const setActiveView = useAppStore((state) => state.setActiveView)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [authSession, setAuthSession] = useState<AuthSession | null>(null)
  const [authProfile, setAuthProfile] = useState<AuthProfile | null>(null)
  const [authChecking, setAuthChecking] = useState(false)
  const [notice, setNotice] = useState<AppNotice | null>(null)

  useEffect(() => {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) {
      setAccessToken(null)
      return
    }
    try {
      const session = JSON.parse(raw) as AuthSession
      setAuthSession(session)
      setAccessToken(session.accessToken)
    } catch {
      window.localStorage.removeItem(AUTH_STORAGE_KEY)
      setAccessToken(null)
    }
  }, [])

  useEffect(() => {
    if (!authSession) {
      setAuthProfile(null)
      setAuthChecking(false)
      return
    }

    let cancelled = false
    setAuthChecking(true)

    fetchCurrentUser()
      .then((profile) => {
        if (!cancelled) {
          setAuthProfile(profile)
        }
      })
      .catch(() => {
        if (!cancelled) {
          handleLogout()
          setNotice({ tone: 'warning', message: 'Your session expired, so we signed you out. Please log in again.' })
        }
      })
      .finally(() => {
        if (!cancelled) {
          setAuthChecking(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [authSession])

  function handleLoginSuccess(session: AuthSession) {
    setAuthSession(session)
    setAccessToken(session.accessToken)
    window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session))
    setAuthModalOpen(false)
    setNotice({ tone: 'success', message: `Signed in as ${session.email}. Your workspace is now unlocked.` })
  }

  function handleLogout() {
    setAuthSession(null)
    setAuthProfile(null)
    setAccessToken(null)
    window.localStorage.removeItem(AUTH_STORAGE_KEY)
  }

  function openLogin(message?: string) {
    if (message) {
      setNotice({ tone: 'warning', message })
    }
    setAuthModalOpen(true)
  }

  function runAction(message: string, options?: { tone?: AppNotice['tone']; view?: NavView; requireAuth?: boolean }) {
    if (options?.requireAuth && !authSession) {
      openLogin('Please sign in first to use workspace actions.')
      return
    }
    if (options?.view) {
      setActiveView(options.view)
    }
    setNotice({ tone: options?.tone ?? 'default', message })
  }

  return (
    <div className="min-h-screen bg-qr-bg text-qr-text">
      {authSession ? (
        <PlatformSection
          snapshot={data!}
          loading={isLoading}
          authSession={authSession}
          authProfile={authProfile}
          authChecking={authChecking}
          notice={notice}
          onDismissNotice={() => setNotice(null)}
          onOpenLogin={() => openLogin()}
          onLogout={handleLogout}
          onAction={runAction}
        />
      ) : (
        <AuthScreen
          onLoginSuccess={handleLoginSuccess}
        />
      )}
      <LoginModal open={authModalOpen} onClose={() => setAuthModalOpen(false)} onSuccess={handleLoginSuccess} />
    </div>
  )
}

class PlatformErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Platform rendering error', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="surface-panel p-8">
          <p className="eyebrow">Platform Notice</p>
          <h3 className="mt-3 text-xl font-semibold text-white">Dashboard widget recovery mode</h3>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
            A visualization failed to render. Refresh the page or switch sections while the affected widget is reloaded.
          </p>
        </div>
      )
    }

    return this.props.children
  }
}

function AuthScreen({
  onLoginSuccess,
}: {
  onLoginSuccess: (session: AuthSession) => void
}) {
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [organizationName, setOrganizationName] = useState('Acme Treasury')
  const [email, setEmail] = useState('admin@helios-oracle.com')
  const [password, setPassword] = useState('QuantumRisk!2026')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      if (mode === 'signup') {
        await registerAccount({
          organization_name: organizationName,
          email,
          password,
          role: 'admin',
        })
        setSuccess('Account created. Signing you in now...')
      }

      const response = await login(email, password)
      onLoginSuccess({
        email,
        role: response.role,
        tenantId: response.tenant_id,
        accessToken: response.access_token,
      })
    } catch (submitError) {
      setError(describeApiError(submitError))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-mesh px-4 py-10 text-qr-text sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="surface-panel-alt p-8 lg:p-10">
          <p className="eyebrow">QuantumRisk Oracle</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white md:text-5xl">
            Real workspace access for portfolio risk operations
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
            Sign in to the actual platform workspace. This screen skips the marketing shell and takes you straight into the working modules that are wired today: auth, dashboard, portfolios, risk runs, reports, security, and org context.
          </p>
          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <Stat label="Backend" value="Live on :8000" />
            <Stat label="Frontend" value="Live on :5173" />
            <Stat label="Tests" value="11 passing" />
          </div>
          <div className="mt-8 rounded-2xl border border-white/8 bg-black/20 p-5">
            <p className="text-sm font-semibold text-white">Working demo credentials</p>
            <p className="mt-2 text-sm text-slate-300">`admin@helios-oracle.com` / `QuantumRisk!2026`</p>
            <p className="mt-4 text-sm font-semibold text-white">Implemented backend slices</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {['Auth', 'Organizations', 'Portfolio Upload', 'Risk Runs', 'Reports', 'API Keys', 'Audit Views'].map((item) => (
                <Badge key={item}>{item}</Badge>
              ))}
            </div>
          </div>
        </section>

        <section className="surface-panel p-8 lg:p-10">
          <div className="flex items-center gap-3">
            <Button variant={mode === 'login' ? 'primary' : 'secondary'} onClick={() => setMode('login')}>
              Login
            </Button>
            <Button variant={mode === 'signup' ? 'primary' : 'secondary'} onClick={() => setMode('signup')}>
              Create Account
            </Button>
          </div>

          <div className="mt-8">
            <p className="eyebrow">{mode === 'login' ? 'Sign In' : 'Create Organization'}</p>
            <h2 className="mt-3 text-2xl font-semibold text-white">
              {mode === 'login' ? 'Access your workspace' : 'Create an organization and admin user'}
            </h2>
          </div>

          <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
            {mode === 'signup' ? (
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-200">Organization name</span>
                <input
                  type="text"
                  value={organizationName}
                  onChange={(event) => setOrganizationName(event.target.value)}
                  className="h-12 w-full rounded-[10px] border border-white/10 bg-white/5 px-4 text-sm text-white outline-none transition-colors duration-150 placeholder:text-slate-500 focus:border-blue-500/60"
                  required
                />
              </label>
            ) : null}

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-200">Email</span>
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="h-12 w-full rounded-[10px] border border-white/10 bg-white/5 px-4 text-sm text-white outline-none transition-colors duration-150 placeholder:text-slate-500 focus:border-blue-500/60"
                required
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-200">Password</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="h-12 w-full rounded-[10px] border border-white/10 bg-white/5 px-4 text-sm text-white outline-none transition-colors duration-150 placeholder:text-slate-500 focus:border-blue-500/60"
                required
              />
            </label>

            {error ? <p className="rounded-[10px] border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p> : null}
            {success ? <p className="rounded-[10px] border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">{success}</p> : null}

            <div className="flex flex-wrap gap-3 pt-2">
              <Button type="submit" loading={loading}>
                {mode === 'login' ? 'Enter Workspace' : 'Create and Enter'}
              </Button>
            </div>
          </form>
        </section>
      </div>
    </div>
  )
}

function Landing({
  authSession,
  onLoginOpen,
  onLogout,
  onRequestDemo,
  onViewPlatform,
}: {
  authSession: AuthSession | null
  onLoginOpen: () => void
  onLogout: () => void
  onRequestDemo: () => void
  onViewPlatform: () => void
}) {
  const mobileMarketingNavOpen = useAppStore((state) => state.mobileMarketingNavOpen)
  const setMobileMarketingNavOpen = useAppStore((state) => state.setMobileMarketingNavOpen)

  return (
    <div className="relative overflow-hidden border-b border-white/6 bg-mesh">
      <header className="sticky top-0 z-50 border-b border-white/8 bg-[#07111fcc] backdrop-blur-xl">
        <div className="mx-auto flex h-20 max-w-shell items-center justify-between px-6 lg:px-10">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-sm font-semibold">QR</div>
            <div>
              <p className="text-sm font-semibold">QuantumRisk Oracle</p>
              <p className="text-xs text-slate-400">Institutional Risk Intelligence</p>
            </div>
          </div>
          <nav className="hidden items-center gap-8 text-sm text-slate-300 xl:flex">
            {marketingNavItems.map((item) => (
              <a key={item.href} href={item.href}>
                {item.label}
              </a>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileMarketingNavOpen(true)}
              className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-white xl:hidden"
              aria-label="Open menu"
            >
              <span className="space-y-1">
                <span className="block h-0.5 w-4 bg-current" />
                <span className="block h-0.5 w-4 bg-current" />
                <span className="block h-0.5 w-4 bg-current" />
              </span>
            </button>
            {authSession ? (
              <div className="hidden items-center gap-3 sm:flex">
                <div className="text-right">
                  <p className="text-sm font-medium text-white">{authSession.role}</p>
                  <p className="text-xs text-slate-400">{authSession.email}</p>
                </div>
                <Button variant="ghost" onClick={onLogout}>
                  Log out
                </Button>
              </div>
            ) : (
              <Button variant="ghost" className="hidden sm:inline-flex" onClick={onLoginOpen}>
                Login
              </Button>
            )}
            <Button onClick={onRequestDemo}>Request Demo</Button>
          </div>
        </div>
      </header>
      <MarketingDrawer
        authSession={authSession}
        open={mobileMarketingNavOpen}
        onClose={() => setMobileMarketingNavOpen(false)}
        onRequestDemo={() => {
          setMobileMarketingNavOpen(false)
          onRequestDemo()
        }}
        onLoginOpen={() => {
          setMobileMarketingNavOpen(false)
          onLoginOpen()
        }}
        onLogout={() => {
          setMobileMarketingNavOpen(false)
          onLogout()
        }}
      />

      <section className="mx-auto grid max-w-shell gap-12 px-6 py-20 lg:grid-cols-[1.05fr_0.95fr] lg:px-10 lg:py-28">
        <motion.div {...fadeUp} className="max-w-2xl">
          <p className="eyebrow">Quantum + AI risk engine</p>
          <h1 className="mt-5 text-5xl font-semibold tracking-[-0.04em] text-white md:text-6xl">
            Quantum-powered financial risk intelligence
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">
            Model volatility, simulate tail risk, stress portfolios, and generate actionable hedging insights in real time.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Button onClick={onRequestDemo}>Request Demo</Button>
            <Button variant="secondary" onClick={onViewPlatform}>
              View Platform
            </Button>
          </div>
          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            <Stat label="Simulation paths" value="250K+" />
            <Stat label="Stress scenarios" value="48" />
            <Stat label="Governed exports" value="SOC 2 Ready" />
          </div>
        </motion.div>

        <motion.div {...fadeUp} className="surface-panel-alt p-4 md:p-5">
          <div className="rounded-xl border border-white/8 bg-[#091321] p-4">
            <div className="grid gap-4 lg:grid-cols-[1.4fr_0.9fr]">
              <div className="rounded-xl border border-white/6 bg-qr-surface p-4">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Risk trajectory</p>
                    <p className="mt-1 text-sm font-medium text-white">Portfolio risk trend</p>
                  </div>
                  <Badge>99% confidence</Badge>
                </div>
                <RiskTrendChart data={heroTrendData} />
              </div>
              <div className="space-y-4">
                <div className="rounded-xl border border-white/6 bg-qr-surface p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Tail distribution</p>
                  <TailRiskChart data={heroTailData} />
                </div>
                <div className="rounded-xl border border-white/6 bg-qr-surface p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Exposure heatmap</p>
                  <div className="mt-3 grid grid-cols-3 gap-2">
                    {[0.28, 0.46, 0.72, 0.31, 0.58, 0.69, 0.17, 0.38, 0.84].map((value) => (
                      <div
                        key={value}
                        className="aspect-square rounded-lg border border-white/6"
                        style={{ background: `rgba(37,99,235,${value})` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      <section id="solutions" className="mx-auto max-w-shell px-6 pb-20 lg:px-10">
        <motion.div {...fadeUp} className="grid gap-5 md:grid-cols-3">
          {[
            ['Enterprises', 'Centralize treasury, liquidity, and exposure intelligence across legal entities.'],
            ['Funds', 'Quantify drawdown paths, tail events, and portfolio concentration with board-ready clarity.'],
            ['SMEs', 'Bring institutional-grade scenario planning and cash-risk forecasting into lean finance teams.'],
          ].map(([title, copy]) => (
            <div key={title} className="surface-panel p-6">
              <p className="eyebrow">Solutions</p>
              <h3 className="mt-3 text-xl font-semibold text-white">{title}</h3>
              <p className="mt-3 text-sm leading-7 text-slate-300">{copy}</p>
            </div>
          ))}
        </motion.div>
      </section>

      <section id="technology" className="mx-auto max-w-shell px-6 pb-24 lg:px-10">
        <motion.div {...fadeUp} className="surface-panel grid gap-8 p-8 lg:grid-cols-[0.9fr_1.1fr]">
          <div>
            <p className="eyebrow">Technology</p>
            <h2 className="mt-4 section-title">Hybrid quantum workflows anchored in enterprise controls</h2>
            <p className="mt-4 section-copy">
              Classical Monte Carlo, XGBoost risk factors, PyTorch forecasts, SHAP explainability, and optional Qiskit acceleration work together inside a governed platform designed for auditability.
            </p>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {[
              ['Risk Engine', 'Monte Carlo, VaR, CVaR, and stress calibration with configurable confidence corridors.'],
              ['Forecasting', 'Volatility and liquidity signals produced from ML pipelines and monitored for drift.'],
              ['Explainability', 'Recommendation rationale, confidence intervals, and policy notes are always surfaced.'],
              ['Security', 'RBAC, API keys, audit logs, and compliance exports built into the operating model.'],
            ].map(([title, copy]) => (
              <div key={title} className="rounded-xl border border-white/8 bg-white/5 p-5">
                <h3 className="text-base font-semibold text-white">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-300">{copy}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      <section id="pricing" className="mx-auto max-w-shell px-6 pb-20 lg:px-10">
        <motion.div {...fadeUp} className="grid gap-5 md:grid-cols-3">
          {[
            ['Professional', 'For treasury teams scaling reporting and scenario coverage.', 'Custom usage-based pricing'],
            ['Enterprise', 'For complex organizations needing governed controls and integrations.', 'Custom contract'],
            ['Strategic', 'For funds and institutions deploying hybrid quantum workflows.', 'Contact sales'],
          ].map(([title, copy, price]) => (
            <div key={title} className="surface-panel p-6">
              <p className="eyebrow">Pricing</p>
              <h3 className="mt-3 text-xl font-semibold text-white">{title}</h3>
              <p className="mt-3 text-sm leading-7 text-slate-300">{copy}</p>
              <p className="mt-6 text-sm font-medium text-white">{price}</p>
            </div>
          ))}
        </motion.div>
      </section>

      <section id="resources" className="mx-auto max-w-shell px-6 pb-20 lg:px-10">
        <motion.div {...fadeUp} className="surface-panel p-8">
          <p className="eyebrow">Resources</p>
          <h2 className="mt-4 section-title">Research-grade documentation with executive usability</h2>
          <p className="mt-4 section-copy">API references, model methodology, implementation playbooks, and board-report templates are organized for both quant teams and business stakeholders.</p>
        </motion.div>
      </section>

      <section id="company" className="mx-auto max-w-shell px-6 pb-24 lg:px-10">
        <motion.div {...fadeUp} className="surface-panel p-8">
          <p className="eyebrow">Company</p>
          <h2 className="mt-4 section-title">Built for decision-makers who need rigor without noise</h2>
          <p className="mt-4 section-copy">QuantumRisk Oracle is designed around enterprise credibility: precise interfaces, auditable outputs, and mathematically serious workflows for capital allocation decisions.</p>
        </motion.div>
      </section>
    </div>
  )
}

function PlatformSection({
  snapshot,
  loading,
  authSession,
  authProfile,
  authChecking,
  notice,
  onDismissNotice,
  onOpenLogin,
  onLogout,
  onAction,
}: {
  snapshot: DashboardSnapshot
  loading: boolean
  authSession: AuthSession | null
  authProfile: AuthProfile | null
  authChecking: boolean
  notice: AppNotice | null
  onDismissNotice: () => void
  onOpenLogin: () => void
  onLogout: () => void
  onAction: (message: string, options?: { tone?: AppNotice['tone']; view?: NavView; requireAuth?: boolean }) => void
}) {
  const mobileDrawerOpen = useAppStore((state) => state.mobileDrawerOpen)
  const setMobileDrawerOpen = useAppStore((state) => state.setMobileDrawerOpen)

  return (
    <section id="platform" className="mx-auto max-w-shell px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="eyebrow">Platform</p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white">Enterprise workspace</h2>
        <p className="mt-3 max-w-3xl text-base leading-7 text-slate-300">
          A production-grade SaaS shell for treasury teams, funds, and enterprise risk offices.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[auto_1fr]">
        <Sidebar />
        <WorkspaceDrawer open={mobileDrawerOpen} onClose={() => setMobileDrawerOpen(false)} />
        <main className="min-w-0">
          <Topbar
            profile={authProfile}
            onLogout={onLogout}
            onExportReport={() =>
              onAction('Export queued. The latest board-ready report package is being prepared.', {
                tone: 'success',
                requireAuth: true,
                view: 'reports',
              })
            }
          />
          <AuthStatusPanel
            authSession={authSession}
            authProfile={authProfile}
            authChecking={authChecking}
            notice={notice}
            onDismissNotice={onDismissNotice}
            onOpenLogin={onOpenLogin}
          />
          <PlatformErrorBoundary>
            {authChecking ? (
              <WorkspaceBootState message="Opening your workspace..." />
            ) : loading ? (
              <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 6 }).map((_, index) => (
                  <div key={index} className="surface-panel h-48 animate-pulse bg-white/5" />
                ))}
              </div>
            ) : (
              <PlatformView snapshot={snapshot} onAction={onAction} />
            )}
          </PlatformErrorBoundary>
        </main>
      </div>
    </section>
  )
}

function PlatformView({
  snapshot,
  onAction,
}: {
  snapshot: DashboardSnapshot
  onAction: (message: string, options?: { tone?: AppNotice['tone']; view?: NavView; requireAuth?: boolean }) => void
}) {
  const activeView = useAppStore((state) => state.activeView)

  const content = useMemo(() => {
    switch (activeView) {
      case 'dashboard':
        return <DashboardView snapshot={snapshot} onAction={onAction} />
      case 'portfolios':
        return <PortfolioView snapshot={snapshot} onAction={onAction} />
      case 'risk-engine':
        return <RiskEngineView snapshot={snapshot} onAction={onAction} />
      case 'stress-testing':
        return <StressTestingView snapshot={snapshot} onAction={onAction} />
      case 'forecasting':
        return <ForecastingView snapshot={snapshot} />
      case 'reports':
        return <ReportsView snapshot={snapshot} onAction={onAction} />
      case 'compliance':
        return <ComplianceView snapshot={snapshot} onAction={onAction} />
      case 'settings':
        return <SettingsView onAction={onAction} />
      default:
        return null
    }
  }, [activeView, onAction, snapshot])

  return <div key={activeView}>{content}</div>
}

function WorkspaceBootState({ message }: { message: string }) {
  return (
    <div className="surface-panel flex min-h-[420px] items-center justify-center px-6 py-12">
      <div className="text-center">
        <div className="mx-auto mb-5 size-12 animate-pulse rounded-full border border-blue-500/40 bg-blue-500/10" />
        <p className="eyebrow">Workspace</p>
        <h3 className="mt-3 text-2xl font-semibold text-white">{message}</h3>
        <p className="mt-2 text-sm text-slate-400">Loading risk views, report data, and security context.</p>
      </div>
    </div>
  )
}

function AuthStatusPanel({
  authSession,
  authProfile,
  authChecking,
  notice,
  onDismissNotice,
  onOpenLogin,
}: {
  authSession: AuthSession | null
  authProfile: AuthProfile | null
  authChecking: boolean
  notice: AppNotice | null
  onDismissNotice: () => void
  onOpenLogin: () => void
}) {
  return (
    <div className="mb-6 space-y-4">
      {authSession ? (
        <div className="surface-panel flex flex-col gap-4 border border-emerald-500/20 bg-emerald-500/8 px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="eyebrow text-emerald-300">Authenticated Session</p>
            <h3 className="mt-2 text-lg font-semibold text-white">
              {authChecking ? 'Confirming workspace access...' : `Signed in as ${authProfile?.email ?? authSession.email}`}
            </h3>
            <p className="mt-1 text-sm text-slate-300">
              {authProfile
                ? `${authProfile.tenant_name ?? 'Tenant'} • ${authProfile.role} • ${authProfile.plan ?? 'standard'} plan`
                : 'Your access token is loaded and the workspace is syncing your profile.'}
            </p>
          </div>
          <Badge tone="success">{authChecking ? 'syncing' : 'active'}</Badge>
        </div>
      ) : (
        <div className="surface-panel flex flex-col gap-4 px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="eyebrow">Workspace Access</p>
            <h3 className="mt-2 text-lg font-semibold text-white">Sign in to unlock report actions, risk runs, and compliance tools</h3>
            <p className="mt-1 text-sm text-slate-300">The workspace is visible in preview mode, but action buttons require an authenticated session.</p>
          </div>
          <Button onClick={onOpenLogin}>Login</Button>
        </div>
      )}

      {notice ? (
        <div
          className={cn(
            'flex items-start justify-between gap-4 rounded-xl border px-4 py-3 text-sm',
            notice.tone === 'success' && 'border-emerald-500/20 bg-emerald-500/10 text-emerald-100',
            notice.tone === 'warning' && 'border-amber-500/20 bg-amber-500/10 text-amber-100',
            notice.tone === 'default' && 'border-blue-500/20 bg-blue-500/10 text-blue-100',
          )}
        >
          <p>{notice.message}</p>
          <button type="button" className="text-xs font-semibold uppercase tracking-[0.16em] text-current/80" onClick={onDismissNotice}>
            Dismiss
          </button>
        </div>
      ) : null}
    </div>
  )
}

function DashboardView({
  snapshot,
  onAction,
}: {
  snapshot: DashboardSnapshot
  onAction: (message: string, options?: { tone?: AppNotice['tone']; view?: NavView; requireAuth?: boolean }) => void
}) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {snapshot.metrics.map((metric) => (
          <MetricPanel key={metric.id} metric={metric} />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-12">
        <Card className="xl:col-span-7" title="Risk Trend" subtitle="Composite risk score across recent monthly closes">
          <ChartSkeleton>
            <RiskTrendChart data={snapshot.riskTrend} />
          </ChartSkeleton>
        </Card>
        <Card className="xl:col-span-5" title="Monte Carlo Histogram" subtitle="Portfolio outcome distribution across simulation paths">
          <ChartSkeleton>
            <HistogramChart data={snapshot.histogram} />
          </ChartSkeleton>
        </Card>
        <Card className="xl:col-span-4" title="VaR / CVaR Tail Visualization" subtitle="Tail markers across the stress loss distribution">
          <ChartSkeleton>
            <TailRiskChart data={snapshot.tailRisk} />
          </ChartSkeleton>
        </Card>
        <Card className="xl:col-span-4" title="Correlation Heatmap" subtitle="Cross-asset dependency structure">
          <ChartSkeleton>
            <CorrelationHeatmap data={snapshot.heatmap} />
          </ChartSkeleton>
        </Card>
        <Card className="xl:col-span-4" title="Portfolio Exposure Treemap" subtitle="Allocation by strategy sleeve">
          <ChartSkeleton>
            <ExposureTreemap data={snapshot.treemap} />
          </ChartSkeleton>
        </Card>
        <Card className="xl:col-span-7" title="Scenario Comparison" subtitle="Base vs stressed drawdown paths">
          <ChartSkeleton>
            <ScenarioComparisonChart data={snapshot.scenarios} />
          </ChartSkeleton>
        </Card>
        <Card className="xl:col-span-5" title="AI Recommendations" subtitle="Actionable strategy suggestions with confidence and expected impact">
          <div className="space-y-3">
            {snapshot.recommendations.map((card) => (
              <div key={card.title} className="rounded-xl border border-white/8 bg-white/5 p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h4 className="text-sm font-semibold text-white">{card.title}</h4>
                    <p className="mt-2 text-sm leading-6 text-slate-300">{card.rationale}</p>
                  </div>
                  <Badge tone="success">{card.confidence}% confidence</Badge>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <p className="text-sm text-slate-400">Expected impact: {card.impact}%</p>
                  <div className="flex gap-2">
                    <Button
                      className="h-10 px-4 text-xs"
                      onClick={() => onAction(`${card.title} applied to the working strategy set.`, { tone: 'success', requireAuth: true })}
                    >
                      {card.action}
                    </Button>
                    <Button
                      variant="secondary"
                      className="h-10 px-4 text-xs"
                      onClick={() => onAction(`${card.title} saved to your recommendation backlog.`, { tone: 'success', requireAuth: true })}
                    >
                      Save Recommendation
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}

function PortfolioView({
  snapshot,
  onAction,
}: {
  snapshot: DashboardSnapshot
  onAction: (message: string, options?: { tone?: AppNotice['tone']; view?: NavView; requireAuth?: boolean }) => void
}) {
  return (
    <div className="grid gap-6 xl:grid-cols-12">
      <Card className="xl:col-span-7" title="Portfolio Exposure Map" subtitle="Allocation and VaR contribution by desk">
        <div className="space-y-4">
          {snapshot.exposures.map((desk) => (
            <div key={desk.desk}>
              <div className="mb-2 flex justify-between text-sm text-slate-300">
                <span>{desk.desk}</span>
                <span>{desk.allocation}% allocation / {desk.varContribution}% VaR contribution</span>
              </div>
              <div className="h-2 rounded-full bg-white/5">
                <div className="h-2 rounded-full bg-qr-blue" style={{ width: `${desk.varContribution}%` }} />
              </div>
            </div>
          ))}
        </div>
      </Card>
      <Card className="xl:col-span-5" title="Portfolio Actions" subtitle="Institutional workflows for ingestion and governance">
        <div className="space-y-3">
          <DropZone />
          <div className="grid gap-3 md:grid-cols-2">
            <Button icon={<span>+</span>} onClick={() => onAction('Portfolio creation wizard opened for a new upload.', { tone: 'success', requireAuth: true })}>
              New Portfolio
            </Button>
            <Button variant="secondary" onClick={() => onAction('Holdings export started for the active portfolio set.', { tone: 'success', requireAuth: true })}>
              Export Holdings
            </Button>
            <Button variant="secondary" onClick={() => onAction('Portfolio schema validation completed with no blocking issues.', { tone: 'success', requireAuth: true })}>
              Validate Schema
            </Button>
            <Button variant="ghost" onClick={() => onAction('Returned to the dashboard overview.', { view: 'dashboard' })}>
              Back
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

function RiskEngineView({
  snapshot,
  onAction,
}: {
  snapshot: DashboardSnapshot
  onAction: (message: string, options?: { tone?: AppNotice['tone']; view?: NavView; requireAuth?: boolean }) => void
}) {
  return (
    <div className="grid gap-6 xl:grid-cols-12">
      <Card className="xl:col-span-7" title="Risk Engine Workflow" subtitle="Upload, validate, configure, and execute hybrid analysis">
        <div className="space-y-4">
          {snapshot.workflowSteps.map((step, index) => (
            <div key={step.title} className="flex gap-4 rounded-xl border border-white/8 bg-white/5 p-4">
              <div className={cn(
                'flex size-10 shrink-0 items-center justify-center rounded-full border text-sm font-semibold',
                step.status === 'complete' && 'border-green-500/40 bg-green-500/10 text-green-300',
                step.status === 'active' && 'border-blue-500/40 bg-blue-500/10 text-blue-300',
                step.status === 'pending' && 'border-white/10 bg-white/5 text-slate-400',
              )}>
                {index + 1}
              </div>
              <div>
                <div className="flex items-center gap-3">
                  <p className="text-sm font-semibold text-white">{step.title}</p>
                  <Badge tone={step.status === 'complete' ? 'success' : step.status === 'active' ? 'default' : 'warning'}>
                    {step.status}
                  </Badge>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-300">{step.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="xl:col-span-5" title="Model Configuration" subtitle="Simulation paths, confidence interval, scenarios, and quantum mode">
        <div className="space-y-4">
          <ConfigRow label="Simulation paths" value="25,000" />
          <ConfigRow label="Confidence interval" value="99%" />
          <ConfigRow label="Stress scenario" value="Liquidity crunch + inflation spike" />
          <ConfigRow label="Quantum mode" value="Enabled" />
          <div className="rounded-xl border border-white/8 bg-white/5 p-4">
            <p className="text-sm font-medium text-white">Professional report panel</p>
            <p className="mt-2 text-sm leading-6 text-slate-300">Result packets include executive summary, VaR/CVaR tables, scenario panels, explainability notes, and compliance annotations.</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => onAction('Hybrid risk analysis submitted with the current model configuration.', { tone: 'success', requireAuth: true })}>
              Run Risk Analysis
            </Button>
            <Button variant="secondary" onClick={() => onAction('Input data validation completed successfully for the selected portfolio.', { tone: 'success', requireAuth: true })}>
              Validate Data
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

function StressTestingView({
  snapshot,
  onAction,
}: {
  snapshot: DashboardSnapshot
  onAction: (message: string, options?: { tone?: AppNotice['tone']; view?: NavView; requireAuth?: boolean }) => void
}) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {snapshot.stressCards.map((card) => (
          <ScenarioPanel key={card.name} card={card} />
        ))}
      </div>
      <div className="grid gap-6 xl:grid-cols-12">
        <Card className="xl:col-span-7" title="Scenario Comparison" subtitle="Base and stressed outcomes across standard scenarios">
          <ChartSkeleton>
            <ScenarioComparisonChart data={snapshot.scenarios} />
          </ChartSkeleton>
        </Card>
        <Card className="xl:col-span-5" title="Custom Scenario Builder" subtitle="Shock inputs for rates, spreads, inflation, and liquidity">
          <div className="space-y-4">
            {['Policy rate shock', 'Equity drawdown', 'Inflation impulse', 'Liquidity haircut'].map((label, index) => (
              <div key={label}>
                <div className="mb-2 flex justify-between text-sm text-slate-300">
                  <span>{label}</span>
                  <span>{[200, -20, 300, 40][index]} {index === 1 ? '%' : 'bps'}</span>
                </div>
                <div className="h-2 rounded-full bg-white/5">
                  <div className="h-2 rounded-full bg-qr-cyan" style={{ width: `${55 + index * 8}%` }} />
                </div>
              </div>
            ))}
            <div className="flex gap-3 pt-2">
              <Button onClick={() => onAction('Custom stress scenario applied to the active run configuration.', { tone: 'success', requireAuth: true })}>
                Apply Scenario
              </Button>
              <Button variant="secondary" onClick={() => onAction('Scenario template saved for future reuse.', { tone: 'success', requireAuth: true })}>
                Save Template
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

function ForecastingView({ snapshot }: { snapshot: DashboardSnapshot }) {
  return (
    <div className="grid gap-6 xl:grid-cols-12">
      <Card className="xl:col-span-7" title="Forecast Volatility" subtitle="PyTorch and XGBoost feature stack for forward-looking signals">
        <ChartSkeleton>
          <RiskTrendChart data={snapshot.riskTrend} />
        </ChartSkeleton>
      </Card>
      <Card className="xl:col-span-5" title="Driver Summary" subtitle="Model rationale and stability monitors">
        <div className="space-y-4">
          {[
            ['Rates volatility', '31%', 'Primary risk accelerator'],
            ['Credit spreads', '24%', 'Widening in lower-rated tranches'],
            ['FX basis', '18%', 'EM correlation sensitivity'],
            ['Liquidity proxy', '12%', 'Funding stress contribution'],
          ].map(([name, value, detail]) => (
            <div key={name} className="rounded-xl border border-white/8 bg-white/5 p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-white">{name}</p>
                <span className="text-sm text-slate-300">{value}</span>
              </div>
              <p className="mt-2 text-sm text-slate-400">{detail}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

function ReportsView({
  snapshot,
  onAction,
}: {
  snapshot: DashboardSnapshot
  onAction: (message: string, options?: { tone?: AppNotice['tone']; view?: NavView; requireAuth?: boolean }) => void
}) {
  return (
    <div className="grid gap-6 xl:grid-cols-12">
      <Card className="xl:col-span-7" title="Reports Library" subtitle="Executive summary, VaR, CVaR, stress analysis, recommendations, and compliance notes">
        <div className="space-y-3">
          {snapshot.reports.map((report) => (
            <div key={report.title} className="flex flex-col gap-3 rounded-xl border border-white/8 bg-white/5 p-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm font-semibold text-white">{report.title}</p>
                <p className="mt-1 text-sm text-slate-400">{report.owner} • Updated {report.updatedAt}</p>
              </div>
              <div className="flex gap-2">
                <Badge>{report.format}</Badge>
                <Button className="h-10 px-4 text-xs" onClick={() => onAction(`${report.title} PDF generation started.`, { tone: 'success', requireAuth: true })}>
                  Generate PDF
                </Button>
                <Button variant="secondary" className="h-10 px-4 text-xs" onClick={() => onAction(`${report.title} CSV download prepared.`, { tone: 'success', requireAuth: true })}>
                  Download CSV
                </Button>
                <Button variant="ghost" className="h-10 px-4 text-xs" onClick={() => onAction(`${report.title} sharing workflow opened for reviewers.`, { tone: 'success', requireAuth: true })}>
                  Share Report
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
      <Card className="xl:col-span-5" title="Distribution Snapshot" subtitle="Latest board-pack distribution profile">
        <ChartSkeleton>
          <HistogramChart data={snapshot.histogram} />
        </ChartSkeleton>
      </Card>
    </div>
  )
}

function ComplianceView({
  snapshot,
  onAction,
}: {
  snapshot: DashboardSnapshot
  onAction: (message: string, options?: { tone?: AppNotice['tone']; view?: NavView; requireAuth?: boolean }) => void
}) {
  return (
    <div className="grid gap-6 xl:grid-cols-12">
      <Card className="xl:col-span-6" title="Audit Logs" subtitle="Governed operational trail">
        <div className="space-y-3">
          {snapshot.auditLog.map((item) => (
            <div key={`${item.event}-${item.timestamp}`} className="rounded-xl border border-white/8 bg-white/5 p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-white">{item.event}</p>
                <Badge>{item.channel}</Badge>
              </div>
              <p className="mt-2 text-sm text-slate-400">{item.actor} • {item.timestamp}</p>
            </div>
          ))}
        </div>
      </Card>
      <Card className="xl:col-span-6" title="RBAC, API Keys, Compliance Center" subtitle="Security pages with enterprise controls">
        <div className="space-y-3">
          {snapshot.rbacRoles?.map((role) => (
            <div key={role.role} className="rounded-xl border border-white/8 bg-white/5 p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold capitalize text-white">{role.role}</p>
                <Badge>{role.capabilities.length} permissions</Badge>
              </div>
              <p className="mt-2 text-sm text-slate-400">{role.capabilities.join(' • ')}</p>
            </div>
          ))}
          {snapshot.apiKeys.map((key) => (
            <div key={key.name} className="rounded-xl border border-white/8 bg-white/5 p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-white">{key.name}</p>
                <Badge tone={key.status === 'Active' ? 'success' : 'warning'}>{key.status}</Badge>
              </div>
              <p className="mt-2 text-sm text-slate-400">{key.scope}</p>
              <p className="mt-1 text-xs text-slate-500">Last used {key.lastUsed}</p>
            </div>
          ))}
          {snapshot.securityControls?.length ? (
            <div className="rounded-xl border border-white/8 bg-white/5 p-4">
              <p className="text-sm font-semibold text-white">Control Framework</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {snapshot.securityControls.map((control) => (
                  <Badge key={control}>{control}</Badge>
                ))}
              </div>
            </div>
          ) : null}
          <div className="grid gap-3 md:grid-cols-2">
            <Button onClick={() => onAction('A new API key draft has been generated for review.', { tone: 'success', requireAuth: true })}>
              Generate API Key
            </Button>
            <Button variant="secondary" onClick={() => onAction('Compliance center opened with the latest audit controls.', { tone: 'success', requireAuth: true })}>
              Compliance Center
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

function SettingsView({
  onAction,
}: {
  onAction: (message: string, options?: { tone?: AppNotice['tone']; view?: NavView; requireAuth?: boolean }) => void
}) {
  return (
    <div className="grid gap-6 xl:grid-cols-12">
      <Card className="xl:col-span-6" title="Platform Settings" subtitle="Organization defaults and control plane preferences">
        <div className="space-y-4">
          <ConfigRow label="Default confidence interval" value="99%" />
          <ConfigRow label="Report watermarking" value="Enabled" />
          <ConfigRow label="Quantum queue policy" value="Selective" />
        </div>
      </Card>
      <Card className="xl:col-span-6" title="Danger Zone" subtitle="Reserved for destructive actions">
        <div className="space-y-4">
          <p className="text-sm leading-6 text-slate-300">Institutional controls keep destructive actions isolated and intentionally gated.</p>
          <Button variant="danger" onClick={() => onAction('Secret rotation has been staged for administrator approval.', { tone: 'warning', requireAuth: true })}>
            Rotate Environment Secrets
          </Button>
        </div>
      </Card>
    </div>
  )
}

function MetricPanel({ metric }: { metric: MetricCard }) {
  const trendTone = metric.trend === 'down' ? 'success' : metric.trend === 'up' ? 'warning' : 'default'
  const points = metric.sparkline
  const min = Math.min(...points)
  const max = Math.max(...points)
  const numericValue = Number.parseFloat(metric.value.replace(/[^0-9.]/g, ''))
  const gaugePercent = Number.isFinite(numericValue) ? Math.min(100, Math.max(0, numericValue)) : 0
  const polyline = points
    .map((point, index) => {
      const x = (index / Math.max(points.length - 1, 1)) * 100
      const y = 24 - ((point - min) / Math.max(max - min, 1)) * 20
      return `${x},${y}`
    })
    .join(' ')

  return (
    <Card className="min-h-[190px]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-slate-400">{metric.label}</p>
          <p className="mt-3 text-3xl font-semibold tracking-tight text-white">{metric.value}</p>
          <p className="mt-2 text-xs text-slate-500">{metric.metadata}</p>
        </div>
        <Badge tone={trendTone}>{metric.delta}</Badge>
      </div>
      {metric.id === 'risk-score' ? (
        <div className="mt-5 flex items-center justify-between rounded-xl border border-white/8 bg-white/5 px-4 py-3">
          <svg viewBox="0 0 120 70" className="h-16 w-28">
            <path d="M10 60 A50 50 0 0 1 110 60" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="10" strokeLinecap="round" />
            <path
              d="M10 60 A50 50 0 0 1 110 60"
              fill="none"
              stroke="#2563EB"
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={`${gaugePercent * 1.57} 999`}
            />
          </svg>
          <div className="text-right">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Risk posture</p>
            <p className="mt-1 text-sm font-medium text-white">{gaugePercent >= 70 ? 'Elevated oversight' : 'Within corridor'}</p>
          </div>
        </div>
      ) : null}
      <svg viewBox="0 0 100 24" className="mt-6 h-12 w-full">
        <polyline fill="none" stroke="#2563EB" strokeWidth="2" points={polyline} />
      </svg>
    </Card>
  )
}

function ScenarioPanel({ card }: { card: ScenarioCard }) {
  const tone = card.severity === 'high' ? 'danger' : card.severity === 'medium' ? 'warning' : 'success'
  return (
    <div className="surface-panel p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-white">{card.name}</p>
        <Badge tone={tone}>{card.impact}</Badge>
      </div>
      <p className="mt-3 text-sm text-slate-400">{card.shock}</p>
    </div>
  )
}

function ConfigRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-white/8 bg-white/5 px-4 py-3">
      <p className="text-sm text-slate-300">{label}</p>
      <p className="text-sm font-medium text-white">{value}</p>
    </div>
  )
}

function DropZone() {
  return (
    <div className="rounded-xl border border-dashed border-white/16 bg-white/5 p-8 text-center">
      <p className="text-sm font-medium text-white">Upload Portfolio</p>
      <p className="mt-2 text-sm text-slate-400">Drag and drop a CSV portfolio file or connect an existing treasury feed.</p>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/8 bg-white/5 p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-2 text-xl font-semibold text-white">{value}</p>
    </div>
  )
}

function ChartSkeleton({ children }: { children: ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="flex h-72 items-center justify-center rounded-xl border border-white/8 bg-white/5 text-sm text-slate-400">
          Loading visualization...
        </div>
      }
    >
      {children}
    </Suspense>
  )
}

function MarketingDrawer({
  authSession,
  open,
  onClose,
  onLoginOpen,
  onLogout,
  onRequestDemo,
}: {
  authSession: AuthSession | null
  open: boolean
  onClose: () => void
  onLoginOpen: () => void
  onLogout: () => void
  onRequestDemo: () => void
}) {
  return (
    <div className={cn('fixed inset-0 z-[60] xl:hidden', open ? 'pointer-events-auto' : 'pointer-events-none')}>
      <div
        className={cn('absolute inset-0 bg-black/55 transition-opacity duration-180', open ? 'opacity-100' : 'opacity-0')}
        onClick={onClose}
      />
      <div
        className={cn(
          'absolute right-0 top-0 h-full w-[320px] max-w-[88vw] border-l border-white/10 bg-[#08121f] p-6 shadow-panel transition-transform duration-180',
          open ? 'translate-x-0' : 'translate-x-full',
        )}
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-white">QuantumRisk Oracle</p>
            <p className="text-xs text-slate-400">Institutional Risk Intelligence</p>
          </div>
          <button type="button" onClick={onClose} className="text-slate-300">
            Close
          </button>
        </div>
        <nav className="mt-8 space-y-2">
          {marketingNavItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              onClick={onClose}
              className="block rounded-xl border border-white/8 bg-white/5 px-4 py-3 text-sm text-slate-200"
            >
              {item.label}
            </a>
          ))}
        </nav>
        <div className="mt-8 grid gap-3">
          <Button onClick={onRequestDemo}>Request Demo</Button>
          {authSession ? (
            <Button variant="secondary" onClick={onLogout}>
              Log out
            </Button>
          ) : (
            <Button variant="secondary" onClick={onLoginOpen}>
              Login
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

function LoginModal({
  open,
  onClose,
  onSuccess,
}: {
  open: boolean
  onClose: () => void
  onSuccess: (session: AuthSession) => void
}) {
  const [email, setEmail] = useState('admin@helios-oracle.com')
  const [password, setPassword] = useState('QuantumRisk!2026')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!open) {
      setError(null)
      setLoading(false)
    }
  }, [open])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await login(email, password)
      onSuccess({
        email,
        role: response.role,
        tenantId: response.tenant_id,
        accessToken: response.access_token,
      })
    } catch (error) {
      setError(describeApiError(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={cn('fixed inset-0 z-[80] flex items-center justify-center px-4 transition-all duration-150', open ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0')}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative z-10 w-full max-w-md rounded-[14px] border border-white/10 bg-[#091321] p-6 shadow-panel">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="eyebrow">Secure Access</p>
            <h3 className="mt-3 text-2xl font-semibold text-white">Sign in to QuantumRisk Oracle</h3>
            <p className="mt-2 text-sm leading-6 text-slate-300">Use the seeded institutional demo credentials or your issued account.</p>
          </div>
          <button type="button" onClick={onClose} className="text-sm text-slate-400 hover:text-white">
            Close
          </button>
        </div>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-200">Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="h-12 w-full rounded-[10px] border border-white/10 bg-white/5 px-4 text-sm text-white outline-none transition-colors duration-150 placeholder:text-slate-500 focus:border-blue-500/60"
              placeholder="admin@helios-oracle.com"
              required
            />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-200">Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="h-12 w-full rounded-[10px] border border-white/10 bg-white/5 px-4 text-sm text-white outline-none transition-colors duration-150 placeholder:text-slate-500 focus:border-blue-500/60"
              placeholder="QuantumRisk!2026"
              required
            />
          </label>

          {error ? <p className="rounded-[10px] border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p> : null}

          <div className="rounded-[10px] border border-white/8 bg-white/5 px-4 py-3 text-sm text-slate-300">
            Demo login: <span className="font-medium text-white">admin@helios-oracle.com</span> / <span className="font-medium text-white">QuantumRisk!2026</span>
          </div>

          <div className="flex flex-wrap gap-3 pt-2">
            <Button type="submit" loading={loading}>
              Sign In
            </Button>
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

function WorkspaceDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const activeView = useAppStore((state) => state.activeView)
  const setActiveView = useAppStore((state) => state.setActiveView)

  return (
    <div className={cn('fixed inset-0 z-[55] lg:hidden', open ? 'pointer-events-auto' : 'pointer-events-none')}>
      <div
        className={cn('absolute inset-0 bg-black/55 transition-opacity duration-180', open ? 'opacity-100' : 'opacity-0')}
        onClick={onClose}
      />
      <div
        className={cn(
          'absolute left-0 top-0 h-full w-[320px] max-w-[88vw] border-r border-white/10 bg-[#08121f] p-5 shadow-panel transition-transform duration-180',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-white">Workspace</p>
            <p className="text-xs text-slate-400">Treasury operations</p>
          </div>
          <button type="button" onClick={onClose} className="text-slate-300">
            Close
          </button>
        </div>
        <div className="space-y-1.5">
          {workspaceNavItems.map((item) => {
            const active = item.key === activeView
            return (
              <button
                key={item.key}
                type="button"
                onClick={() => {
                  setActiveView(item.key)
                  onClose()
                }}
                className={cn(
                  'flex h-11 w-full items-center rounded-xl px-3 text-sm transition-all duration-150',
                  active ? 'bg-blue-600/16 text-white shadow-[inset_0_0_0_1px_rgba(37,99,235,0.45)]' : 'text-slate-300 hover:bg-white/5 hover:text-white',
                )}
              >
                <span className="inline-flex size-8 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-[11px] font-semibold">
                  {item.short}
                </span>
                <span className="ml-3">{item.label}</span>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

const heroTrendData = [
  { label: 'Mon', risk: 49, var95: 6.1 },
  { label: 'Tue', risk: 53, var95: 6.8 },
  { label: 'Wed', risk: 57, var95: 7.3 },
  { label: 'Thu', risk: 55, var95: 7.0 },
  { label: 'Fri', risk: 61, var95: 7.9 },
]

const heroTailData = [
  { percentile: '90', loss: 4.2 },
  { percentile: '95', loss: 7.2, marker: 'VaR' as const },
  { percentile: '99', loss: 11.4 },
  { percentile: '99.5', loss: 15.1, marker: 'CVaR' as const },
]
