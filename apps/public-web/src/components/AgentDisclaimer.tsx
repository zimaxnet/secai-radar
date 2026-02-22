import { AlertTriangle } from 'lucide-react';

export function AgentDisclaimer() {
    return (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 mb-6">
            <div className="flex gap-3">
                <AlertTriangle className="h-5 w-5 text-yellow-500 shrink-0 mt-0.5" />
                <div className="text-sm text-yellow-200">
                    <p className="font-medium text-yellow-400 mb-1">Disclaimer</p>
                    <p>
                        The customizations in this repository are sourced from and created by third-party developers.
                        GitHub does not verify, endorse, or guarantee the functionality or security of these agents.
                        Please carefully inspect any agent and its documentation before installing to understand permissions
                        it may require and actions it may perform.
                    </p>
                </div>
            </div>
        </div>
    );
}
