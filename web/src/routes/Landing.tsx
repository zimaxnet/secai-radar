import { Link } from 'react-router-dom'

const demoTenantId = (import.meta.env.VITE_DEFAULT_TENANT as string) || 'CONTOSO'

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 font-sans text-gray-900">
      {/* Navigation */}
      <nav className="container mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">S</div>
          <span className="text-xl font-bold text-gray-900">SecAI Radar</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600">
          <a href="#" className="hover:text-blue-600 transition-colors">Home</a>
          <a href="#features" className="hover:text-blue-600 transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-blue-600 transition-colors">How It Works</a>
          <a href="#" className="hover:text-blue-600 transition-colors">Pricing</a>
          <a href="#" className="hover:text-blue-600 transition-colors">Contact</a>
        </div>
        <button className="px-5 py-2 bg-blue-600 text-white text-sm font-semibold rounded-full hover:bg-blue-700 transition-colors shadow-sm">
          Login
        </button>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-16 pb-24 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 tracking-tight">
          SecAI Radar
        </h1>
        <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
          Vendor-Neutral Azure Security Assessment Platform
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <Link
            to={`/tenant/${demoTenantId}/assessment`}
            data-tour="explore-demo"
            className="px-8 py-3 bg-blue-600 text-white rounded-full font-semibold hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
          >
            Explore Interactive Demo
          </Link>
          <Link
            to="/assessments"
            className="px-8 py-3 bg-white text-blue-600 border border-gray-200 rounded-full font-semibold hover:bg-gray-50 transition-colors shadow-sm"
          >
            Start New Assessment
          </Link>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="container mx-auto px-4 mb-24" id="features">
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-start gap-4">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">Vendor-Neutral</h3>
              <p className="text-sm text-gray-600">Unbiased security assessment without platform lock-in.</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-start gap-4">
            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">Explainable</h3>
              <p className="text-sm text-gray-600">Clear insights into security posture and decision-making.</p>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-start gap-4">
            <div className="p-3 bg-green-50 text-green-600 rounded-xl">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
            </div>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">Actionable</h3>
              <p className="text-sm text-gray-600">Prioritized recommendations to improve security instantly.</p>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="container mx-auto px-4 mb-24" id="how-it-works">
        <h2 className="text-2xl font-bold text-gray-900 mb-12 text-center">How It Works</h2>
        <div className="relative max-w-6xl mx-auto">
          {/* Connecting Line */}
          <div className="hidden md:block absolute top-6 left-0 w-full h-0.5 bg-gray-200 -z-10"></div>
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-8 text-center">
            {[
              { step: 1, title: 'Configure', desc: 'Set up your environment and define scope.' },
              { step: 2, title: 'Assess', desc: 'Automated scanning and analysis.' },
              { step: 3, title: 'Gaps', desc: 'Identify security gaps and vulnerabilities.' },
              { step: 4, title: 'Recommendations', desc: 'Get prioritized, actionable insights.' },
              { step: 5, title: 'Report', desc: 'Generate comprehensive security reports.' },
            ].map((item) => (
              <div key={item.step} className="bg-transparent">
                <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg mx-auto mb-4 shadow-md border-4 border-white">
                  {item.step}
                </div>
                <h3 className="font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-xs text-gray-500 px-2">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Security Domains */}
      <div className="container mx-auto px-4 mb-24">
        <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Security Domains</h2>
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
            <div key={domain.code} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-3 hover:shadow-md transition-shadow cursor-default">
              <span className="px-2 py-1 bg-blue-50 text-blue-600 text-xs font-bold rounded">{domain.code}</span>
              <div className="text-left">
                <div className="text-xs font-bold text-gray-900">{domain.code}</div>
                <div className="text-[10px] text-gray-500 truncate max-w-[80px]">{domain.name}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Demo Journey */}
      <div className="container mx-auto px-4 mb-24">
        <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Walk the Demo Experience</h2>
        <div className="grid md:grid-cols-4 gap-6 max-w-6xl mx-auto">
          {[
            {
              title: 'Dashboard',
              desc: 'Visualize your security posture at a glance.',
              to: `/tenant/${demoTenantId}/dashboard`,
              img: 'bg-blue-100' // Placeholder for image
            },
            {
              title: 'Tool Inventory',
              desc: 'Manage and audit your entire security stack.',
              to: `/tenant/${demoTenantId}/tools`,
              img: 'bg-indigo-100'
            },
            {
              title: 'Gap Analysis',
              desc: 'Identify and prioritize critical security gaps.',
              to: `/tenant/${demoTenantId}/gaps`,
              img: 'bg-purple-100'
            },
             {
              title: 'Executive Report',
              desc: 'Generate summary and remediation plans.',
              to: `/tenant/${demoTenantId}/report`,
              img: 'bg-green-100'
            },
          ].map((item, i) => (
            <Link key={i} to={item.to} className="group bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition-all">
              <div className={`h-32 ${item.img} flex items-center justify-center`}>
                {/* Placeholder UI illustration */}
                <div className="w-24 h-16 bg-white/50 rounded shadow-sm"></div>
              </div>
              <div className="p-5">
                <h3 className="font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">{item.title}</h3>
                <p className="text-xs text-gray-500">{item.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

