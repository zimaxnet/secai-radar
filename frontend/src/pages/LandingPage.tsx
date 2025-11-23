import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
    Shield, 
    Sparkles, 
    TrendingUp, 
    ArrowRight, 
    CheckCircle,
    Zap,
    BarChart3,
    Users
} from 'lucide-react';

export const LandingPage: React.FC = () => {
    return (
        <div className="min-h-screen bg-slate-950 text-white">
            {/* Hero Section */}
            <div className="relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20" />
                <div className="absolute top-0 left-0 w-full h-full">
                    <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 rounded-full blur-[120px]" />
                    <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/10 rounded-full blur-[120px]" />
                </div>
                
                <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center"
                    >
                        <div className="inline-block mb-4 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium">
                            AI-Powered Security Assessment Platform
                        </div>
                        <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500">
                            SecAI Radar
                        </h1>
                        <p className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto mb-8">
                            Comprehensive security assessment with specialized AI agents working in harmony to secure your cloud infrastructure.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Link
                                to="/tenant/default/dashboard"
                                className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all font-semibold text-lg shadow-lg shadow-blue-500/50"
                            >
                                Get Started
                                <ArrowRight size={20} />
                            </Link>
                            <Link
                                to="/tenant/default/agents"
                                className="inline-flex items-center gap-2 px-8 py-4 bg-slate-800 border border-slate-700 text-white rounded-xl hover:bg-slate-700 transition-all font-semibold text-lg"
                            >
                                Meet the Agents
                                <Sparkles size={20} />
                            </Link>
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Features Section */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
                    <p className="text-xl text-slate-400">Everything you need for comprehensive security assessment</p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
                    {[
                        {
                            icon: Sparkles,
                            title: '7 Specialized AI Agents',
                            description: 'A team of autonomous AI agents, each specializing in different security domains, working together seamlessly.',
                            color: 'from-purple-500 to-pink-500'
                        },
                        {
                            icon: Shield,
                            title: 'Control Management',
                            description: 'Import, track, and manage security controls across multiple frameworks (CAF, CIS, NIST).',
                            color: 'from-blue-500 to-cyan-500'
                        },
                        {
                            icon: TrendingUp,
                            title: 'Gap Analysis',
                            description: 'Identify security gaps by comparing tool capabilities against control requirements with AI-powered insights.',
                            color: 'from-green-500 to-emerald-500'
                        },
                        {
                            icon: BarChart3,
                            title: 'Real-time Dashboard',
                            description: 'Monitor your security posture with live progress tracking and comprehensive analytics.',
                            color: 'from-yellow-500 to-orange-500'
                        },
                        {
                            icon: Users,
                            title: 'Multi-Tenant Support',
                            description: 'Manage assessments for multiple tenants with complete isolation and customizable workflows.',
                            color: 'from-indigo-500 to-purple-500'
                        },
                        {
                            icon: Zap,
                            title: 'AI Recommendations',
                            description: 'Get intelligent recommendations for improving security coverage based on your current tool inventory.',
                            color: 'from-pink-500 to-rose-500'
                        }
                    ].map((feature, index) => {
                        const Icon = feature.icon;
                        return (
                            <motion.div
                                key={feature.title}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: index * 0.1 }}
                                className="bg-slate-900 rounded-xl p-6 border border-slate-800 hover:border-slate-700 transition-all"
                            >
                                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4`}>
                                    <Icon size={24} className="text-white" />
                                </div>
                                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                                <p className="text-slate-400">{feature.description}</p>
                            </motion.div>
                        );
                    })}
                </div>

                {/* CTA Section */}
                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl p-12 text-center relative overflow-hidden"
                >
                    <div className="absolute inset-0 bg-black/20" />
                    <div className="relative z-10">
                        <h2 className="text-4xl font-bold mb-4">Ready to Get Started?</h2>
                        <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
                            Join organizations using SecAI Radar to streamline their security assessment workflows.
                        </p>
                        <Link
                            to="/tenant/default/dashboard"
                            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-purple-600 rounded-xl hover:bg-blue-50 transition-all font-semibold text-lg shadow-lg"
                        >
                            Launch Dashboard
                            <ArrowRight size={20} />
                        </Link>
                    </div>
                </motion.div>
            </div>

            {/* Footer */}
            <footer className="border-t border-slate-800 py-8">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-400">
                    <p>© 2024 SecAI Radar. Built with AI for security professionals.</p>
                </div>
            </footer>
        </div>
    );
};

