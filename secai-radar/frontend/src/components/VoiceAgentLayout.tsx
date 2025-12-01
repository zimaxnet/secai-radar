import React, { useState, useEffect, useRef } from 'react';
import { Mic, Activity, Shield, Server, Users, BarChart, Brain, MessageSquare } from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  role: string;
  color: string;
  icon: React.ElementType;
  description: string;
  expertise: string[];
}

const SecAIRadarLayout: React.FC = () => {
  const [activeAgent, setActiveAgent] = useState('Supervisor');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState<string>('');
  const [conversation, setConversation] = useState<Array<{ agent: string; message: string; timestamp: Date }>>([]);
  const audioWaveformRef = useRef<HTMLDivElement>(null);

  const agents: Agent[] = [
    { 
      id: 'Thorne', 
      name: 'Dr. Aris Thorne', 
      role: 'Security Architect', 
      color: 'border-yellow-500 bg-yellow-500/10',
      icon: Shield,
      description: 'Framework authority and security architecture expert',
      expertise: ['CAF', 'CIS', 'NIST', 'Security Architecture']
    },
    { 
      id: 'Vance', 
      name: 'Leo Vance', 
      role: 'IAM Analyst', 
      color: 'border-cyan-500 bg-cyan-500/10',
      icon: Users,
      description: 'Identity and access management specialist',
      expertise: ['IAM', 'RBAC', 'Conditional Access', 'Privilege Management']
    },
    { 
      id: 'Patel', 
      name: 'Ravi Patel', 
      role: 'Infra Architect', 
      color: 'border-orange-500 bg-orange-500/10',
      icon: Server,
      description: 'Cloud infrastructure and topology expert',
      expertise: ['Infrastructure', 'CAF Landing Zones', 'Topology', 'Scanning']
    },
    { 
      id: 'Sato', 
      name: 'Kenji Sato', 
      role: 'Findings Analyst', 
      color: 'border-indigo-500 bg-indigo-500/10',
      icon: BarChart,
      description: 'Data correlation and pattern detection specialist',
      expertise: ['Data Analysis', 'Pattern Detection', 'Evidence Analysis', 'Correlation']
    },
    { 
      id: 'Bridges', 
      name: 'Elena Bridges', 
      role: 'Business Strategist', 
      color: 'border-purple-500 bg-purple-500/10',
      icon: MessageSquare,
      description: 'Business impact and executive communication expert',
      expertise: ['Risk Quantification', 'Executive Reporting', 'ROI Analysis', 'Governance']
    },
    { 
      id: 'Sterling', 
      name: 'Marcus Sterling', 
      role: 'Governance', 
      color: 'border-slate-300 bg-slate-300/10',
      icon: Shield,
      description: 'Conflict resolution and governance specialist',
      expertise: ['Conflict Resolution', 'Trade-off Analysis', 'Stakeholder Alignment', 'Governance']
    },
    { 
      id: 'Supervisor', 
      name: 'System Orchestrator', 
      role: 'Orchestrator', 
      color: 'border-green-500 bg-green-500/10',
      icon: Activity,
      description: 'Workflow management and quality assurance',
      expertise: ['Workflow Orchestration', 'Quality Gates', 'Audit Trails', 'Synthesis']
    },
  ];

  const activeAgentData = agents.find(a => a.id === activeAgent);

  // Simulate voice waveform animation
  useEffect(() => {
    if (isListening || isSpeaking) {
      const interval = setInterval(() => {
        if (audioWaveformRef.current) {
          const waveform = audioWaveformRef.current;
          const bars = waveform.querySelectorAll('.wave-bar');
          bars.forEach((bar: Element) => {
            const height = Math.random() * 60 + 20;
            (bar as HTMLElement).style.height = `${height}%`;
          });
        }
      }, 150);
      return () => clearInterval(interval);
    }
  }, [isListening, isSpeaking]);

  // Simulate agent response
  const handleVoiceInput = () => {
    setIsListening(true);
    
    // Simulate listening duration
    setTimeout(() => {
      setIsListening(false);
      setIsSpeaking(true);
      
      // Simulate agent response
      const sampleResponses: Record<string, string> = {
        Thorne: "Based on the CIS benchmarks and NIST framework, we need to enforce MFA on root accounts and implement Zero Trust architecture.",
        Vance: "I've analyzed your IAM configuration. You need to review your conditional access policies and ensure proper separation of duties.",
        Patel: "The infrastructure scan shows several security gaps. Let me map the topology and identify critical paths that need immediate attention.",
        Sato: "I've correlated findings from multiple sources. There are three high-priority patterns that require immediate investigation.",
        Bridges: "From a business perspective, these security gaps pose significant risk exposure. The estimated impact on compliance could be substantial.",
        Sterling: "We need to balance these security requirements with business constraints. Let me help resolve the trade-offs.",
        Supervisor: "I've orchestrated the assessment workflow. All quality gates are passed, and the audit trail is complete."
      };

      const response = sampleResponses[activeAgent] || "I understand your question. Let me provide guidance on that.";
      
      setConversation(prev => [
        ...prev,
        { agent: activeAgent, message: response, timestamp: new Date() }
      ]);

      // Simulate speaking duration
      setTimeout(() => {
        setIsSpeaking(false);
      }, 3000);
    }, 2000);
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">
      
      {/* LEFT: Main Workflow / Assessment Area (65%) */}
      <main className="flex-1 flex flex-col border-r border-slate-700">
        <header className="h-16 border-b border-slate-700 flex items-center px-6 bg-slate-800/50">
          <Shield className="text-blue-400 mr-3" />
          <h1 className="text-xl font-semibold tracking-wide">
            SecAI RADAR 
            <span className="text-xs bg-blue-600 px-2 py-0.5 rounded ml-2">ASSESSMENT MODE</span>
          </h1>
        </header>
        
        {/* Dynamic Content View */}
        <div className="flex-1 p-8 overflow-y-auto relative">
          <div className="bg-slate-800/40 rounded-xl border border-slate-700 p-8 h-full shadow-inner">
            <h2 className="text-2xl mb-4 font-light">
              Current Focus: <span className="text-blue-400">Azure Identity Migration</span>
            </h2>
            <p className="text-slate-400 mb-6">
              {activeAgentData?.name} is {isSpeaking ? 'speaking...' : isListening ? 'listening...' : 'ready to assist'}
            </p>
            
            {/* Placeholder for Diagrams/Data */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="h-40 bg-slate-700/50 rounded animate-pulse"></div>
              <div className="h-40 bg-slate-700/50 rounded animate-pulse"></div>
              <div className="h-40 bg-slate-700/50 rounded animate-pulse col-span-2"></div>
            </div>

            {/* Conversation History */}
            {conversation.length > 0 && (
              <div className="mt-6 space-y-3">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Recent Conversation</h3>
                {conversation.slice(-3).map((msg, idx) => {
                  const agent = agents.find(a => a.id === msg.agent);
                  return (
                    <div key={idx} className={`p-4 rounded-lg border ${agent?.color || 'border-slate-600'}`}>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold text-blue-400">{agent?.name}</span>
                        <span className="text-xs text-slate-500">
                          {msg.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm text-slate-300">{msg.message}</p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* BOTTOM: Voice Interaction Deck */}
        <div className="h-32 bg-slate-800 border-t border-slate-700 p-4 flex flex-col items-center justify-center relative">
          
          {/* Live Transcript Bubble */}
          {transcript && (
            <div className="absolute -top-12 bg-slate-900/90 backdrop-blur px-6 py-2 rounded-full border border-slate-600 text-sm shadow-lg transform transition-all">
              "{transcript}"
            </div>
          )}

          {isSpeaking && activeAgentData && (
            <div className="absolute -top-12 bg-slate-900/90 backdrop-blur px-6 py-2 rounded-full border border-blue-600 text-sm shadow-lg transform transition-all">
              <span className="text-blue-400">{activeAgentData.name}: </span>
              {conversation[conversation.length - 1]?.message.substring(0, 60)}...
            </div>
          )}

          <div className="flex items-center gap-6 w-full justify-center">
            {/* Voice Waveform Visualizer */}
            <div 
              ref={audioWaveformRef}
              className="h-8 w-32 flex items-end justify-center gap-1"
            >
              {[...Array(20)].map((_, i) => (
                <div
                  key={i}
                  className="wave-bar w-1 bg-blue-400 rounded-full transition-all duration-150"
                  style={{ height: '20%' }}
                />
              ))}
            </div>
            
            <button 
              onClick={handleVoiceInput}
              disabled={isListening || isSpeaking}
              className={`
                h-16 w-16 rounded-full flex items-center justify-center transition-all shadow-xl
                ${isListening 
                  ? 'bg-red-500 shadow-red-500/50 scale-110 animate-pulse' 
                  : isSpeaking
                  ? 'bg-green-500 shadow-green-500/50 scale-110'
                  : 'bg-blue-600 hover:bg-blue-500 hover:scale-105'
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            >
              <Mic className={`h-8 w-8 text-white ${isListening ? 'animate-pulse' : ''}`} />
            </button>
            
            {/* Voice Waveform Visualizer */}
            <div 
              ref={audioWaveformRef}
              className="h-8 w-32 flex items-end justify-center gap-1"
            >
              {[...Array(20)].map((_, i) => (
                <div
                  key={i}
                  className="wave-bar w-1 bg-blue-400 rounded-full transition-all duration-150"
                  style={{ height: '20%' }}
                />
              ))}
            </div>
          </div>

          {/* Active Agent Indicator */}
          <div className="absolute bottom-2 left-4 flex items-center gap-2 text-xs text-slate-500">
            <div className={`h-2 w-2 rounded-full ${isListening || isSpeaking ? 'bg-green-400 animate-pulse' : 'bg-slate-600'}`}></div>
            <span>Talking to: <span className="text-blue-400">{activeAgentData?.name}</span></span>
          </div>
        </div>
      </main>

      {/* RIGHT: The Agent Council Rail (35%) */}
      <aside className="w-80 bg-slate-950 border-l border-slate-800 flex flex-col overflow-y-auto custom-scrollbar">
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-2 mb-2">
            <Brain className="h-5 w-5 text-blue-400" />
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">The Council</div>
          </div>
          <p className="text-xs text-slate-600">Select an agent to consult</p>
        </div>
        
        <div className="flex-1 space-y-2 p-2">
          {agents.map((agent) => {
            const Icon = agent.icon;
            const isActive = activeAgent === agent.id;
            const isBusy = isActive && (isListening || isSpeaking);
            
            return (
              <div 
                key={agent.id}
                onClick={() => !isBusy && setActiveAgent(agent.id)}
                className={`
                  group relative flex items-center p-3 rounded-xl cursor-pointer transition-all duration-200 border-2
                  ${isActive 
                    ? `bg-slate-800 ${agent.color} shadow-lg scale-[1.02]` 
                    : 'bg-transparent border-transparent hover:bg-slate-900 hover:border-slate-700'
                  }
                  ${isBusy ? 'opacity-75 cursor-wait' : ''}
                `}
              >
                {/* Avatar Placeholder */}
                <div className={`
                  h-12 w-12 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 mr-4 overflow-hidden 
                  relative border-2 flex items-center justify-center
                  ${isActive ? 'border-white shadow-lg' : 'border-slate-600'}
                `}>
                  <Icon className={`h-6 w-6 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  
                  {/* Speaking/Listening Indicator */}
                  {isBusy && (
                    <div className="absolute inset-0 bg-blue-500/20 animate-pulse rounded-full"></div>
                  )}
                  
                  {isActive && isSpeaking && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-green-400 animate-pulse"></div>
                  )}
                  
                  {isActive && isListening && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-red-400 animate-pulse"></div>
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className={`
                    text-sm font-medium truncate
                    ${isActive ? 'text-white' : 'text-slate-400'}
                  `}>
                    {agent.name}
                  </h3>
                  <p className="text-xs text-slate-500 truncate">{agent.role}</p>
                  {isActive && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {agent.expertise.slice(0, 2).map((exp, idx) => (
                        <span key={idx} className="text-xs px-1.5 py-0.5 bg-slate-700/50 rounded text-slate-400">
                          {exp}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Status Dot */}
                <div className={`
                  h-2 w-2 rounded-full flex-shrink-0
                  ${isActive && isSpeaking
                    ? 'bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.8)]'
                    : isActive && isListening
                    ? 'bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.8)]'
                    : isActive
                    ? 'bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.8)]'
                    : 'bg-slate-600'
                  }
                `}></div>
              </div>
            );
          })}
        </div>

        {/* Active Agent Details */}
        {activeAgentData && (
          <div className={`p-4 border-t border-slate-800 ${activeAgentData.color}`}>
            <h4 className="text-sm font-semibold mb-2 text-white">{activeAgentData.name}</h4>
            <p className="text-xs text-slate-400 mb-3">{activeAgentData.description}</p>
            <div className="flex flex-wrap gap-1">
              {activeAgentData.expertise.map((exp, idx) => (
                <span key={idx} className="text-xs px-2 py-1 bg-slate-800/50 rounded text-slate-300">
                  {exp}
                </span>
              ))}
            </div>
          </div>
        )}
      </aside>
    </div>
  );
};

export default SecAIRadarLayout;

