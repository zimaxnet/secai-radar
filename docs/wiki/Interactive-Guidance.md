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

### Voice Input
- Utilises the browser **Web Speech API** (`SpeechRecognition` / `webkitSpeechRecognition`)
- Supported in Chromium-based browsers and Safari (when SpeechRecognition is enabled)
- Microphone button toggles recognition; transcript is appended to the chat prompt
- Gracefully degrades when the API is unavailable (button hidden)

### Voice Output
- Uses browser **Speech Synthesis API** (`speechSynthesis`)
- Speaks Azure OpenAI answers automatically after each response
- Cancels previous utterances when a new answer arrives

### Accessibility
- Users can disable autoplay speech via browser settings
- Transcript remains visible in the assistant for reference

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
