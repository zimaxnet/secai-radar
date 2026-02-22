import { AlertTriangle } from 'lucide-react';

export function AgentDisclaimer() {
    return (
        <div className="pt-6 mt-8 border-t border-slate-800/50">
            <div className="flex gap-2 items-start text-slate-500 text-xs text-left max-w-4xl mx-auto">
                <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                <p>
                    <span className="font-semibold text-slate-400">Disclaimer:</span> The customizations and agents linked in this directory are sourced from open registries and community submissions. GitHub does not verify, endorse, or guarantee the functionality or security of these agents. Ensure you independently inspect any agent, reviewing its requested permissions and potential side effects, before installation.
                </p>
            </div>
        </div>
    );
}
