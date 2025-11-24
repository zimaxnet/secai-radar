import { useState } from 'react'
import { postTools } from '../api'

interface Props { tenantId: string }

export default function Tools({ tenantId }: Props) {
  const [vendorToolId, setVendorToolId] = useState('')
  const [enabled, setEnabled] = useState(true)
  const [configScore, setConfigScore] = useState(0.8)
  const [message, setMessage] = useState<string | null>(null)
  const [messageType, setMessageType] = useState<'success' | 'error' | null>(null)
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    if (!vendorToolId.trim()) {
      setMessage('Vendor Tool ID is required')
      setMessageType('error')
      return
    }
    
    setMessage(null)
    setMessageType(null)
    setLoading(true)
    
    try {
      const res = await postTools(tenantId, { vendorToolId, Enabled: enabled, ConfigScore: configScore })
      if (res?.ok) {
        setMessage('Tool configuration saved successfully')
        setMessageType('success')
        // Reset form
        setVendorToolId('')
        setEnabled(true)
        setConfigScore(0.8)
      } else {
        setMessage('Error saving tool configuration')
        setMessageType('error')
      }
    } catch (err) {
      setMessage('Failed to save tool configuration')
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Tools</h1>
        <p className="mt-1 text-sm text-slate-600">Configure security tools and their configuration scores</p>
      </div>

      <div className="card p-6 max-w-2xl">
        <h2 className="text-lg font-semibold text-slate-900 mb-6">Add Tool Configuration</h2>
        
        {message && (
          <div className={`alert mb-6 ${messageType === 'success' ? 'alert-success' : 'alert-error'}`}>
            {message}
          </div>
        )}

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Vendor Tool ID <span className="text-red-500">*</span>
            </label>
            <input
              className="input-field"
              value={vendorToolId}
              onChange={e => setVendorToolId(e.target.value)}
              placeholder="e.g., wiz-cspm, crowdstrike-falcon"
            />
            <p className="mt-1 text-xs text-slate-500">Enter the tool identifier from the catalog</p>
          </div>

          <div className="flex items-center space-x-3 p-4 bg-slate-50 rounded-md">
            <input
              type="checkbox"
              id="enabled"
              checked={enabled}
              onChange={e => setEnabled(e.target.checked)}
              className="w-4 h-4 text-slate-900 border-slate-300 rounded focus:ring-slate-500"
            />
            <label htmlFor="enabled" className="text-sm font-medium text-slate-700">
              Tool is enabled
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Configuration Score <span className="text-slate-500">(0.0 - 1.0)</span>
            </label>
            <div className="space-y-2">
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={configScore}
                onChange={e => setConfigScore(parseFloat(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-900"
              />
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500">0.0</span>
                <span className="text-sm font-semibold text-slate-900">{configScore.toFixed(2)}</span>
                <span className="text-xs text-slate-500">1.0</span>
              </div>
            </div>
            <p className="mt-2 text-xs text-slate-500">
              Configuration quality score. Higher values indicate better configuration quality.
            </p>
          </div>

          <div className="pt-4 border-t border-slate-200">
            <button
              onClick={submit}
              disabled={loading || !vendorToolId.trim()}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="spinner mr-2"></div>
                  Saving...
                </>
              ) : (
                'Save Tool Configuration'
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="card p-6 max-w-2xl">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Configuration Score Guide</h2>
        <div className="space-y-3 text-sm text-slate-600">
          <div className="flex items-start">
            <span className="font-medium text-slate-900 mr-2">0.9 - 1.0:</span>
            <span>Excellent configuration, fully optimized</span>
          </div>
          <div className="flex items-start">
            <span className="font-medium text-slate-900 mr-2">0.7 - 0.89:</span>
            <span>Good configuration, minor improvements possible</span>
          </div>
          <div className="flex items-start">
            <span className="font-medium text-slate-900 mr-2">0.5 - 0.69:</span>
            <span>Fair configuration, significant improvements needed</span>
          </div>
          <div className="flex items-start">
            <span className="font-medium text-slate-900 mr-2">0.0 - 0.49:</span>
            <span>Poor configuration, major improvements required</span>
          </div>
        </div>
      </div>
    </div>
  )
}
