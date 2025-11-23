import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Shield, Plus, Search, Filter, Download, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

interface Control {
    RowKey: string;
    PartitionKey: string;
    Domain: string;
    ControlTitle: string;
    Status: string;
    Owner: string;
}

export const ControlsPage: React.FC = () => {
    const { id: tenantId, domain } = useParams<{ id: string; domain?: string }>();
    const [controls, setControls] = useState<Control[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        const fetchControls = async () => {
            if (!tenantId) return;
            
            try {
                const url = `http://localhost:8000/api/tenant/${tenantId}/controls${domain ? `?domain=${domain}` : ''}`;
                const response = await fetch(url);
                if (response.ok) {
                    const data = await response.json();
                    setControls(data.items || []);
                }
            } catch (error) {
                console.error('Failed to fetch controls:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchControls();
    }, [tenantId, domain]);

    const getStatusColor = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'complete': return 'bg-green-500/20 text-green-400 border-green-500/30';
            case 'inprogress': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
            default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
        }
    };

    const filteredControls = controls.filter(control =>
        searchQuery === '' ||
        control.ControlTitle?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        control.RowKey?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <Layout tenantId={tenantId}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                            <Shield className="text-blue-400" size={32} />
                            Security Controls
                        </h1>
                        <p className="text-slate-400">
                            {domain ? `Domain: ${domain}` : 'All domains'} • {controls.length} controls
                        </p>
                    </div>
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
                        <Plus size={20} />
                        Import Controls
                    </button>
                </div>

                {/* Search and Filters */}
                <div className="bg-slate-900 rounded-xl p-4 mb-6 border border-slate-800 flex items-center gap-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
                        <input
                            type="text"
                            placeholder="Search controls..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                        />
                    </div>
                    <button className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 transition-colors flex items-center gap-2">
                        <Filter size={20} />
                        Filter
                    </button>
                    <button className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 transition-colors flex items-center gap-2">
                        <Download size={20} />
                        Export
                    </button>
                </div>

                {/* Controls List */}
                {loading ? (
                    <div className="text-center py-12 text-slate-400">Loading controls...</div>
                ) : filteredControls.length === 0 ? (
                    <div className="bg-slate-900 rounded-xl p-12 border border-slate-800 text-center">
                        <Shield className="mx-auto mb-4 text-slate-600" size={48} />
                        <h3 className="text-xl font-bold mb-2">No controls found</h3>
                        <p className="text-slate-400 mb-6">
                            {searchQuery ? 'Try adjusting your search query' : 'Get started by importing your first set of controls'}
                        </p>
                        <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                            Import Controls
                        </button>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {filteredControls.map((control, index) => (
                            <motion.div
                                key={control.RowKey}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.05 }}
                                className="bg-slate-900 rounded-xl p-6 border border-slate-800 hover:border-slate-700 transition-all"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <h3 className="text-lg font-semibold text-white">{control.ControlTitle || control.RowKey}</h3>
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(control.Status)}`}>
                                                {control.Status || 'Not Started'}
                                            </span>
                                        </div>
                                        <p className="text-sm text-slate-400 mb-2">Control ID: {control.RowKey}</p>
                                        {control.Owner && (
                                            <p className="text-sm text-slate-500">Owner: {control.Owner}</p>
                                        )}
                                    </div>
                                    <Link
                                        to={`/tenant/${tenantId}/control/${control.RowKey}`}
                                        className="px-4 py-2 bg-blue-600/20 border border-blue-600/30 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors text-sm font-medium flex items-center gap-1"
                                    >
                                        View Details
                                        <ArrowRight size={14} />
                                    </Link>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </div>
        </Layout>
    );
};

