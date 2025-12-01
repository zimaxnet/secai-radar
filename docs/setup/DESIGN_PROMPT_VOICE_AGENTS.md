# UI Design Prompt for SecAI Radar - Multi-Agent Voice Interface

## Prompt for Nano Banana Design Tool

---

**Create a compelling, professional user interface layout for SecAI Radar - a security assessment platform that features 7 specialized AI agent personas. The interface must enable real-time voice interaction with each agent, bringing their unique intellect and expertise to life through conversational voice responses.**

### Application Context

**SecAI Radar** is a corporate security assessment platform designed for security consultants and architects. It provides vendor-neutral security assessments, gap analysis, and actionable recommendations aligned with CAF, CIS, and NIST frameworks.

### The 7 Agent Personas

Each agent has a distinct personality, expertise area, and communication style:

1. **Dr. Aris Thorne** - Knowledge Base Guardian
   - **Role**: Principal Security Architect
   - **Personality**: Rigorous, framework-focused, uncompromising on standards
   - **Expertise**: CAF, CIS, NIST frameworks, security architecture
   - **Communication Style**: Academic, authoritative, cites frameworks
   - **Visual Identity**: Professional, intellectual, confident

2. **Leo Vance** - Identity & Access Analyst
   - **Role**: Identity & Access Management Specialist
   - **Personality**: Detail-oriented, compliance-focused, technical expert
   - **Expertise**: IAM, RBAC, conditional access, privilege management
   - **Communication Style**: Precise, methodical, compliance-focused
   - **Visual Identity**: Analytical, focused, trustworthy

3. **Ravi Patel** - Infrastructure Architect
   - **Role**: Cloud Infrastructure Specialist
   - **Personality**: Technical, systematic, infrastructure-focused
   - **Expertise**: Infrastructure scanning, CAF Landing Zones, topology mapping
   - **Communication Style**: Technical, practical, solution-oriented
   - **Visual Identity**: Technical, confident, action-oriented

4. **Kenji Sato** - Findings Analyst
   - **Role**: Data Analysis & Correlation Specialist
   - **Personality**: Analytical, data-driven, pattern-focused
   - **Expertise**: Data correlation, pattern detection, evidence analysis
   - **Communication Style**: Analytical, evidence-based, clear
   - **Visual Identity**: Thoughtful, analytical, detail-focused

5. **Elena Bridges** - Business Impact Strategist
   - **Role**: Business Communication & Risk Strategist
   - **Personality**: Business-focused, executive-oriented, risk-aware
   - **Expertise**: Risk quantification, executive reporting, ROI analysis
   - **Communication Style**: Business-oriented, executive-level, clear
   - **Visual Identity**: Professional, approachable, strategic

6. **Marcus Sterling** - Conflict Resolution & Governance
   - **Role**: Executive Decision Maker & Governance Specialist
   - **Personality**: Balanced, pragmatic, governance-focused
   - **Expertise**: Conflict resolution, trade-off analysis, stakeholder alignment
   - **Communication Style**: Executive, balanced, decisive
   - **Visual Identity**: Authoritative, balanced, leadership-focused

7. **Supervisor** - System Orchestrator
   - **Role**: Workflow Manager & Quality Assurance
   - **Personality**: Systematic, workflow-focused, quality-oriented
   - **Expertise**: Workflow orchestration, quality gates, audit trails
   - **Communication Style**: Organized, clear, systematic
   - **Visual Identity**: Coordinated, organized, reliable

### Design Requirements

#### 1. Visual Presence for All Agents

- **Agent Avatars**: Each agent must have a distinctive, professional avatar/face
  - High-quality, realistic or stylized representations
  - Reflects each agent's personality and role
  - Professional appearance suitable for corporate use
  - Diverse representation (age, ethnicity, gender) reflecting global team
  - Subtle visual indicators of expertise (e.g., Aris might have framework symbols)

- **Agent Layout**: 
  - Visible presence on screen at all times or easily accessible
  - Consider sidebar, floating panel, or dedicated agent zone
  - Each agent should be visually distinct and recognizable
  - Status indicators (available, speaking, thinking, processing)

#### 2. Voice Interaction Interface

- **Voice Input**:
  - Large, prominent microphone button/area
  - Visual feedback when listening (pulsing, waveform, etc.)
  - Ability to select which agent to talk to
  - Visual indication of which agent is being addressed

- **Voice Output**:
  - Lip-sync or facial animation when agent speaks
  - Subtle animations during speech (nodding, gestures)
  - Visual waveform or audio visualization during speech
  - Clear indication of which agent is speaking

- **Conversation Display**:
  - Chat transcript showing voice interactions
  - Agent responses displayed as text (optional)
  - Conversation history with each agent
  - Ability to replay or reference previous conversations

#### 3. Layout Structure

**Suggested Layout Components:**

1. **Main Content Area** (Center)
   - Current assessment/workflow view
   - Dashboard, controls, gaps analysis, etc.
   - Responsive to agent suggestions

