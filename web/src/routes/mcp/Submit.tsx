/**
 * Submit Evidence Page (/mcp/submit)
 * 
 * Purpose: Allow providers and customers to submit evidence packs
 * Based on Step 6: MVP PRD + UI Component Spec
 */

import { useState } from 'react'
import { DISCLAIMERS } from '../../utils/copy'
import Disclaimer from '../../components/mcp/Disclaimer'
import { trackSubmitEvidenceStarted, trackSubmitEvidenceCompleted } from '../../utils/analytics'

type SubmissionType = 'provider' | 'customer' | null

export default function Submit() {
  const [submissionType, setSubmissionType] = useState<SubmissionType>(null)
  const [formData, setFormData] = useState({
    contactEmail: '',
    serverUrl: '',
    repoUrl: '',
    evidenceLinks: '',
    notes: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    
    trackSubmitEvidenceStarted(formData.serverUrl ? undefined : undefined, undefined)

    // TODO: Implement actual submission API call
    // POST /api/v1/public/mcp/submit-evidence
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    trackSubmitEvidenceCompleted(undefined, undefined, true)
    setSubmitting(false)
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="space-y-6">
        <h1 className="text-4xl font-bold text-white mb-4">Evidence Submitted</h1>
        <div className="bg-green-500/20 border border-green-500/30 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-2">Thank you for your submission!</h2>
          <p className="text-slate-300 mb-4">
            We've received your evidence submission. Our team will review it and update the relevant server's Trust Score and Evidence Confidence accordingly.
          </p>
          <p className="text-sm text-slate-400">
            You'll receive a confirmation email at {formData.contactEmail} shortly.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Submit Evidence</h1>
        <p className="text-slate-400">Help improve MCP server verification by submitting evidence</p>
      </div>

      {/* Choose Submission Type */}
      {!submissionType && (
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">I am a...</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => {
                setSubmissionType('provider')
                trackSubmitEvidenceStarted(undefined, undefined)
              }}
              className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-blue-500/50 hover:bg-slate-800 transition-colors text-left"
            >
              <h3 className="text-lg font-semibold text-white mb-2">Provider / Vendor</h3>
              <p className="text-sm text-slate-400">
                Submit evidence for your MCP server to improve Trust Score and Evidence Confidence
              </p>
            </button>
            <button
              onClick={() => {
                setSubmissionType('customer')
                trackSubmitEvidenceStarted(undefined, undefined)
              }}
              className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-blue-500/50 hover:bg-slate-800 transition-colors text-left"
            >
              <h3 className="text-lg font-semibold text-white mb-2">Customer / User</h3>
              <p className="text-sm text-slate-400">
                Submit evidence you've discovered about an MCP server
              </p>
            </button>
          </div>
        </div>
      )}

      {/* Submission Form */}
      {submissionType && (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              {submissionType === 'provider' ? 'Provider Evidence Submission' : 'Customer Evidence Submission'}
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Contact Email *
                </label>
                <input
                  type="email"
                  required
                  value={formData.contactEmail}
                  onChange={(e) => setFormData({ ...formData, contactEmail: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  placeholder="your@email.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Server URL / Repository *
                </label>
                <input
                  type="url"
                  required
                  value={formData.serverUrl || formData.repoUrl}
                  onChange={(e) => {
                    const url = e.target.value
                    if (url.includes('github.com') || url.includes('gitlab.com')) {
                      setFormData({ ...formData, repoUrl: url, serverUrl: '' })
                    } else {
                      setFormData({ ...formData, serverUrl: url, repoUrl: '' })
                    }
                  }}
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  placeholder="https://github.com/org/mcp-server or https://mcp.example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Evidence Links *
                </label>
                <textarea
                  required
                  value={formData.evidenceLinks}
                  onChange={(e) => setFormData({ ...formData, evidenceLinks: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  rows={4}
                  placeholder="One URL per line:&#10;https://docs.example.com/security&#10;https://example.com/security-report.pdf"
                />
                <p className="text-xs text-slate-400 mt-1">
                  Provide links to documentation, security reports, attestations, or other verifiable evidence
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Additional Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  rows={3}
                  placeholder="Any additional context or information..."
                />
              </div>

              {submissionType === 'provider' && (
                <div>
                  <label className="flex items-start gap-3 text-sm text-slate-300">
                    <input
                      type="checkbox"
                      required
                      className="mt-1 rounded"
                    />
                    <span>
                      I acknowledge that this is <strong className="text-white">not a certification</strong> and that we may publish a response status on the server detail page.
                    </span>
                  </label>
                </div>
              )}
            </div>
          </div>

          {/* Disclaimers */}
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-6">
            <h3 className="text-sm font-semibold text-yellow-400 mb-2">Important Notes</h3>
            <Disclaimer variant="short" className="text-slate-300" />
            <p className="text-xs text-slate-400 mt-3">
              By submitting evidence, you agree that we may review, validate, and reference it in our Trust Score assessments.
              {submissionType === 'provider' && ' Provider response status will be visible on server detail pages.'}
            </p>
          </div>

          {/* Submit Button */}
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => {
                setSubmissionType(null)
                setFormData({
                  contactEmail: '',
                  serverUrl: '',
                  repoUrl: '',
                  evidenceLinks: '',
                  notes: '',
                })
              }}
              className="px-6 py-3 bg-slate-800 text-slate-300 rounded-lg font-medium hover:bg-slate-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Submitting...' : 'Submit Evidence'}
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

