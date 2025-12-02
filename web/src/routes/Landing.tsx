import { Link } from 'react-router-dom'
import GlassCard from '../components/ui/GlassCard'

const demoTenantId = (import.meta.env.VITE_DEFAULT_TENANT as string) || 'CONTOSO'

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 font-sans text-white">
      {/* Navigation */}
      <nav className="container mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-cyan-400 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/30">S</div>
          <span className="text-xl font-bold text-white">SecAI Radar</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
          <a href="#" className="hover:text-blue-400 transition-colors">Home</a>
          <a href="#features" className="hover:text-blue-400 transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-blue-400 transition-colors">How It Works</a>
          <a href="#" className="hover:text-blue-400 transition-colors">Pricing</a>
          <a href="#" className="hover:text-blue-400 transition-colors">Contact</a>
        </div>
        <button className="px-5 py-2 bg-gradient-to-r from-blue-600 to-cyan-400 text-white text-sm font-semibold rounded-full hover:from-blue-700 hover:to-cyan-500 transition-all shadow-lg shadow-blue-500/30">
          Login
        </button>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-16 pb-24 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 tracking-tight text-glow">
          SecAI Radar
        </h1>
        <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
          Vendor-Neutral Azure Security Assessment Platform
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <Link
            to={`/tenant/${demoTenantId}/assessment`}
            data-tour="explore-demo"
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-cyan-400 text-white rounded-full font-semibold hover:from-blue-700 hover:to-cyan-500 transition-all shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40"
          >
            Explore Interactive Demo
          </Link>
          <Link
            to="/assessments"
            className="px-8 py-3 bg-slate-800/60 backdrop-blur-xl text-blue-400 border border-white/10 rounded-full font-semibold hover:bg-slate-800/80 hover:border-blue-500/30 transition-all shadow-lg"
          >
            Start New Assessment
          </Link>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="container mx-auto px-4 mb-24" id="features">
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <GlassCard className="p-6 flex items-start gap-4">
            <div className="p-3 bg-blue-500/20 text-blue-400 rounded-xl border border-blue-500/30">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <div>
              <h3 className="font-bold text-white mb-1">Vendor-Neutral</h3>
              <p className="text-sm text-slate-400">Unbiased security assessment without platform lock-in.</p>
            </div>
          </GlassCard>
          <GlassCard className="p-6 flex items-start gap-4">
            <div className="p-3 bg-cyan-500/20 text-cyan-400 rounded-xl border border-cyan-500/30">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            </div>
            <div>
              <h3 className="font-bold text-white mb-1">Explainable</h3>
              <p className="text-sm text-slate-400">Clear insights into security posture and decision-making.</p>
            </div>
          </GlassCard>
          <GlassCard className="p-6 flex items-start gap-4">
            <div className="p-3 bg-green-500/20 text-green-400 rounded-xl border border-green-500/30">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
            </div>
            <div>
              <h3 className="font-bold text-white mb-1">Actionable</h3>
              <p className="text-sm text-slate-400">Prioritized recommendations to improve security instantly.</p>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* How It Works */}
      <div className="container mx-auto px-4 mb-24" id="how-it-works">
        <h2 className="text-2xl font-bold text-white mb-12 text-center">How It Works</h2>
        <div className="relative max-w-6xl mx-auto">
          {/* Connecting Line */}
          <div className="hidden md:block absolute top-6 left-0 w-full h-0.5 bg-gradient-to-r from-blue-600/50 via-cyan-400/50 to-blue-600/50 -z-10"></div>
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-8 text-center">
            {[
              { step: 1, title: 'Configure', desc: 'Set up your environment and define scope.' },
              { step: 2, title: 'Assess', desc: 'Automated scanning and analysis.' },
              { step: 3, title: 'Gaps', desc: 'Identify security gaps and vulnerabilities.' },
              { step: 4, title: 'Recommendations', desc: 'Get prioritized, actionable insights.' },
              { step: 5, title: 'Report', desc: 'Generate comprehensive security reports.' },
            ].map((item) => (
              <div key={item.step} className="bg-transparent">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-cyan-400 text-white rounded-full flex items-center justify-center font-bold text-lg mx-auto mb-4 shadow-lg shadow-blue-500/30 border-4 border-slate-800">
                  {item.step}
                </div>
                <h3 className="font-bold text-white mb-2">{item.title}</h3>
                <p className="text-xs text-slate-400 px-2">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Security Domains */}
      <div className="container mx-auto px-4 mb-24">
        <h2 className="text-2xl font-bold text-white mb-8 text-center">Security Domains</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 max-w-6xl mx-auto">
          {[
            { code: 'NET', name: 'Network Security' },
            { code: 'ID', name: 'Identity' },
            { code: 'DATA', name: 'Data Protection' },
            { code: 'APP', name: 'Application Security' },
            { code: 'DEV', name: 'DevSecOps' },
            { code: 'CLOUD', name: 'Cloud Security' },
            { code: 'END', name: 'Endpoint Security' },
            { code: 'IOT', name: 'IoT Security' },
            { code: 'OPS', name: 'Security Operations' },
            { code: 'COMP', name: 'Compliance' },
            { code: 'THREAT', name: 'Threat Intel' },
            { code: 'GOV', name: 'Governance' }
          ].map(domain => (
            <GlassCard key={domain.code} hoverEffect className="p-4 flex items-center gap-3 cursor-default">
              <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs font-bold rounded border border-blue-500/30">{domain.code}</span>
              <div className="text-left">
                <div className="text-xs font-bold text-white">{domain.code}</div>
                <div className="text-[10px] text-slate-400 truncate max-w-[80px]">{domain.name}</div>
              </div>
            </GlassCard>
          ))}
        </div>
      </div>

      {/* Demo Journey */}
      <div className="container mx-auto px-4 mb-24">
        <h2 className="text-2xl font-bold text-white mb-8 text-center">Walk the Demo Experience</h2>
        <div className="grid md:grid-cols-4 gap-6 max-w-6xl mx-auto">
          {[
            {
              title: 'Dashboard',
              desc: 'Visualize your security posture at a glance.',
              to: `/tenant/${demoTenantId}/dashboard`,
              gradient: 'from-blue-600/20 to-cyan-400/20'
            },
            {
              title: 'Tool Inventory',
              desc: 'Manage and audit your entire security stack.',
              to: `/tenant/${demoTenantId}/tools`,
              gradient: 'from-purple-600/20 to-blue-500/20'
            },
            {
              title: 'Gap Analysis',
              desc: 'Identify and prioritize critical security gaps.',
              to: `/tenant/${demoTenantId}/gaps`,
              gradient: 'from-red-600/20 to-orange-500/20'
            },
             {
              title: 'Executive Report',
              desc: 'Generate summary and remediation plans.',
              to: `/tenant/${demoTenantId}/report`,
              gradient: 'from-green-600/20 to-emerald-500/20'
            },
          ].map((item, i) => (
            <Link key={i} to={item.to}>
              <GlassCard hoverEffect className="overflow-hidden">
                <div className={`h-32 bg-gradient-to-br ${item.gradient} flex items-center justify-center`}>
                  {/* Placeholder UI illustration */}
                  <div className="w-24 h-16 bg-white/10 backdrop-blur-sm rounded shadow-lg border border-white/10"></div>
                </div>
                <div className="p-5">
                  <h3 className="font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">{item.title}</h3>
                  <p className="text-xs text-slate-400">{item.desc}</p>
                </div>
              </GlassCard>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