2. **Agent Panel** (Right Sidebar or Floating)
   - All 7 agents visible in a grid or list
   - Each agent card showing:
     - Avatar/face
     - Name and role
     - Availability status
     - Recent activity indicator
   - Click to focus/select an agent
   - Hover for quick info

3. **Voice Interaction Zone** (Bottom or Integrated)
   - Large microphone button
   - Selected agent prominently displayed
   - Current conversation display
   - Voice controls (mute, pause, cancel)

4. **Agent Detail View** (Modal or Slide-out)
   - When agent is selected/active:
     - Larger avatar/face
     - Agent information (role, expertise)
     - Conversation interface
     - Knowledge areas/expertise tags

#### 4. Visual Design Principles

- **Professional & Corporate**: Suitable for enterprise security assessments
- **Modern & Engaging**: Compelling, not boring corporate UI
- **Accessible**: Clear visual hierarchy, readable fonts, good contrast
- **Responsive**: Works on desktop, tablet (mobile optional)
- **Dark/Light Mode**: Support for both themes
- **Color Coding**: Subtle color differentiation for agents (not overwhelming)

#### 5. Interaction Patterns

- **Agent Selection**: Click/tap agent to start conversation
- **Voice Activation**: Click microphone, speak, release when done
- **Visual Feedback**: Clear indicators for:
  - Listening state
  - Processing/thinking
  - Speaking/responding
  - Errors or issues

- **Context Awareness**: 
  - Agents understand current page/context
  - Suggestions based on workflow stage
  - Smart agent recommendations ("Ask Aris about framework alignment")

#### 6. Technical Considerations

- **Real-time Voice Processing**:
  - Low-latency voice-to-text
  - Real-time text-to-speech with natural voices
  - Voice activity detection
  - Noise cancellation

- **Agent Intelligence**:
  - Each agent maintains conversation context
  - Responses reflect agent's expertise and personality
  - Framework citations and references for Aris
  - Business-focused responses from Elena

- **Performance**:
  - Smooth animations
  - Responsive interactions
  - Efficient rendering of multiple agent avatars

### Design Style Inspiration

- **Corporate**: Microsoft Azure Portal, AWS Console (but more engaging)
- **Modern AI Tools**: ChatGPT interface, Claude.ai (but with multiple personas)
- **Professional Dashboards**: Tableau, Power BI (with personality)
- **Video Conferencing**: Zoom, Teams (for avatar inspiration)

### Key Visual Elements to Include

1. **Agent Avatars**: High-quality, diverse, professional
2. **Voice Waveform**: Visual representation of voice activity
3. **Status Indicators**: Available, speaking, thinking, busy
4. **Conversation Threads**: Organized by agent
5. **Context Indicators**: What page/context the user is in
6. **Quick Actions**: Easy access to common agent queries
7. **Agent Expertise Tags**: Visual representation of each agent's expertise

### User Experience Flow

1. User arrives at assessment page
2. Agents are visible and available
3. User asks question verbally or clicks agent
4. Selected agent's avatar animates (listening/thinking/speaking)
5. Agent responds with voice and text
6. Conversation continues naturally
7. Other agents can be consulted for different perspectives

### Design Deliverables Needed

- **Wireframe/Layout**: Overall structure and component placement
- **Agent Avatar Designs**: Visual concepts for all 7 agents
- **Voice Interaction UI**: Microphone, waveform, conversation display
- **State Variations**: Listening, speaking, thinking, idle
- **Responsive Layouts**: Desktop, tablet versions
- **Color Palette**: Professional, accessible, agent differentiation
- **Typography**: Clear, readable, professional
- **Iconography**: Consistent icon system
- **Animation Concepts**: How agents animate during interactions

### Success Criteria

The design should be:
- ✅ **Compelling**: Users want to interact with agents
- ✅ **Professional**: Suitable for corporate security assessments
- ✅ **Intuitive**: Easy to understand how to use voice interaction
- ✅ **Engaging**: Makes AI agents feel alive and present
- ✅ **Accessible**: Works for all users, including accessibility needs
- ✅ **Scalable**: Can accommodate future agents or features

---

## Additional Notes for Implementation

### Voice Technology Stack Recommendations
- **Speech Recognition**: Azure Speech Services, Google Speech-to-Text, or Whisper
- **Text-to-Speech**: Azure Neural Voices, Google Cloud Text-to-Speech, or ElevenLabs (for natural, expressive voices)
- **Voice Activity Detection**: Built into speech recognition services
- **Real-time Processing**: WebSockets or Server-Sent Events for streaming

### Agent Personality in Voice
- Different voice profiles for each agent (age, gender, accent)
- Speaking pace and style matches personality (Aris: methodical, Elena: executive, Ravi: technical)
- Emotional tone appropriate to context (professional but warm)

### Avatar Technology
- **Static Avatars**: Designed illustrations or photos
- **Animated Avatars**: ReadyPlayerMe, Microsoft Mesh, or custom solutions
- **Lip Sync**: Sync animations with voice output
- **Expression System**: Subtle facial expressions based on conversation context

---

**This prompt provides comprehensive context for creating a compelling, professional UI that brings the SecAI Radar agents to life through visual presence and real-time voice interaction.**

