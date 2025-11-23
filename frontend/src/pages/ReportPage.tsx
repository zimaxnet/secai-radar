import React from 'react';
import { useParams } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { FileText, Download, Printer } from 'lucide-react';

export const ReportPage: React.FC = () => {
    const { id: tenantId } = useParams<{ id: string }>();

    return (
        <Layout tenantId={tenantId}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                            <FileText className="text-blue-400" size={32} />
                            Assessment Report
                        </h1>
                        <p className="text-slate-400">
                            Generate comprehensive security assessment reports
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <button className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 transition-colors flex items-center gap-2">
                            <Printer size={20} />
                            Print
                        </button>
                        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
                            <Download size={20} />
                            Download PDF
                        </button>
                    </div>
                </div>

                <div className="bg-slate-900 rounded-xl p-12 border border-slate-800 text-center">
                    <FileText className="mx-auto mb-4 text-slate-600" size={48} />
                    <h3 className="text-xl font-bold mb-2">Report Generation Coming Soon</h3>
                    <p className="text-slate-400">
                        AI-powered report generation with executive summaries and detailed findings
                    </p>
                </div>
            </div>
        </Layout>
    );
};

