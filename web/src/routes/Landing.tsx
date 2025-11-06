import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            SecAI Radar
          </h1>
          <p className="text-2xl text-gray-700 mb-4">
            Vendor-Neutral Azure Security Assessment Platform
          </p>
          <p className="text-lg text-gray-600 mb-8">
            Based on the SecAI Framework — Capability-driven, explainable, and actionable security assessments
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/assessments"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg"
            >
              Start New Assessment
            </Link>
            <Link
              to="/assessments"
              className="px-8 py-3 bg-white text-blue-600 border-2 border-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              Continue Assessment
            </Link>
          </div>
        </div>

        {/* What is SecAI Framework */}
        <div className="max-w-6xl mx-auto mb-16">
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">What is the SecAI Framework?</h2>
            <p className="text-lg text-gray-700 mb-6">
              The SecAI Framework provides a <strong>vendor-neutral, capability-driven approach</strong> to security assessments. 
              Instead of focusing on specific tools (like Sentinel), we map security controls to <strong>capability requirements</strong> 
              and measure how well your actual security tools cover those capabilities.
            </p>
            <div className="grid md:grid-cols-3 gap-6 mt-8">
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl mb-2">🎯</div>
                <h3 className="font-semibold text-gray-900 mb-2">Vendor-Neutral</h3>
                <p className="text-sm text-gray-700">
                  Works with any security tool stack — Google SecOps, Palo Alto, Wiz, CrowdStrike, Azure Defender, and more.
                </p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-2xl mb-2">📊</div>
                <h3 className="font-semibold text-gray-900 mb-2">Explainable</h3>
                <p className="text-sm text-gray-700">
                  Every score is reproducible and explainable. See exactly which capabilities matter and which tools cover them.
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl mb-2">✅</div>
                <h3 className="font-semibold text-gray-900 mb-2">Actionable</h3>
                <p className="text-sm text-gray-700">
                  Clear gap analysis with specific recommendations — tune existing tools or identify new capabilities needed.
                </p>
              </div>
            </div>
          </div>

          {/* Assessment Process */}
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">How It Works</h2>
            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  1
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Configure Your Environment</h3>
                  <p className="text-gray-700">
                    Identify which security tools your organization uses and their configuration quality. 
                    This creates your tool inventory.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  2
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Assess Security Domains</h3>
                  <p className="text-gray-700">
                    Work through 12 security domains (Network, Identity, Data Protection, etc.). 
                    For each control, document evidence, enter observations, and review coverage.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  3
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Identify Gaps</h3>
                  <p className="text-gray-700">
                    The system automatically calculates coverage scores and identifies gaps — 
                    both hard gaps (missing capabilities) and soft gaps (configuration issues).
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  4
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Get Recommendations</h3>
                  <p className="text-gray-700">
                    Receive AI-powered recommendations for addressing gaps. 
                    Prioritize tuning existing tools before suggesting new investments.
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  5
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Generate Report</h3>
                  <p className="text-gray-700">
                    Create comprehensive assessment reports with executive summaries, 
                    gap analysis, and actionable remediation plans.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Security Domains */}
          <div className="bg-white rounded-lg shadow-lg p-8 mt-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">12 Security Domains</h2>
            <p className="text-gray-700 mb-6">
              SecAI Radar assesses security across 12 comprehensive domains, each mapped to industry frameworks 
              (CIS Controls, NIST CSF, Azure Security Benchmark).
            </p>
            <div className="grid md:grid-cols-3 gap-4">
              {[
                { code: 'NET', name: 'Network Security' },
                { code: 'ID', name: 'Identity Management' },
                { code: 'PA', name: 'Privileged Access' },
                { code: 'DATA', name: 'Data Protection' },
                { code: 'ASSET', name: 'Asset Management' },
                { code: 'LOG', name: 'Logging & Threat Detection' },
                { code: 'IR', name: 'Incident Response' },
                { code: 'POST', name: 'Posture & Vulnerability Management' },
                { code: 'END', name: 'Endpoint Security' },
                { code: 'BAK', name: 'Backup & Recovery' },
                { code: 'DEV', name: 'DevOps Security' },
                { code: 'GOV', name: 'Governance & Strategy' }
              ].map(domain => (
                <div key={domain.code} className="p-3 bg-gray-50 rounded border border-gray-200">
                  <span className="font-semibold text-gray-900">{domain.code}</span>
                  <span className="text-gray-600 ml-2">— {domain.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-blue-600 text-white rounded-lg p-8">
            <h2 className="text-2xl font-bold mb-4">Ready to Start Your Assessment?</h2>
            <p className="text-blue-100 mb-6">
              Begin your vendor-neutral security assessment using the SecAI Framework. 
              Get started in minutes, complete at your own pace.
            </p>
            <Link
              to="/assessments"
              className="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              Start Assessment →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

