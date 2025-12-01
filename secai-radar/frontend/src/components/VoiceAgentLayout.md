# Voice Agent Layout Component

## Overview

The `VoiceAgentLayout` component provides a compelling, professional interface for interacting with SecAI Radar's 7 specialized AI agent personas through real-time voice conversation.

## Features

### Visual Presence
- **7 Agent Avatars**: Each agent has a distinct visual identity with icons and color coding
- **Status Indicators**: Real-time status showing when agents are listening, speaking, or idle
- **Agent Panel**: Right sidebar displaying all agents simultaneously ("The Council")
- **Active Agent Highlighting**: Clear visual indication of the currently selected agent

### Voice Interaction
- **Voice Input**: Large microphone button with visual feedback
- **Voice Waveform**: Animated waveform visualization during listening/speaking
- **Live Transcript**: Real-time display of conversation
- **Conversation History**: Maintains conversation thread with each agent
- **Visual Feedback**: Pulsing animations, color changes, and status indicators

### Enhanced UX
- **Agent Details**: Shows agent description and expertise when selected
- **Conversation Thread**: Displays recent conversation history
- **Contextual States**: Different visual states for listening, speaking, thinking
- **Smooth Animations**: Professional animations for state transitions

## Component Structure

```
VoiceAgentLayout
├── Main Content Area (Left - 65%)
│   ├── Header
│   ├── Dynamic Content View
│   └── Conversation History
├── Voice Interaction Deck (Bottom)
│   ├── Live Transcript Bubble
│   ├── Voice Waveform Visualizer
│   ├── Microphone Button
│   └── Active Agent Indicator
└── Agent Council Rail (Right - 35%)
    ├── Agent List
    └── Active Agent Details
```

## Agent Personalities

1. **Dr. Aris Thorne** - Framework authority (Yellow theme)
2. **Leo Vance** - IAM specialist (Cyan theme)
3. **Ravi Patel** - Infrastructure expert (Orange theme)
4. **Kenji Sato** - Data analyst (Indigo theme)
5. **Elena Bridges** - Business strategist (Purple theme)
6. **Marcus Sterling** - Governance leader (Slate theme)
7. **Supervisor** - System orchestrator (Green theme)

## Usage

```tsx
import VoiceAgentLayout from './components/VoiceAgentLayout';

function App() {
  return <VoiceAgentLayout />;
}
```

## Integration Points

### Voice API Integration
The component is designed to integrate with:
- **Speech-to-Text**: Azure Speech Services, Google Speech-to-Text, or Whisper
- **Text-to-Speech**: Azure Neural Voices, Google Cloud TTS, or ElevenLabs
- **Real-time Processing**: WebSockets or Server-Sent Events

### Backend Integration
Connect to backend API endpoints:
- `/api/agents/{agentId}/chat` - Send message to agent
- `/api/agents/{agentId}/voice` - Real-time voice streaming
- WebSocket endpoint for bidirectional voice communication

## Future Enhancements

- [ ] Real voice input/output integration
- [ ] Avatar images/animations
- [ ] Lip-sync with voice output
- [ ] Agent recommendations based on context
- [ ] Multi-agent conversations
- [ ] Voice command shortcuts
- [ ] Conversation export/import
- [ ] Agent personality settings

## Styling

Uses Tailwind CSS with:
- Dark theme (slate-900, slate-800)
- Agent-specific color coding
- Smooth animations and transitions
- Responsive design considerations

