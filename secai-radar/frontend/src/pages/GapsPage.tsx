import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { TrendingDown, AlertTriangle, CheckCircle, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

interface GapResult {
    ControlID: string;
    Coverage: number;
    HardGaps: Array<{ capabilityId: string }>;
    SoftGaps: Array<{ capabilityId: string; best: number; min: number }>;
    AIRecommendation?: string;
}

export const GapsPage: React.FC = () => {
    const { id: tenantId } = useParams<{ id: string }>();
    const [gaps, setGaps] = useState<GapResult[]>([]);
    const [loading, setLoading] = useState(true);
    const [includeAI, setIncludeAI] = useState(false);

    useEffect(() => {
        const fetchGaps = async () => {
            if (!tenantId) return;
            
            try {
                const url = `http://localhost:8000/api/tenant/${tenantId}/gaps?ai=${includeAI}`;
                const response = await fetch(url);
                if (response.ok) {
                    const data = await response.json();
                    setGaps(data.items || []);
                }
            } catch (error) {
                console.error('Failed to fetch gaps:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchGaps();
    }, [tenantId, includeAI]);

    const controlsWithGaps = gaps.filter(g => g.HardGaps.length > 0 || g.SoftGaps.length > 0).length;
    const totalHardGaps = gaps.reduce((sum, g) => sum + g.HardGaps.length, 0);
    const totalSoftGaps = gaps.reduce((sum, g) => sum + g.SoftGaps.length, 0);
    const avgCoverage = gaps.length > 0
        ? gaps.reduce((sum, g) => sum + g.Coverage, 0) / gaps.length
        : 0;

    return (
        <Layout tenantId={tenantId}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                            <TrendingDown className="text-blue-400" size={32} />
                            Gap Analysis
                        </h1>
                        <p className="text-slate-400">
                            Identify security coverage gaps based on tool capabilities
                        </p>
                    </div>
                    <label className="flex items-center gap-3 px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg cursor-pointer hover:bg-slate-800 transition-colors">
                        <input
                            type="checkbox"
                            checked={includeAI}
                            onChange={(e) => setIncludeAI(e.target.checked)}
                            className="rounded"
                        />
                        <Sparkles size={18} className="text-purple-400" />
                        <span className="text-sm font-medium">AI Recommendations</span>
                    </label>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                        <div className="text-3xl font-bold text-white mb-2">{gaps.length}</div>
                        <div className="text-slate-400 text-sm">Controls Analyzed</div>
                    </div>
                    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                        <div className="text-3xl font-bold text-blue-400 mb-2">{(avgCoverage * 100).toFixed(1)}%</div>
                        <div className="text-slate-400 text-sm">Avg Coverage</div>
                    </div>
                    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                        <div className="text-3xl font-bold text-red-400 mb-2">{totalHardGaps}</div>
                        <div className="text-slate-400 text-sm">Hard Gaps</div>
                    </div>
                    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                        <div className="text-3xl font-bold text-yellow-400 mb-2">{totalSoftGaps}</div>
                        <div className="text-slate-400 text-sm">Soft Gaps</div>
                    </div>
                </div>

                {/* Gaps List */}
                {loading ? (
                    <div className="text-center py-12 text-slate-400">Analyzing gaps...</div>
                ) : gaps.length === 0 ? (
                    <div className="bg-slate-900 rounded-xl p-12 border border-slate-800 text-center">
                        <AlertTriangle className="mx-auto mb-4 text-slate-600" size={48} />
                        <h3 className="text-xl font-bold mb-2">No gaps data available</h3>
                        <p className="text-slate-400">Import controls and configure tools to analyze gaps</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {gaps
                            .filter(g => g.HardGaps.length > 0 || g.SoftGaps.length > 0)
                            .sort((a, b) => a.Coverage - b.Coverage)
                            .map((gap, index) => (
                                <motion.div
                                    key={gap.ControlID}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                    className="bg-slate-900 rounded-xl p-6 border border-slate-800"
                                >
                                    <div className="flex items-start justify-between mb-4">
                                        <div>
                                            <h3 className="text-lg font-semibold text-white mb-1">
                                                {gap.ControlID}
                                            </h3>
                                            <div className="flex items-center gap-4 text-sm">
                                                <span className="text-slate-400">
                                                    Coverage: <span className="text-white font-medium">{(gap.Coverage * 100).toFixed(1)}%</span>
                                                </span>
                                                <div className="w-32 bg-slate-700 rounded-full h-2 overflow-hidden">
                                                    <div
                                                        className={`h-full transition-all ${
                                                            gap.Coverage >= 0.8 
                                                                ? 'bg-green-500' 
                                                                : gap.Coverage >= 0.5 
                                                                ? 'bg-yellow-500' 
                                                                : 'bg-red-500'
                                                        }`}
                                                        style={{ width: `${gap.Coverage * 100}%` }}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                        {gap.HardGaps.length > 0 && (
                                            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <AlertTriangle className="text-red-400" size={18} />
                                                    <span className="font-semibold text-red-400">Hard Gaps</span>
                                                    <span className="text-xs text-slate-400">({gap.HardGaps.length})</span>
                                                </div>
                                                <div className="space-y-1">
                                                    {gap.HardGaps.slice(0, 3).map((g, i) => (
                                                        <div key={i} className="text-sm text-slate-300">
                                                            • {g.capabilityId}
                                                        </div>
                                                    ))}
                                                    {gap.HardGaps.length > 3 && (
                                                        <div className="text-xs text-slate-400">
                                                            +{gap.HardGaps.length - 3} more
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                        
                                        {gap.SoftGaps.length > 0 && (
                                            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <TrendingDown className="text-yellow-400" size={18} />
                                                    <span className="font-semibold text-yellow-400">Soft Gaps</span>
                                                    <span className="text-xs text-slate-400">({gap.SoftGaps.length})</span>
                                                </div>
                                                <div className="space-y-1">
                                                    {gap.SoftGaps.slice(0, 3).map((g, i) => (
                                                        <div key={i} className="text-sm text-slate-300">
                                                            • {g.capabilityId} (current: {(g.best * 100).toFixed(0)}%, needed: {(g.min * 100).toFixed(0)}%)
                                                        </div>
                                                    ))}
                                                    {gap.SoftGaps.length > 3 && (
                                                        <div className="text-xs text-slate-400">
                                                            +{gap.SoftGaps.length - 3} more
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                    
                                    {gap.AIRecommendation && (
                                        <div className="mt-4 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                                            <div className="flex items-center gap-2 mb-2">
                                                <Sparkles className="text-purple-400" size={18} />
                                                <span className="font-semibold text-purple-400">AI Recommendation</span>
                                            </div>
                                            <p className="text-sm text-slate-300">{gap.AIRecommendation}</p>
                                        </div>
                                    )}
                                </motion.div>
                            ))}
                    </div>
                )}
            </div>
        </Layout>
    );
};

