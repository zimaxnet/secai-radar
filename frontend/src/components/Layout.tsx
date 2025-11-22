import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
    LayoutDashboard, 
    Users, 
    Shield, 
    Wrench, 
    TrendingDown, 
    FileText,
    Sparkles,
    Menu,
    X
} from 'lucide-react';
import { useState } from 'react';

interface LayoutProps {
    children: React.ReactNode;
    tenantId?: string;
}

export const Layout: React.FC<LayoutProps> = ({ children, tenantId = 'default' }) => {
    const location = useLocation();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const navItems = [
        { path: `/tenant/${tenantId}/dashboard`, label: 'Dashboard', icon: LayoutDashboard },
        { path: `/tenant/${tenantId}/agents`, label: 'AI Agents', icon: Sparkles },
        { path: `/tenant/${tenantId}/controls`, label: 'Controls', icon: Shield },
        { path: `/tenant/${tenantId}/tools`, label: 'Tools', icon: Wrench },
        { path: `/tenant/${tenantId}/gaps`, label: 'Gap Analysis', icon: TrendingDown },
        { path: `/tenant/${tenantId}/report`, label: 'Report', icon: FileText },
    ];

    const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + '/');

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            {/* Top Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-lg border-b border-slate-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => setSidebarOpen(!sidebarOpen)}
                                className="lg:hidden p-2 rounded-lg hover:bg-slate-800 transition-colors"
                            >
                                {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
                            </button>
                            <Link to={`/tenant/${tenantId}/dashboard`} className="flex items-center gap-2">
                                <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                                    <Shield size={20} />
                                </div>
                                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                                    SecAI Radar
                                </span>
                            </Link>
                        </div>
                        <div className="hidden lg:flex items-center gap-1">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 ${
                                            isActive(item.path)
                                                ? 'bg-blue-600 text-white'
                                                : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                        }`}
                                    >
                                        <Icon size={18} />
                                        <span className="font-medium">{item.label}</span>
                                    </Link>
                                );
                            })}
                        </div>
                        <div className="text-sm text-slate-400 hidden md:block">
                            Tenant: <span className="text-blue-400 font-mono">{tenantId}</span>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Mobile Sidebar */}
            {sidebarOpen && (
                <div 
                    className="lg:hidden fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
                    onClick={() => setSidebarOpen(false)}
                >
                    <div 
                        className="fixed left-0 top-16 bottom-0 w-64 bg-slate-900 border-r border-slate-800 overflow-y-auto"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="p-4 space-y-2">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        onClick={() => setSidebarOpen(false)}
                                        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                                            isActive(item.path)
                                                ? 'bg-blue-600 text-white'
                                                : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                        }`}
                                    >
                                        <Icon size={20} />
                                        <span className="font-medium">{item.label}</span>
                                    </Link>
                                );
                            })}
                        </div>
                    </div>
                </div>
            )}

            {/* Main Content */}
            <div className="pt-16">
                {children}
            </div>
        </div>
    );
};

