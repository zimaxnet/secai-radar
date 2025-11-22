import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Wrench, Plus, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface Tool {
    RowKey: string;
    Enabled: boolean;
    ConfigScore: number;
    Owner: string;
    Notes: string;
}

export const ToolsPage: React.FC = () => {
    const { id: tenantId } = useParams<{ id: string }>();
    const [tools, setTools] = useState<Tool[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTools = async () => {
            if (!tenantId) return;
            
            try {
                const response = await fetch(`http://localhost:8000/api/tenant/${tenantId}/tools`);
                if (response.ok) {
                    const data = await response.json();
                    setTools(data.items || []);
                }
            } catch (error) {
                console.error('Failed to fetch tools:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchTools();
    }, [tenantId]);

    const enabledCount = tools.filter(t => t.Enabled).length;
    const avgConfigScore = tools.length > 0
        ? tools.reduce((sum, t) => sum + (t.ConfigScore || 0), 0) / tools.length
        : 0;

    return (
        <Layout tenantId={tenantId}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                            <Wrench className="text-blue-400" size={32} />
                            Security Tools Inventory
                        </h1>
                        <p className="text-slate-400">
                            Manage your security tools and their configuration scores
                        </p>
                    </div>
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
                        <Plus size={20} />
                        Add Tool
                    </button>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                        <div className="text-3xl font-bold text-white mb-2">{tools.length}</div>
                        <div className="text-slate-400 text-sm">Total Tools</div>
                    </div>
                    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                        <div className="text-3xl font-bold text-green-400 mb-2">{enabledCount}</div>
                        <div className="text-slate-400 text-sm">Enabled</div>
                    </div>
                    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                        <div className="text-3xl font-bold text-blue-400 mb-2">{avgConfigScore.toFixed(1)}</div>
                        <div className="text-slate-400 text-sm">Avg Config Score</div>
                    </div>
                </div>

                {/* Tools List */}
                {loading ? (
                    <div className="text-center py-12 text-slate-400">Loading tools...</div>
                ) : tools.length === 0 ? (
                    <div className="bg-slate-900 rounded-xl p-12 border border-slate-800 text-center">
                        <Wrench className="mx-auto mb-4 text-slate-600" size={48} />
                        <h3 className="text-xl font-bold mb-2">No tools configured</h3>
                        <p className="text-slate-400 mb-6">Add your security tools to start gap analysis</p>
                        <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                            Add First Tool
                        </button>
                    </div>
                ) : (
                    <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                        <div className="divide-y divide-slate-800">
                            {tools.map((tool, index) => (
                                <motion.div
                                    key={tool.RowKey}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                    className="p-6 hover:bg-slate-800/50 transition-colors"
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-4 flex-1">
                                            <div className={`p-3 rounded-lg ${
                                                tool.Enabled 
                                                    ? 'bg-green-500/20' 
                                                    : 'bg-slate-700'
                                            }`}>
                                                {tool.Enabled ? (
                                                    <CheckCircle className="text-green-400" size={24} />
                                                ) : (
                                                    <XCircle className="text-slate-400" size={24} />
                                                )}
                                            </div>
                                            <div className="flex-1">
                                                <h3 className="text-lg font-semibold text-white mb-1">
                                                    {tool.RowKey}
                                                </h3>
                                                <div className="flex items-center gap-4 text-sm text-slate-400">
                                                    <span>Config Score: {(tool.ConfigScore || 0).toFixed(2)}</span>
                                                    {tool.Owner && <span>Owner: {tool.Owner}</span>}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <div className="w-32 bg-slate-700 rounded-full h-2 overflow-hidden">
                                                <div
                                                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all"
                                                    style={{ width: `${(tool.ConfigScore || 0) * 100}%` }}
                                                />
                                            </div>
                                            <button className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 transition-colors text-sm">
                                                Edit
                                            </button>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </Layout>
    );
};

