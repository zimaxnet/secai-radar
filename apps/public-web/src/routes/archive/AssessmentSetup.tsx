import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { getDomains } from '../api'

interface Props { tenantId: string }

const SETUP_STEPS = [
  { id: 1, title: 'Welcome', description: 'Introduction to assessment setup' },
  { id: 2, title: 'Tool Inventory', description: 'Configure security tools' },
  { id: 3, title: 'Scope Selection', description: 'Select security domains' },
  { id: 4, title: 'Review & Start', description: 'Review and begin assessment' }
]

export default function AssessmentSetup({ tenantId }: Props) {
  const [currentStep, setCurrentStep] = useState(1)
  const [domains, setDomains] = useState<any[]>([])
  const [selectedDomains, setSelectedDomains] = useState<Set<string>>(new Set())
  const navigate = useNavigate()

  useEffect(() => {
    getDomains().then(data => {
      // Handle both array and object formats
      let domainList: any[] = []
      if (Array.isArray(data)) {
        domainList = data
      } else if (data?.domains && typeof data.domains === 'object') {
        // Convert object format { NET: "Network Security", ... } to array
        domainList = Object.entries(data.domains).map(([code, name]) => ({ code, name }))
      }
      setDomains(domainList)
      // Pre-select all domains by default
      setSelectedDomains(new Set(domainList.map((domain: any) => domain.code)))
    })
  }, [])

  const toggleDomain = (domainCode: string) => {
    const newSelected = new Set(selectedDomains)
    if (newSelected.has(domainCode)) {
      newSelected.delete(domainCode)
    } else {
      newSelected.add(domainCode)
    }
    setSelectedDomains(newSelected)
  }

  const handleNext = () => {
    if (currentStep < SETUP_STEPS.length) {
      setCurrentStep(currentStep + 1)
    } else {
      // Complete setup and navigate to assessment overview
      navigate(`/tenant/${tenantId}/assessment`)
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleStartAssessment = () => {
    navigate(`/tenant/${tenantId}/assessment`)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Link to="/assessments" className="text-blue-600 hover:underline text-sm mb-4 inline-block">
            ← Back to Assessments
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Assessment Setup</h1>
          <p className="text-gray-600">Configure your SecAI Framework assessment</p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            {SETUP_STEPS.map((step, idx) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                    currentStep > step.id ? 'bg-green-500 text-white' :
                    currentStep === step.id ? 'bg-blue-600 text-white' :
                    'bg-gray-200 text-gray-600'
                  }`}>
                    {currentStep > step.id ? '✓' : step.id}
                  </div>
                  <div className="mt-2 text-center">
                    <div className={`text-sm font-semibold ${
                      currentStep >= step.id ? 'text-gray-900' : 'text-gray-500'
                    }`}>
                      {step.title}
                    </div>
                    <div className="text-xs text-gray-500 hidden md:block">{step.description}</div>
                  </div>
                </div>
                {idx < SETUP_STEPS.length - 1 && (
                  <div className={`h-1 flex-1 mx-2 ${
                    currentStep > step.id ? 'bg-green-500' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Step 1: Welcome */}
          {currentStep === 1 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to SecAI Assessment Setup</h2>
              <p className="text-gray-700 mb-6">
                This setup wizard will help you configure your security assessment. 
                The process takes about 5-10 minutes and covers:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 mb-6">
                <li>Identifying your security tool inventory</li>
                <li>Selecting which security domains to assess</li>
                <li>Reviewing your assessment scope</li>
              </ul>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="text-sm font-semibold text-blue-900 mb-2">About the SecAI Framework</div>
                <p className="text-sm text-blue-800">
                  The SecAI Framework uses a <strong>capability-based approach</strong> to security assessments. 
                  Instead of focusing on specific tools, we map controls to capabilities and measure how well 
                  your tools cover those capabilities. This provides a vendor-neutral, explainable assessment.
                </p>
              </div>
            </div>
          )}

          {/* Step 2: Tool Inventory */}
          {currentStep === 2 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Security Tool Inventory</h2>
              <p className="text-gray-700 mb-6">
                Which security tools does this organization currently use? 
                You can add or modify tools later, but setting up your tool inventory now helps 
                the system calculate coverage scores accurately.
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <div className="text-sm font-semibold text-yellow-900 mb-2">💡 Tip</div>
                <p className="text-sm text-yellow-800">
                  Don't worry about getting this perfect right now. You can always add tools, 
                  adjust configuration scores, and refine your inventory as you work through the assessment.
                </p>
              </div>
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">Tool inventory management is available after setup.</p>
                <Link
                  to={`/tenant/${tenantId}/tools`}
                  className="text-blue-600 hover:underline font-semibold"
                >
                  Manage Tools →
                </Link>
              </div>
            </div>
          )}

          {/* Step 3: Scope Selection */}
          {currentStep === 3 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Select Security Domains</h2>
              <p className="text-gray-700 mb-6">
                Which security domains should be included in this assessment? 
                We recommend assessing all domains for a comprehensive evaluation, 
                but you can customize based on your needs.
              </p>
              <div className="mb-4 flex gap-4">
                <button
                  onClick={() => setSelectedDomains(new Set(domains.map((d: any) => d.code)))}
                  className="text-sm text-blue-600 hover:underline"
                >
                  Select All
                </button>
                <button
                  onClick={() => setSelectedDomains(new Set())}
                  className="text-sm text-gray-600 hover:underline"
                >
                  Clear All
                </button>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                {domains.map((domain: any) => (
                  <div
                    key={domain.code}
                    onClick={() => toggleDomain(domain.code)}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      selectedDomains.has(domain.code)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-semibold text-gray-900">{domain.code}</div>
                        <div className="text-sm text-gray-600">{domain.name}</div>
                      </div>
                      <div className={`w-6 h-6 rounded border-2 flex items-center justify-center ${
                        selectedDomains.has(domain.code)
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-gray-300'
                      }`}>
                        {selectedDomains.has(domain.code) && (
                          <span className="text-white text-sm">✓</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">
                  <strong>{selectedDomains.size}</strong> domain{selectedDomains.size !== 1 ? 's' : ''} selected
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Review & Start */}
          {currentStep === 4 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Review & Start Assessment</h2>
              <p className="text-gray-700 mb-6">
                Review your assessment configuration and start your SecAI Framework assessment.
              </p>
              <div className="space-y-4 mb-6">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm font-semibold text-gray-700 mb-1">Tenant</div>
                  <div className="text-lg text-gray-900">{tenantId}</div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm font-semibold text-gray-700 mb-1">Security Domains Selected</div>
                  <div className="text-lg text-gray-900">{selectedDomains.size} domains</div>
                  <div className="text-sm text-gray-600 mt-2">
                    {Array.from(selectedDomains).join(', ')}
                  </div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm font-semibold text-gray-700 mb-1">Next Steps</div>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    <li>Import controls for selected domains</li>
                    <li>Configure security tool inventory</li>
                    <li>Begin domain-by-domain assessment</li>
                  </ul>
                </div>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="text-sm font-semibold text-blue-900 mb-2">Ready to Start?</div>
                <p className="text-sm text-blue-800">
                  You can always modify your tool inventory and add more controls later. 
                  Let's begin your assessment!
                </p>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
            <button
              onClick={handleBack}
              disabled={currentStep === 1}
              className={`px-6 py-2 rounded-lg font-semibold ${
                currentStep === 1
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              ← Back
            </button>
            {currentStep < SETUP_STEPS.length ? (
              <button
                onClick={handleNext}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
              >
                Next →
              </button>
            ) : (
              <button
                onClick={handleStartAssessment}
                className="px-6 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
              >
                Start Assessment →
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

