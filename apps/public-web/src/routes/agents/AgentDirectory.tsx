import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getAgentRankings } from '../../api/public'
import { trackPageView } from '../../utils/analytics'
import { AgentDisclaimer } from '../../components/AgentDisclaimer'

interface AgentRankingItem {
    rank: number
    agentId: string
    agentSlug: string
    agentName: string
    categoryPrimary: string
    agentType: string
    trustScore: number
    tier: 'A' | 'B' | 'C' | 'D'
    evidenceConfidence: number
    lastAssessedAt: string
}

export default function AgentDirectory() {
    const [agents, setAgents] = useState<AgentRankingItem[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        trackPageView('/agents/directory')

        const fetchAgents = async () => {
            setLoading(true)
            try {
                const result = await getAgentRankings(1, 50)
                setAgents(result.items.map((item: any, index: number) => ({
                    rank: index + 1,
                    agentId: item.agentId || '',
                    agentSlug: item.agentSlug || '',
                    agentName: item.agentName || 'Unknown',
                    categoryPrimary: item.categoryPrimary || 'Unknown',
                    agentType: item.agentType || 'Unknown',
                    trustScore: item.trustScore || 0,
                    tier: item.tier || 'D',
                    evidenceConfidence: item.evidenceConfidence || 0,
                    lastAssessedAt: item.lastAssessedAt || '',
                })))
            } catch (error) {
                console.error('Error fetching agents:', error)
            } finally {
                setLoading(false)
            }
        }
        fetchAgents()
    }, [])

    const getTierColor = (tier: string) => {
        switch (tier) {
            case 'A': return 'text-green-400 bg-green-500/20'
            case 'B': return 'text-blue-400 bg-blue-500/20'
            case 'C': return 'text-yellow-400 bg-yellow-500/20'
            case 'D': return 'text-red-400 bg-red-500/20'
            default: return 'text-slate-400 bg-slate-500/20'
        }
    }

    if (loading) {
        return (
            <div className="flex h-64 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
            </div>
        )
    }

    return (
        <section aria-labelledby="agent-directory-title" className="space-y-6">
            <AgentDisclaimer />

            <header className="flex items-center justify-between">
                <div>
                    <h1 id="agent-directory-title" className="text-4xl font-bold text-white mb-2">Verified Agents Directory</h1>
                    <p className="text-slate-400">Trust-first exploration of third-party Agents</p>
                </div>
            </header>

            <div role="region" aria-label="Agent Rankings Table" className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden mt-6">
                <table className="w-full">
                    <thead className="bg-slate-800/50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Rank</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Agent</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Type</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Category</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Trust Score</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Evidence</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase">Last Verified</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                        {agents.map((item) => (
                            <tr key={item.agentId} className="hover:bg-slate-800/30 transition-colors">
                                <td className="px-6 py-4 whitespace-nowrap text-slate-400">#{item.rank}</td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {item.agentSlug ? (
                                        <Link to={`/agents/${item.agentSlug}`} className="text-white hover:text-blue-400 font-medium">
                                            {item.agentName}
                                        </Link>
                                    ) : (
                                        <span className="text-white font-medium">{item.agentName}</span>
                                    )}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-slate-400">{item.agentType}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-slate-400">{item.categoryPrimary}</td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center gap-2">
                                        <span className="text-white font-semibold">{item.trustScore}</span>
                                        <span className={`px-2 py-1 rounded text-xs font-medium ${getTierColor(item.tier)}`}>
                                            {item.tier}
                                        </span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-slate-400">{item.evidenceConfidence}/3</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                                    {item.lastAssessedAt ? new Date(item.lastAssessedAt).toLocaleDateString() : '—'}
                                </td>
                            </tr>
                        ))}
                        {agents.length === 0 && (
                            <tr>
                                <td colSpan={7} className="px-6 py-8 text-center text-slate-400">
                                    No verified agents found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </section>
    )
}
