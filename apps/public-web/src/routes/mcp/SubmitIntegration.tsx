import { useState } from 'react'
import { submitIntegration } from '../../api/public'

export default function SubmitIntegration() {
    const [formData, setFormData] = useState({
        contactEmail: '',
        repoUrl: '',
        integrationType: 'mcp',
    })
    const [submitting, setSubmitting] = useState(false)
    const [submitted, setSubmitted] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSubmitting(true)
        setError(null)

        try {
            await submitIntegration({
                repoUrl: formData.repoUrl,
                integrationType: formData.integrationType as 'mcp' | 'agent',
                contactEmail: formData.contactEmail || undefined,
            })
            setSubmitted(true)
        } catch (err: any) {
            setError(err.message || 'Failed to submit integration')
        } finally {
            setSubmitting(false)
        }
    }

    if (submitted) {
        return (
            <div className="space-y-6">
                <h1 className="text-4xl font-bold text-white mb-4">Integration Submitted</h1>
                <div className="bg-green-500/20 border border-green-500/30 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-2">Thank you!</h2>
                    <p className="text-slate-300 mb-4">
                        We've queued your repository for ingestion and verification. Our scouts will analyze the repository soon.
                    </p>
                    <button
                        onClick={() => {
                            setSubmitted(false);
                            setFormData({ contactEmail: '', repoUrl: '', integrationType: 'mcp' });
                        }}
                        className="text-blue-400 hover:text-blue-300 font-medium"
                    >
                        Submit Another Integration
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6 max-w-2xl">
            <div>
                <h1 className="text-4xl font-bold text-white mb-2">Submit Integration</h1>
                <p className="text-slate-400">Add an MCP Server or AI Agent to the SecAI Radar verification pipeline.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-4">

                    {error && (
                        <div className="bg-red-500/10 border border-red-500/30 text-red-500 rounded p-4 text-sm">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Integration Type *
                        </label>
                        <select
                            title="Integration Type"
                            value={formData.integrationType}
                            onChange={(e) => setFormData({ ...formData, integrationType: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                        >
                            <option value="mcp">MCP Server</option>
                            <option value="agent">AI Agent</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Repository URL *
                        </label>
                        <input
                            type="url"
                            required
                            value={formData.repoUrl}
                            onChange={(e) => setFormData({ ...formData, repoUrl: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                            placeholder="https://github.com/your-org/your-repo"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Contact Email (Optional)
                        </label>
                        <input
                            type="email"
                            value={formData.contactEmail}
                            onChange={(e) => setFormData({ ...formData, contactEmail: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                            placeholder="you@company.com"
                        />
                        <p className="text-xs text-slate-400 mt-1">
                            We'll notify you if we encounter issues verifying your integration.
                        </p>
                    </div>

                </div>

                <div className="flex justify-end">
                    <button
                        type="submit"
                        disabled={submitting}
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {submitting ? 'Submitting...' : 'Queue for Verification'}
                    </button>
                </div>
            </form>
        </div>
    )
}
