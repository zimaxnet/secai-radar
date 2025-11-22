import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { 
    Shield, 
    TrendingUp, 
    AlertTriangle, 
    CheckCircle, 
    Clock,
    Sparkles,
    ArrowRight,
    Activity
} from 'lucide-react';
import { motion } from 'framer-motion';
import { apiClient } from '../services/api';

interface DomainSummary {
    domain: string;
    total: number;
    complete: number;
    inProgress: number;
    notStarted: number;
}

interface AgentSummary {
    id: string;
    name: string;
    status: 'available' | 'busy';
    lastActivity: string;
}

export const Dashboard: React.FC = () => {
    const { id: tenantId } = useParams<{ id: string }>();
    const [domains, setDomains] = useState<DomainSummary[]>([]);
    const [loading, setLoading] = useState(true);
    const [agents] = useState<AgentSummary[]>([
        { id: 'aris', name: 'Aris', status: 'available', lastActivity: '2m ago' },
        { id: 'leo', name: 'Leo', status: 'available', lastActivity: '5m ago' },
        { id: 'ravi', name: 'Ravi', status: 'busy', lastActivity: 'Active now' },
        { id: 'kenji', name: 'Kenji', status: 'available', lastActivity: '10m ago' },
    ]);

    useEffect(() => {
        const fetchSummary = async () => {
            if (!tenantId) return;
            
            try {
                const response = await fetch(`http://localhost:8000/api/tenant/${tenantId}/summary`);
                if (response.ok) {
                    const data = await response.json();
                    setDomains(data.byDomain || []);
                }
            } catch (error) {
                console.error('Failed to fetch summary:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, [tenantId]);

    const totalControls = domains.reduce((sum, d) => sum + d.total, 0);
    const completeControls = domains.reduce((sum, d) => sum + d.complete, 0);
    const inProgressControls = domains.reduce((sum, d) => sum + d.inProgress, 0);
    const overallProgress = totalControls > 0 ? (completeControls / totalControls) * 100 : 0;

    return (
        <Layout tenantId={tenantId}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Hero Section */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white relative overflow-hidden">
                        <div className="absolute inset-0 bg-black/20" />
                        <div className="relative z-10">
                            <h1 className="text-4xl md:text-5xl font-bold mb-2">Security Assessment Dashboard</h1>
                            <p className="text-blue-100 text-lg">
                                Monitor your security posture across all domains with AI-powered insights
                            </p>
                        </div>
                        <div className="absolute -right-20 -top-20 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
                    </div>
                </motion.div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="bg-slate-900 rounded-xl p-6 border border-slate-800"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <Shield className="text-blue-400" size={24} />
                            <span className="text-2xl font-bold text-white">{totalControls}</span>
                        </div>
                        <p className="text-slate-400 text-sm">Total Controls</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="bg-slate-900 rounded-xl p-6 border border-slate-800"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <CheckCircle className="text-green-400" size={24} />
                            <span className="text-2xl font-bold text-white">{completeControls}</span>
                        </div>
                        <p className="text-slate-400 text-sm">Completed</p>
                        <div className="mt-2 h-2 bg-slate-800 rounded-full overflow-hidden">
                            <div 
                                className="h-full bg-green-500 transition-all"
                                style={{ width: `${overallProgress}%` }}
                            />
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="bg-slate-900 rounded-xl p-6 border border-slate-800"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <Clock className="text-yellow-400" size={24} />
                            <span className="text-2xl font-bold text-white">{inProgressControls}</span>
                        </div>
                        <p className="text-slate-400 text-sm">In Progress</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="bg-slate-900 rounded-xl p-6 border border-slate-800"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <TrendingUp className="text-purple-400" size={24} />
                            <span className="text-2xl font-bold text-white">{Math.round(overallProgress)}%</span>
                        </div>
                        <p className="text-slate-400 text-sm">Overall Progress</p>
                    </motion.div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Domain Progress */}
                    <div className="lg:col-span-2 bg-slate-900 rounded-xl p-6 border border-slate-800">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold">Security Domains</h2>
                            <Link
                                to={`/tenant/${tenantId}/controls`}
                                className="text-blue-400 hover:text-blue-300 text-sm font-medium flex items-center gap-1"
                            >
                                View All <ArrowRight size={16} />
                            </Link>
                        </div>

                        {loading ? (
                            <div className="text-slate-400 text-center py-8">Loading domains...</div>
                        ) : domains.length === 0 ? (
                            <div className="text-center py-8">
                                <p className="text-slate-400 mb-4">No controls imported yet</p>
                                <Link
                                    to={`/tenant/${tenantId}/controls`}
                                    className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Import Controls
                                </Link>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {domains.map((domain, index) => {
                                    const progress = domain.total > 0 ? (domain.complete / domain.total) * 100 : 0;
                                    return (
                                        <motion.div
                                            key={domain.domain}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.5 + index * 0.1 }}
                                        >
                                            <Link
                                                to={`/tenant/${tenantId}/domain/${domain.domain}`}
                                                className="block p-4 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors border border-slate-700"
                                            >
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="font-semibold text-white">{domain.domain}</span>
                                                    <span className="text-sm text-slate-400">
                                                        {domain.complete}/{domain.total}
                                                    </span>
                                                </div>
                                                <div className="h-2 bg-slate-700 rounded-full overflow-hidden mb-2">
                                                    <div
                                                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all"
                                                        style={{ width: `${progress}%` }}
                                                    />
                                                </div>
                                                <div className="flex items-center gap-4 text-xs text-slate-400">
                                                    <span className="flex items-center gap-1">
                                                        <CheckCircle size={14} className="text-green-400" />
                                                        {domain.complete}
                                                    </span>
                                                    <span className="flex items-center gap-1">
                                                        <Clock size={14} className="text-yellow-400" />
                                                        {domain.inProgress}
                                                    </span>
                                                    <span className="flex items-center gap-1">
                                                        <AlertTriangle size={14} className="text-red-400" />
                                                        {domain.notStarted}
                                                    </span>
                                                </div>
                                            </Link>
                                        </motion.div>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* AI Agents Status */}
                    <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold flex items-center gap-2">
                                <Sparkles className="text-purple-400" size={24} />
                                AI Agents
                            </h2>
                            <Link
                                to={`/tenant/${tenantId}/agents`}
                                className="text-blue-400 hover:text-blue-300 text-sm font-medium"
                            >
                                View All
                            </Link>
                        </div>
                        <div className="space-y-3">
                            {agents.map((agent, index) => (
                                <motion.div
                                    key={agent.id}
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: 0.6 + index * 0.1 }}
                                    className="flex items-center justify-between p-3 bg-slate-800 rounded-lg border border-slate-700"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-lg ${
                                            agent.status === 'available' 
                                                ? 'bg-green-500/20' 
                                                : 'bg-yellow-500/20'
                                        }`}>
                                            <Activity 
                                                size={16} 
                                                className={agent.status === 'available' ? 'text-green-400' : 'text-yellow-400'} 
                                            />
                                        </div>
                                        <div>
                                            <p className="font-medium text-white">{agent.name}</p>
                                            <p className="text-xs text-slate-400">{agent.lastActivity}</p>
                                        </div>
                                    </div>
                                    <span className={`text-xs px-2 py-1 rounded-full ${
                                        agent.status === 'available'
                                            ? 'bg-green-500/20 text-green-400'
                                            : 'bg-yellow-500/20 text-yellow-400'
                                    }`}>
                                        {agent.status}
                                    </span>
                                </motion.div>
                            ))}
                        </div>
                        <Link
                            to={`/tenant/${tenantId}/agents`}
                            className="mt-4 block w-full text-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-medium"
                        >
                            Chat with Agents
                        </Link>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

