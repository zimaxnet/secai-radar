import React, { useState, useEffect, useRef } from 'react';
import { Mic, Activity, Shield, Server, Users, BarChart, Brain, MessageSquare, Power, Volume2, Image as ImageIcon } from 'lucide-react';
import VisualWorkspace from './VisualWorkspace';

interface Agent {
  id: string;
  name: string;
  role: string;
  color: string;
  icon: React.ElementType;
  description: string;
  expertise: string[];
  voice: string;
  systemPrompt: string;
  image?: string;
  bio?: string;
}

const SecAIRadarLayout: React.FC = () => {
  const [activeAgent, setActiveAgent] = useState('Supervisor');
  const [isConnected, setIsConnected] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState<string>('');
  const [conversation, setConversation] = useState<Array<{ agent: string; message: string; timestamp: Date }>>([]);

  // Visual Generation State
  const [showVisualWorkspace, setShowVisualWorkspace] = useState(false);
  const [isGeneratingVisual, setIsGeneratingVisual] = useState(false);
  const [currentVisual, setCurrentVisual] = useState<string | null>(null);
  const [visualParams, setVisualParams] = useState<any>(null);

  const audioRef = useRef<HTMLAudioElement>(new Audio());
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const dataChannelRef = useRef<RTCDataChannel | null>(null);
  const audioWaveformRef = useRef<HTMLDivElement>(null);

  const agents: Agent[] = [
    {
      id: 'Thorne',
      name: 'Dr. Aris Thorne',
      role: 'Security Architect',
      color: 'border-yellow-500 bg-yellow-500/10',
      icon: Shield,
      description: 'Framework authority and security architecture expert',
      expertise: ['CAF', 'CIS', 'NIST', 'Security Architecture'],
      voice: 'echo',
      systemPrompt: "You are Dr. Aris Thorne, a Principal Security Architect. You are academic, rigorous, and uncompromising on security standards. You focus on Azure CAF alignment and Zero Trust.",
      image: '/assets/agents/aris_thorne.png',
      bio: "Dr. Aris Thorne is the intellectual bedrock of the team. A Principal Security Architect with decades of experience, he approaches every problem with academic rigor and an uncompromising standard for security. He views the cloud not just as infrastructure, but as a fortress that must be built on the unshakeable foundation of the Azure Cloud Adoption Framework."
    },
    {
      id: 'Vance',
      name: 'Leo Vance',
      role: 'IAM Analyst',
      color: 'border-cyan-500 bg-cyan-500/10',
      icon: Users,
      description: 'Identity and access management specialist',
      expertise: ['IAM', 'RBAC', 'Conditional Access', 'Privilege Management'],
      voice: 'alloy',
      systemPrompt: "You are Leo Vance, a Security Architect specializing in IAM. You are detail-oriented and technical. You focus on Entra ID, RBAC, and MCA billing roles.",
      image: '/assets/agents/leo_vance.png',
      bio: "Leo Vance lives in the details. As a Security Architect specializing in Identity and Access Management, he navigates the complex web of permissions, roles, and policies with surgical precision. He believes that in a Zero Trust world, identity is the new perimeter, and he guards it vigilantly."
    },
    {
      id: 'Patel',
      name: 'Ravi Patel',
      role: 'Infra Architect',
      color: 'border-orange-500 bg-orange-500/10',
      icon: Server,
      description: 'Cloud infrastructure and topology expert',
      expertise: ['Infrastructure', 'CAF Landing Zones', 'Topology', 'Scanning'],
      voice: 'ash',
      systemPrompt: "You are Ravi Patel, a Security Engineer. You are technical, code-centric, and task-focused. You translate designs into Terraform/Bicep and run security scans.",
      image: '/assets/agents/ravi_patel.png',
      bio: "Ravi Patel is the builder. A hands-on Security Engineer who prefers code to theory, he translates high-level architectural designs into concrete, secure infrastructure. Whether it's writing Terraform scripts or analyzing vulnerability scans, Ravi ensures that the rubber meets the road safely and efficiently."
    },
    {
      id: 'Sato',
      name: 'Kenji Sato',
      role: 'Findings Analyst',
      color: 'border-indigo-500 bg-indigo-500/10',
      icon: BarChart,
      description: 'Data correlation and pattern detection specialist',
      expertise: ['Data Analysis', 'Pattern Detection', 'Evidence Analysis', 'Correlation'],
      voice: 'sage',
      systemPrompt: "You are Kenji Sato, a Program Manager. You are meticulous, organized, and schedule-driven. You focus on tracking dependencies, schedules, and status reporting.",
      image: '/assets/agents/kenji_sato.png',
      bio: "Kenji Sato is the heartbeat of the project. As a Program Manager, he transforms chaos into order, ensuring that every dependency is tracked, every risk is identified, and every deadline is met. His meticulous nature and organizational prowess keep the complex machinery of the migration moving forward smoothly."
    },
    {
      id: 'Bridges',
      name: 'Elena Bridges',
      role: 'Business Strategist',
      color: 'border-purple-500 bg-purple-500/10',
      icon: MessageSquare,
      description: 'Business impact and executive communication expert',
      expertise: ['Risk Quantification', 'Executive Reporting', 'ROI Analysis', 'Governance'],
      voice: 'shimmer',
      systemPrompt: "You are Elena Bridges, a Relationship Manager. You are empathetic and business-focused. You translate technical risks into business impact and protect customer interests.",
      image: '/assets/agents/elena_bridges.png',
      bio: "Elena Bridges is the bridge between technology and business. As a Relationship Manager, she speaks both languages fluently, translating technical risks into business impacts and ensuring that the migration serves the organization's strategic goals. She is the voice of the customer, ensuring their needs are never lost in the technical details."
    },
    {
      id: 'Sterling',
      name: 'Marcus Sterling',
      role: 'Governance',
      color: 'border-slate-300 bg-slate-300/10',
      icon: Shield,
      description: 'Conflict resolution and governance specialist',
      expertise: ['Conflict Resolution', 'Trade-off Analysis', 'Stakeholder Alignment', 'Governance'],
      voice: 'verse',
      systemPrompt: "You are Marcus Sterling, a Senior Manager. You are decisive and risk-averse. You focus on the Iron Triangle (Scope, Cost, Time) and make executive decisions.",
      image: '/assets/agents/marcus_sterling.png',
      bio: "Marcus Sterling is the steady hand at the helm. As the Senior Project Lead, he balances the competing demands of scope, cost, and time with decisive leadership. Risk-averse but pragmatic, he makes the tough calls that keep the project aligned with its executive mandate."
    },
    {
      id: 'Supervisor',
      name: 'System Orchestrator',
      role: 'Orchestrator',
      color: 'border-green-500 bg-green-500/10',
      icon: Activity,
      description: 'Workflow management and quality assurance',
      expertise: ['Workflow Orchestration', 'Quality Gates', 'Audit Trails', 'Synthesis'],
      voice: 'alloy',
      systemPrompt: "You are the System Orchestrator. You manage the workflow and ensure quality. You are helpful, neutral, and efficient.",
      bio: "The System Orchestrator is the central nervous system of the operation. It manages the workflow, ensures quality gates are met, and maintains the audit trail. Helpful, neutral, and efficient, it synthesizes the inputs from all agents to drive the mission forward."
    },
  ];

  const activeAgentData = agents.find(a => a.id === activeAgent);

  // Initialize WebRTC
  const startSession = async () => {
    try {
      const pc = new RTCPeerConnection();
      peerConnectionRef.current = pc;

      // Handle remote audio
      pc.ontrack = (event) => {
        audioRef.current.srcObject = event.streams[0];
        audioRef.current.play();
      };

      // Handle data channel
      const dc = pc.createDataChannel("oai-events");
      dataChannelRef.current = dc;

      dc.onmessage = (e) => {
        const event = JSON.parse(e.data);
        if (event.type === 'response.audio_transcript.delta') {
          setTranscript(prev => prev + event.delta);
          setIsSpeaking(true);
        } else if (event.type === 'response.done') {
          setIsSpeaking(false);
          if (event.response?.output?.[0]?.content?.[0]?.transcript) {
            setConversation(prev => [
              ...prev,
              {
                agent: activeAgent,
                message: event.response.output[0].content[0].transcript,
                timestamp: new Date()
              }
            ]);
            setTranscript('');
          }
        }
      };

      // Get microphone stream
      const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
      pc.addTrack(ms.getTracks()[0], ms);

      // Create offer
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      // Send to backend
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
      const response = await fetch(`${baseUrl}/realtime/session`, {
        method: "POST",
        body: JSON.stringify({ sdpOffer: offer.sdp }),
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) throw new Error('Failed to start session');

      const answer = await response.text();
      await pc.setRemoteDescription({ type: "answer", sdp: answer });

      setIsConnected(true);

      // Initial configuration for the active agent
      if (activeAgentData && dc.readyState === 'open') {
        updateAgentPersona(activeAgentData);
      } else {
        dc.onopen = () => {
          if (activeAgentData) updateAgentPersona(activeAgentData);
        };
      }

    } catch (err) {
      console.error("Failed to start session:", err);
      alert("Failed to connect to voice server. Check console for details.");
    }
  };

  const stopSession = () => {
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }
    setIsConnected(false);
    setIsSpeaking(false);
  };

  const updateAgentPersona = (agent: Agent) => {
    if (dataChannelRef.current?.readyState === 'open') {
      const event = {
        type: "session.update",
        session: {
          voice: agent.voice,
          instructions: agent.systemPrompt,
        },
      };
      dataChannelRef.current.send(JSON.stringify(event));

      // Also trigger a greeting
      const responseCreate = {
        type: "response.create",
        response: {
          modalities: ["text", "audio"],
          instructions: `Greet the user as ${agent.name}. Keep it brief.`,
        },
      };
      dataChannelRef.current.send(JSON.stringify(responseCreate));
    }
  };

  // Switch agent handler
  const handleAgentSwitch = (agentId: string) => {
    setActiveAgent(agentId);
    const agent = agents.find(a => a.id === agentId);
    if (agent && isConnected) {
      updateAgentPersona(agent);
    }
  };

  // Waveform animation
  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(() => {
        if (audioWaveformRef.current) {
          const bars = audioWaveformRef.current.querySelectorAll('.wave-bar');
          bars.forEach((bar: Element) => {
            const height = isSpeaking ? Math.random() * 60 + 20 : 10;
            (bar as HTMLElement).style.height = `${height}%`;
          });
        }
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isConnected, isSpeaking]);

  // Mock Trigger for Visual Generation
  const handleGenerateVisual = () => {
    if (!activeAgentData) return;

    let visualFile = '';
    let params = {};

    switch (activeAgentData.id) {
      case 'Thorne':
        visualFile = '/assets/generated/architecture_diagram_v1.svg';
        params = {
          type: "diagram",
          style: "blueprint",
          elements: ["hub", "spoke", "firewall"],
          narrative: "Drafting the Hub & Spoke network topology based on Azure CAF standards..."
        };
        break;
      case 'Vance':
        visualFile = '/assets/generated/threat_model_graph.svg';
        params = {
          type: "graph",
          style: "threat_model",
          elements: ["attacker", "firewall", "app_server", "db"],
          narrative: "Mapping potential attack vectors and data flow boundaries..."
        };
        break;
      case 'Sato':
        visualFile = '/assets/generated/migration_timeline.svg';
        params = {
          type: "chart",
          style: "gantt",
          phases: ["Assessment", "Migration", "Optimization"],
          narrative: "Visualizing the migration phases and critical path dependencies..."
        };
        break;
      default:
        return; // No visual for others in this demo
    }

    setShowVisualWorkspace(true);
    setIsGeneratingVisual(true);
    setVisualParams(params);

    // Simulate generation delay
    setTimeout(() => {
      setIsGeneratingVisual(false);
      setCurrentVisual(visualFile);
    }, 3000);
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden relative">

      {/* Visual Workspace Overlay */}
      {showVisualWorkspace && (
        <VisualWorkspace
          isGenerating={isGeneratingVisual}
          currentVisual={currentVisual}
          jsonParams={visualParams}
          onClose={() => setShowVisualWorkspace(false)}
        />
      )}

      {/* LEFT: Main Workflow / Assessment Area (65%) */}
      <main className="flex-1 flex flex-col border-r border-slate-700">
        <header className="h-16 border-b border-slate-700 flex items-center px-6 bg-slate-800/50 justify-between">
          <div className="flex items-center">
            <Shield className="text-blue-400 mr-3" />
            <h1 className="text-xl font-semibold tracking-wide">
              SecAI RADAR
              <span className="text-xs bg-blue-600 px-2 py-0.5 rounded ml-2">VOICE INTERFACE</span>
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${isConnected ? 'bg-green-500/20 text-green-400' : 'bg-slate-700 text-slate-400'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-slate-500'}`}></div>
              {isConnected ? 'LIVE CONNECTION' : 'DISCONNECTED'}
            </div>
          </div>
        </header>

        {/* Dynamic Content View */}
        <div className="flex-1 p-8 overflow-y-auto relative">
          <div className="bg-slate-800/40 rounded-xl border border-slate-700 p-8 h-full shadow-inner flex flex-col">
            <div className="flex items-start justify-between mb-8">
              <div>
                <h2 className="text-3xl mb-2 font-light text-white">
                  {activeAgentData?.name}
                </h2>
                <p className="text-blue-400 text-lg">{activeAgentData?.role}</p>
              </div>
              <div className={`p-1 rounded-full ${activeAgentData?.color} border-2 border-slate-600 overflow-hidden w-32 h-32 flex items-center justify-center`}>
                {activeAgentData?.image ? (
                  <img src={activeAgentData.image} alt={activeAgentData.name} className="w-full h-full object-cover rounded-full" />
                ) : (
                  activeAgentData && <activeAgentData.icon className="w-16 h-16 text-white" />
                )}
              </div>
            </div>

            {activeAgentData?.bio && (
              <div className="mb-6 p-4 bg-slate-900/30 rounded-lg border border-slate-700/50">
                <p className="text-slate-300 text-sm leading-relaxed italic">
                  "{activeAgentData.bio}"
                </p>
              </div>
            )}

            <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
              {conversation.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-50">
                  <Volume2 className="w-16 h-16 mb-4" />
                  <p>Start a session to speak with the team</p>
                </div>
              ) : (
                conversation.map((msg, idx) => {
                  const agent = agents.find(a => a.id === msg.agent);
                  return (
                    <div key={idx} className={`p-4 rounded-lg border bg-slate-800/50 ${agent?.color || 'border-slate-600'}`}>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold text-blue-400">{agent?.name}</span>
                        <span className="text-xs text-slate-500">
                          {msg.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-slate-200 leading-relaxed">{msg.message}</p>
                    </div>
                  );
                })
              )}
            </div>

            {/* Live Transcript */}
            {transcript && (
              <div className="mt-4 p-3 bg-slate-900/50 rounded border border-slate-700 text-slate-300 text-sm italic">
                "{transcript}..."
              </div>
            )}

          </div>
        </div>

        {/* BOTTOM: Voice Interaction Deck */}
        <div className="h-32 bg-slate-800 border-t border-slate-700 p-4 flex flex-col items-center justify-center relative">

          <div className="flex items-center gap-8 w-full justify-center">
            {/* Voice Waveform Visualizer */}
            <div
              ref={audioWaveformRef}
              className="h-12 w-48 flex items-end justify-center gap-1 opacity-80"
            >
              {[...Array(20)].map((_, i) => (
                <div
                  key={i}
                  className="wave-bar w-1.5 bg-blue-400 rounded-full transition-all duration-100"
                  style={{ height: '10%' }}
                />
              ))}
            </div>

            <button
              onClick={isConnected ? stopSession : startSession}
              className={`
                h-16 w-16 rounded-full flex items-center justify-center transition-all shadow-xl border-4
                ${isConnected
                  ? 'bg-red-500 border-red-600 hover:bg-red-600 shadow-red-500/20'
                  : 'bg-blue-600 border-blue-500 hover:bg-blue-500 shadow-blue-500/20 hover:scale-105'
                }
              `}
            >
              {isConnected ? (
                <Power className="h-6 w-6 text-white" />
              ) : (
                <Mic className="h-6 w-6 text-white" />
              )}
            </button>

            {/* Mirrored Waveform */}
            <div
              className="h-12 w-48 flex items-end justify-center gap-1 opacity-80"
            >
              {/* Just a visual balance, static or mirrored if needed */}
              {[...Array(20)].map((_, i) => (
                <div
                  key={i}
                  className="w-1.5 bg-slate-700 rounded-full"
                  style={{ height: '10%' }}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Visual Trigger Button (Demo) */}
        <div className="absolute right-8 top-1/2 -translate-y-1/2">
          <button
            onClick={handleGenerateVisual}
            disabled={!['Thorne', 'Vance', 'Sato'].includes(activeAgent || '')}
            className={`
                flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all
                ${['Thorne', 'Vance', 'Sato'].includes(activeAgent || '')
                ? 'bg-slate-700 hover:bg-slate-600 text-white shadow-lg'
                : 'bg-slate-800/50 text-slate-600 cursor-not-allowed'}
              `}
            title="Ask agent to generate a visual"
          >
            <ImageIcon className="h-4 w-4" />
            <span>Generate Visual</span>
          </button>
        </div>

        {/* Active Agent Indicator */}
        <div className="absolute bottom-2 left-4 flex items-center gap-2 text-xs text-slate-500">
          <span>Voice: <span className="text-blue-400 font-mono">{activeAgentData?.voice.toUpperCase()}</span></span>
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

            return (
              <div
                key={agent.id}
                onClick={() => handleAgentSwitch(agent.id)}
                className={`
                  group relative flex items-center p-3 rounded-xl cursor-pointer transition-all duration-200 border-2
                  ${isActive
                    ? `bg-slate-800 ${agent.color} shadow-lg scale-[1.02]`
                    : 'bg-transparent border-transparent hover:bg-slate-900 hover:border-slate-700'
                  }
                `}
              >
                {/* Avatar Placeholder */}
                <div className={`
                  h-12 w-12 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 mr-4 overflow-hidden 
                  relative border-2 flex items-center justify-center
                  ${isActive ? 'border-white shadow-lg' : 'border-slate-600'}
                `}>
                  {agent.image ? (
                    <img src={agent.image} alt={agent.name} className="w-full h-full object-cover" />
                  ) : (
                    <Icon className={`h-6 w-6 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  )}

                  {isActive && isSpeaking && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-green-400 animate-pulse"></div>
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
                </div>

                {/* Status Dot */}
                <div className={`
                  h-2 w-2 rounded-full flex-shrink-0
                  ${isActive && isConnected
                    ? 'bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.8)]'
                    : isActive
                      ? 'bg-blue-400'
                      : 'bg-slate-600'
                  }
                `}></div>
              </div>
            );
          })}
        </div>
      </aside>
    </div>
  );
};

export default SecAIRadarLayout;
