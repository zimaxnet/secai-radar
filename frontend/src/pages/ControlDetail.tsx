import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { 
    Shield, 
    Upload, 
    FileText, 
    CheckCircle, 
    Clock,
    AlertTriangle,
    X,
    MessageSquare,
    Sparkles,
    Save,
    ArrowLeft
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatInterface } from '../components/ChatInterface';
import { agents } from '../data/agents';

interface Control {
    RowKey: string;
    PartitionKey: string;
    Domain: string;
    ControlTitle: string;
    ControlDescription: string;
    Question: string;
    RequiredEvidence: string;
    Status: string;
    Owner: string;
    Notes: string;
    ScoreNumeric: number;
    SourceRef: string;
}

interface Evidence {
    file_name: string;
    file_url: string;
    uploaded_at: string;
    size: number;
}

export const ControlDetail: React.FC = () => {
    const { id: tenantId, controlId } = useParams<{ id: string; controlId: string }>();
    const navigate = useNavigate();
    const [control, setControl] = useState<Control | null>(null);
    const [evidence, setEvidence] = useState<Evidence[]>([]);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);
    const [showAgentChat, setShowAgentChat] = useState(false);
    const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
    const [uploading, setUploading] = useState(false);
    const [fileInput, setFileInput] = useState<HTMLInputElement | null>(null);

    // Form state
    const [status, setStatus] = useState('');
    const [owner, setOwner] = useState('');
    const [notes, setNotes] = useState('');

    useEffect(() => {
        if (!tenantId || !controlId) return;

        const fetchControl = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/tenant/${tenantId}/control/${controlId}`);
                if (response.ok) {
                    const data = await response.json();
                    setControl(data);
                    setStatus(data.Status || 'NotStarted');
                    setOwner(data.Owner || '');
                    setNotes(data.Notes || '');
                    
                    // Fetch evidence
                    const evidenceResponse = await fetch(`http://localhost:8000/api/tenant/${tenantId}/control/${controlId}/evidence`);
                    if (evidenceResponse.ok) {
                        const evidenceData = await evidenceResponse.json();
                        setEvidence(evidenceData.items || []);
                    }
                }
            } catch (error) {
                console.error('Failed to fetch control:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchControl();
    }, [tenantId, controlId]);

    const handleUpdate = async () => {
        if (!tenantId || !controlId) return;
        
        setUpdating(true);
        try {
            const response = await fetch(`http://localhost:8000/api/tenant/${tenantId}/control/${controlId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    Status: status,
                    Owner: owner,
                    Notes: notes
                })
            });

            if (response.ok) {
                const data = await response.json();
                setControl(data.control);
                alert('Control updated successfully!');
            }
        } catch (error) {
            console.error('Failed to update control:', error);
            alert('Failed to update control');
        } finally {
            setUpdating(false);
        }
    };

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file || !tenantId || !controlId) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(
                `http://localhost:8000/api/tenant/${tenantId}/control/${controlId}/evidence`,
                {
                    method: 'POST',
                    body: formData
                }
            );

            if (response.ok) {
                const data = await response.json();
                setEvidence(prev => [...prev, data.evidence]);
                alert('Evidence uploaded successfully!');
            } else {
                alert('Failed to upload evidence');
            }
        } catch (error) {
            console.error('Failed to upload evidence:', error);
            alert('Failed to upload evidence');
        } finally {
            setUploading(false);
            if (fileInput) fileInput.value = '';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'complete': return 'bg-green-500/20 text-green-400 border-green-500/30';
            case 'inprogress': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
            default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'complete': return <CheckCircle size={18} />;
            case 'inprogress': return <Clock size={18} />;
            default: return <AlertTriangle size={18} />;
        }
    };

    if (loading) {
        return (
            <Layout tenantId={tenantId}>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div className="text-center py-12 text-slate-400">Loading control details...</div>
                </div>
            </Layout>
        );
    }

    if (!control) {
        return (
            <Layout tenantId={tenantId}>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div className="bg-slate-900 rounded-xl p-12 border border-slate-800 text-center">
                        <AlertTriangle className="mx-auto mb-4 text-red-400" size={48} />
                        <h3 className="text-xl font-bold mb-2">Control not found</h3>
                        <Link
                            to={`/tenant/${tenantId}/controls`}
                            className="text-blue-400 hover:text-blue-300"
                        >
                            Back to Controls
                        </Link>
                    </div>
                </div>
            </Layout>
        );
    }

    const selectedAgentData = selectedAgent ? agents.find(a => a.id === selectedAgent) : null;

    return (
        <Layout tenantId={tenantId}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="mb-8">
                    <Link
                        to={`/tenant/${tenantId}/controls`}
                        className="inline-flex items-center gap-2 text-slate-400 hover:text-white mb-4 transition-colors"
                    >
                        <ArrowLeft size={18} />
                        Back to Controls
                    </Link>
                    <div className="flex items-start justify-between">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <Shield className="text-blue-400" size={32} />
                                <h1 className="text-3xl font-bold">{control.ControlTitle || control.RowKey}</h1>
                                <span className={`px-3 py-1 rounded-full text-sm font-medium border flex items-center gap-2 ${getStatusColor(control.Status)}`}>
                                    {getStatusIcon(control.Status)}
                                    {control.Status || 'Not Started'}
                                </span>
                            </div>
                            <p className="text-slate-400 mb-1">Control ID: {control.RowKey}</p>
                            <p className="text-slate-400">Domain: {control.Domain}</p>
                        </div>
                        <button
                            onClick={() => setShowAgentChat(!showAgentChat)}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
                        >
                            <Sparkles size={18} />
                            {showAgentChat ? 'Hide' : 'Show'} AI Agents
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Control Information */}
                        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                            <h2 className="text-xl font-bold mb-4">Control Information</h2>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm font-medium text-slate-400 mb-1 block">Description</label>
                                    <p className="text-white">{control.ControlDescription || 'No description provided'}</p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-slate-400 mb-1 block">Question</label>
                                    <p className="text-white">{control.Question || 'No question specified'}</p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-slate-400 mb-1 block">Required Evidence</label>
                                    <p className="text-white">{control.RequiredEvidence || 'No specific evidence requirements'}</p>
                                </div>
                                {control.SourceRef && (
                                    <div>
                                        <label className="text-sm font-medium text-slate-400 mb-1 block">Source Reference</label>
                                        <p className="text-white font-mono text-sm">{control.SourceRef}</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Update Form */}
                        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                            <h2 className="text-xl font-bold mb-4">Update Control</h2>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm font-medium text-slate-400 mb-2 block">Status</label>
                                    <select
                                        value={status}
                                        onChange={(e) => setStatus(e.target.value)}
                                        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                                    >
                                        <option value="NotStarted">Not Started</option>
                                        <option value="InProgress">In Progress</option>
                                        <option value="Complete">Complete</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-slate-400 mb-2 block">Owner</label>
                                    <input
                                        type="text"
                                        value={owner}
                                        onChange={(e) => setOwner(e.target.value)}
                                        placeholder="Enter owner name or email"
                                        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-slate-400 mb-2 block">Notes</label>
                                    <textarea
                                        value={notes}
                                        onChange={(e) => setNotes(e.target.value)}
                                        placeholder="Add notes about this control..."
                                        rows={4}
                                        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                                    />
                                </div>
                                <button
                                    onClick={handleUpdate}
                                    disabled={updating}
                                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                                >
                                    <Save size={18} />
                                    {updating ? 'Updating...' : 'Save Changes'}
                                </button>
                            </div>
                        </div>

                        {/* Evidence Collection */}
                        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-bold">Evidence</h2>
                                <label className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors cursor-pointer flex items-center gap-2">
                                    <Upload size={18} />
                                    Upload Evidence
                                    <input
                                        ref={(el) => setFileInput(el)}
                                        type="file"
                                        onChange={handleFileUpload}
                                        className="hidden"
                                        disabled={uploading}
                                    />
                                </label>
                            </div>
                            
                            {uploading && (
                                <div className="mb-4 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg text-blue-400 text-sm">
                                    Uploading evidence...
                                </div>
                            )}

                            {evidence.length === 0 ? (
                                <div className="text-center py-8 text-slate-400">
                                    <FileText className="mx-auto mb-2 text-slate-600" size={32} />
                                    <p>No evidence uploaded yet</p>
                                </div>
                            ) : (
                                <div className="space-y-2">
                                    {evidence.map((item, index) => (
                                        <div
                                            key={index}
                                            className="flex items-center justify-between p-4 bg-slate-800 rounded-lg border border-slate-700"
                                        >
                                            <div className="flex items-center gap-3">
                                                <FileText className="text-blue-400" size={20} />
                                                <div>
                                                    <p className="text-white font-medium">{item.file_name}</p>
                                                    <p className="text-xs text-slate-400">
                                                        {(item.size / 1024).toFixed(2)} KB
                                                        {item.uploaded_at && ` • ${new Date(item.uploaded_at).toLocaleDateString()}`}
                                                    </p>
                                                </div>
                                            </div>
                                            <a
                                                href={item.file_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="px-3 py-1 bg-blue-600/20 border border-blue-600/30 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors text-sm"
                                            >
                                                View
                                            </a>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Agent Chat Sidebar */}
                    {showAgentChat && (
                        <div className="space-y-4">
                            <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                    <Sparkles className="text-purple-400" size={24} />
                                    AI Agent Help
                                </h2>
                                <p className="text-slate-400 text-sm mb-4">
                                    Get assistance from specialized AI agents for this control
                                </p>
                                
                                <div className="space-y-2 mb-4">
                                    {agents.filter(a => ['aris', 'elena', 'leo'].includes(a.id)).map((agent) => (
                                        <button
                                            key={agent.id}
                                            onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                                            className={`w-full p-3 rounded-lg border transition-all text-left ${
                                                selectedAgent === agent.id
                                                    ? 'bg-purple-600/20 border-purple-500/50'
                                                    : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                                            }`}
                                        >
                                            <div className="flex items-center gap-2">
                                                <div className={`w-2 h-2 rounded-full ${
                                                    selectedAgent === agent.id ? 'bg-purple-400' : 'bg-slate-500'
                                                }`} />
                                                <span className="font-medium text-white">{agent.name}</span>
                                            </div>
                                            <p className="text-xs text-slate-400 mt-1">{agent.role}</p>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {selectedAgent && selectedAgentData && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden"
                                >
                                    <div className={`h-2 bg-gradient-to-r ${selectedAgentData.color}`} />
                                    <div className="p-4">
                                        <div className="flex items-center justify-between mb-4">
                                            <h3 className="font-bold text-white">{selectedAgentData.name}</h3>
                                            <button
                                                onClick={() => setSelectedAgent(null)}
                                                className="p-1 rounded-lg hover:bg-slate-800 transition-colors"
                                            >
                                                <X size={18} className="text-slate-400" />
                                            </button>
                                        </div>
                                        <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                                            <ChatInterface 
                                                agent={selectedAgentData}
                                                contextControl={control}
                                            />
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </Layout>
    );
};

