# Interactive Guidance & Voice Assistant

This page describes the in-app onboarding tour, contextual help assistant, and voice interaction features introduced in November 2025. All content applies to the `main` branch build deployed at `secai-radar.zimax.net` and is reflected in the wiki (`gh-pages`) branch.

---

## Onboarding Tour

### Overview
- Powered by **React Joyride**
- Automatically runs the first time a user visits the landing page
- Highlights critical UI elements across Landing, Assessment Overview, Dashboard, Gaps, and Report screens

### Controls
- **Restart tour**: Use the “Restart Tour” quick action in the help assistant
- **Skip**: Press `Esc` or click “Skip” in the tooltip
- **Scripted demo**: The “Run Guided Demo” action auto-navigates Landing ➜ Assessment ➜ Dashboard ➜ Gaps ➜ Report, pausing at each step with context

### Persistence
- Completion state stored in `localStorage` (`secai-tour-completed`)
- Clearing browser storage or choosing “Restart Tour” starts the journey over

---

## Help Assistant

### Features
- Floating widget anchored bottom-right of every route
- Context-aware Azure OpenAI responses with page metadata and tenant ID
- FAQ quick buttons for common topics (hard gaps, coverage scoring, recommendations)
- Quick actions to restart the tour or launch the scripted demo
- Token usage telemetry surfaced on the Gaps page for transparency

### Backend Endpoint
`POST /api/tenant/{tenantId}/ai/help`
- Request body: `{ "question": string, "context": Record<string, any> }`
- Response: `{ "answer": string, "tenantId": string, "context": {...} }`
- Uses existing Azure OpenAI credentials configured for other AI features

### Configuration Notes
- No additional secrets beyond `azure-openai-api-key`
- Respects existing fault handling in `api/shared/ai_service.py`
- Returns `503` when AI is not configured; the UI displays the error to the user

---

## Voice Interaction

### Architecture
- When the microphone toggle is enabled, the browser opens a **WebRTC** session to an Azure Function proxy.
- The proxy forwards the Session Description (SDP) to the **Azure OpenAI `gpt-realtime`** deployment.
- Audio streams directly to the model; responses stream back as synthesized speech.
- Typed questions still route through `gpt-5-chat` via the existing `/ai/help` endpoint.

### Endpoints & Configuration
- **Proxy endpoint**: `POST /api/realtime/session`
  - Body: `{ "sdpOffer": string, "deployment": "gpt-realtime" }`
  - Headers: `Content-Type: application/json`
  - Returns: SDP answer (`text/plain`)
- Environment variables required in the Function App:
  - `AZURE_OPENAI_REALTIME_ENDPOINT` (e.g., `https://<resource>.cognitiveservices.azure.com/openai/realtime`)
  - `AZURE_OPENAI_REALTIME_KEY`
  - `AZURE_OPENAI_REALTIME_DEPLOYMENT` (defaults to `gpt-realtime`)
  - Optional: `REALTIME_PROXY_ALLOWED_ORIGIN` for stricter CORS

### Browser Support
- Works on Chromium-based browsers (Edge, Chrome) and Safari 17+ where WebRTC + microphone access is available.
- If WebRTC is unavailable or permission is denied, the microphone button is disabled and users can fall back to typed questions.
- Audio playback uses an `<audio>` element injected by the assistant; no plugins required.

### Using Voice Mode
1. Open the help assistant (`?` button) and click the microphone.
2. Grant microphone access when prompted.
3. Speak naturally; responses stream back using the model's synthesized voice.
4. Click the microphone again to end the session. The assistant reverts to text-only mode automatically when the panel closes.

### Costs & Monitoring
- Azure bills Realtime usage per audio minute—track consumption via the Azure OpenAI metrics blade.
- The proxy logs session metadata (tenant, route, timestamps) for auditing; raw audio is not persisted.
- Consider setting alerts on the `gpt-realtime` deployment if you expect heavy voice usage.

### Accessibility Notes
- Text responses remain available in the transcript; users can still rely on browser speech synthesis for typed answers.
- Voice mode requires user consent for microphone access—document this in onboarding material for end users.

### Troubleshooting
- **Voice button disabled**: Browser lacks WebRTC support or microphone permission was denied.
- **No audio playback**: Ensure autoplay isn’t blocked and the site is allowed to play sound.
- **Connection drops**: Check network firewalls—WebRTC requires outbound UDP/TCP.

---

## Usage Metrics & Cost Awareness

- Gaps page shows Azure OpenAI token totals, run counts, and per-model breakdown when AI mode is enabled (`?ai=true`)
- Data sourced from the `AiUsage` table via the `/api/tenant/{tenantId}/ai/usage` endpoint
- Widget refreshes after each AI recommendation fetch to keep counts accurate

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Help panel shows “AI service not available” | Confirm `azure-openai-api-key` is present in Key Vault and Function App has access |
| Voice icon missing | Browser lacks Web Speech API support; use typed questions instead |
| Guided demo stops mid-way | Ensure pop-up blocker allows automated navigation and the tour is not already running |

---

## Related Links
- [Home](/wiki/Home)
- [AI Integration](/wiki/AI-Integration)
- [Development Workflow](/wiki/Development-Workflow)
