import { useEffect, useState, FC } from 'react';
import { Loader2, Code, X } from 'lucide-react';

interface VisualWorkspaceProps {
    isGenerating: boolean;
    currentVisual: string | null;
    jsonParams: any | null;
    onClose: () => void;
}

const VisualWorkspace: FC<VisualWorkspaceProps> = ({ isGenerating, currentVisual, jsonParams, onClose }) => {
    const [showJson, setShowJson] = useState(false);
    const [progress, setProgress] = useState(0);

    // Simulate progress bar during generation
    useEffect(() => {
        if (isGenerating) {
            setProgress(0);
            const interval = setInterval(() => {
                setProgress(prev => {
                    if (prev >= 100) {
                        clearInterval(interval);
                        return 100;
                    }
                    return prev + 1; // Slow progress
                });
            }, 50); // 5 seconds total roughly
            return () => clearInterval(interval);
        } else {
            setProgress(100);
        }
    }, [isGenerating]);

    if (!isGenerating && !currentVisual) return null;

    return (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-950/90 backdrop-blur-sm p-8">
            <div className="relative w-full max-w-5xl h-[80vh] bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col">

                {/* Header */}
                <div className="h-14 border-b border-slate-700 flex items-center justify-between px-6 bg-slate-800/50">
                    <div className="flex items-center gap-3">
                        <div className={`h-2 w-2 rounded-full ${isGenerating ? 'bg-blue-400 animate-pulse' : 'bg-green-400'}`} />
                        <span className="font-mono text-sm text-slate-300">
                            {isGenerating ? 'GENERATING_VISUAL_ASSET...' : 'VISUAL_ASSET_READY'}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setShowJson(!showJson)}
                            className={`p-2 rounded hover:bg-slate-700 transition-colors ${showJson ? 'text-blue-400 bg-slate-800' : 'text-slate-400'}`}
                            title="Toggle JSON Parameters"
                        >
                            <Code className="h-4 w-4" />
                        </button>
                        <button
                            onClick={onClose}
                            className="p-2 rounded hover:bg-red-500/20 hover:text-red-400 text-slate-400 transition-colors"
                            aria-label="Close"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="flex-1 relative flex">

                    {/* Visual Canvas */}
                    <div className="flex-1 flex items-center justify-center bg-[url('/assets/grid-pattern.svg')] bg-repeat relative overflow-hidden">

                        {isGenerating ? (
                            <div className="flex flex-col items-center max-w-md text-center p-6">
                                <div className="relative mb-8">
                                    <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 animate-pulse rounded-full"></div>
                                    <Loader2 className="h-16 w-16 text-blue-400 animate-spin relative z-10" />
                                </div>
                                <h3 className="text-xl font-light text-white mb-2">Synthesizing Visual Data</h3>
                                <p className="text-slate-400 text-sm mb-6">
                                    {jsonParams?.narrative || "Processing request parameters..."}
                                </p>

                                {/* Progress Bar */}
                                <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-blue-500 transition-all duration-100 ease-linear"
                                        style={{ width: `${progress}%` }}
                                    />
                                </div>
                                <div className="mt-2 font-mono text-xs text-blue-400">{progress}%</div>
                            </div>
                        ) : (
                            <div className="relative w-full h-full p-8 flex items-center justify-center animate-in fade-in zoom-in duration-500">
                                <img
                                    src={currentVisual || ''}
                                    alt="Generated Visual"
                                    className="max-w-full max-h-full object-contain shadow-2xl rounded-lg border border-slate-700/50"
                                />
                                <div className="absolute bottom-6 right-6 flex gap-2">
                                    <button className="px-3 py-1.5 bg-slate-800/80 backdrop-blur border border-slate-600 rounded text-xs text-white hover:bg-slate-700">
                                        Download
                                    </button>
                                    <button className="px-3 py-1.5 bg-blue-600/80 backdrop-blur border border-blue-500 rounded text-xs text-white hover:bg-blue-500">
                                        Add to Report
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* JSON Overlay (if toggled) */}
                        {showJson && (
                            <div className="absolute top-4 right-4 w-80 bg-slate-950/90 backdrop-blur border border-slate-700 rounded-lg p-4 shadow-xl text-xs font-mono overflow-auto max-h-[calc(100%-2rem)] animate-in slide-in-from-right-10">
                                <div className="text-slate-500 mb-2 uppercase tracking-wider font-bold">Generation Parameters</div>
                                <pre className="text-green-400 whitespace-pre-wrap">
                                    {JSON.stringify(jsonParams, null, 2)}
                                </pre>
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );
};

export default VisualWorkspace;
