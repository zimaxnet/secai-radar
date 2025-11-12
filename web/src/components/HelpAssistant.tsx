import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useLocation, useParams } from 'react-router-dom'
import { createRealtimeSession, getAIHelp } from '../api'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const FAQ_ITEMS: Array<{ question: string; answer?: string; prompt?: string }> = [
  {
    question: 'What is a hard gap?',
    prompt: 'Explain what a hard gap means in SecAI Radar and how to resolve it.'
  },
  {
    question: 'How is coverage calculated?',
    prompt: 'Describe how control coverage is calculated, including weights and tool strength.'
  },
  {
    question: 'Where do recommendations come from?',
    prompt: 'Explain how AI recommendations are generated for gaps and what data they use.'
  }
]

function derivePageContext(pathname: string): { page: string; description: string } {
  if (pathname === '/' ) {
    return { page: 'Landing', description: 'Landing page with overview cards and demo journey' }
  }
  if (pathname.includes('/assessment')) {
    return { page: 'Assessment Overview', description: 'Progress dashboard showing overall assessment status and next steps' }
  }
  if (pathname.includes('/dashboard')) {
    return { page: 'Dashboard', description: 'Radar chart and domain breakdown with coverage metrics' }
  }
  if (pathname.includes('/gaps')) {
    return { page: 'Gaps', description: 'Gap analysis with hard/soft gaps and AI recommendations' }
  }
  if (pathname.includes('/controls')) {
    return { page: 'Controls', description: 'Control list with filtering and evidence status' }
  }
  if (pathname.includes('/report')) {
    return { page: 'Report', description: 'Generated assessment report with executive summary and data exports' }
  }
  if (pathname.includes('/tools')) {
    return { page: 'Tools', description: 'Security tool inventory with capability mappings' }
  }
  return { page: 'Unknown', description: 'Navigate within the SecAI Radar app' }
}

export default function HelpAssistant() {
  const location = useLocation()
  const params = useParams<{ id?: string }>()
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [voiceState, setVoiceState] = useState<'idle' | 'connecting' | 'connected' | 'error'>('idle')
  const [voiceError, setVoiceError] = useState<string | null>(null)
  const [realtimeSupported, setRealtimeSupported] = useState(false)
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const remoteAudioRef = useRef<HTMLAudioElement | null>(null)
  const dataChannelRef = useRef<RTCDataChannel | null>(null)
  const realtimeDeployment = (import.meta.env.VITE_REALTIME_DEPLOYMENT as string | undefined) || undefined
  const tenantId = params.id || (import.meta.env.VITE_DEFAULT_TENANT as string) || 'NICO'

  const context = useMemo(() => derivePageContext(location.pathname), [location.pathname])

  useEffect(() => {
    if (!isOpen) return
    setMessages(prev => {
      if (prev.length === 0) {
        return [
          {
            role: 'assistant',
            content: `Hi there! You're on the ${context.page} page. Ask me anything about this screen or the SecAI Framework.`
          }
        ]
      }
      return prev
    })
  }, [context.page, isOpen])

  const detectRealtimeSupport = useCallback(() => {
    if (typeof window === 'undefined' || typeof navigator === 'undefined') {
      return false
    }
    const hasPeer = 'RTCPeerConnection' in window || 'webkitRTCPeerConnection' in window
    const hasMedia = !!navigator.mediaDevices?.getUserMedia
    return hasPeer && hasMedia
  }, [])

  useEffect(() => {
    setRealtimeSupported(detectRealtimeSupport())
  }, [detectRealtimeSupport])

  const stopVoiceSession = useCallback((options: { preserveError?: boolean } = {}) => {
    dataChannelRef.current?.close()
    dataChannelRef.current = null

    peerConnectionRef.current?.close()
    peerConnectionRef.current = null

    mediaStreamRef.current?.getTracks().forEach(track => track.stop())
    mediaStreamRef.current = null

    if (remoteAudioRef.current) {
      remoteAudioRef.current.srcObject = null
    }

    if (!options.preserveError) {
      setVoiceError(null)
    }
    setVoiceState('idle')
  }, [])

  useEffect(() => () => stopVoiceSession(), [stopVoiceSession])

  const sendRealtimeInstructions = useCallback(() => {
    if (dataChannelRef.current?.readyState === 'open') {
      const instructions = `You are the SecAI Radar help assistant. The user is currently on the ${context.page} page. ${context.description}`
      try {
        dataChannelRef.current.send(JSON.stringify({
          type: 'response.create',
          response: {
            instructions,
            modalities: ['audio'],
          },
        }))
      } catch (err) {
        console.warn('Failed to send realtime instructions', err)
      }
    }
  }, [context.description, context.page])

  useEffect(() => {
    if (voiceState === 'connected') {
      sendRealtimeInstructions()
    }
  }, [voiceState, sendRealtimeInstructions])

  useEffect(() => {
    if (!isOpen && voiceState !== 'idle') {
      stopVoiceSession()
    }
  }, [isOpen, voiceState, stopVoiceSession])

  const waitForIceGathering = useCallback((pc: RTCPeerConnection) => {
    if (pc.iceGatheringState === 'complete') {
      return Promise.resolve(pc.localDescription?.sdp ?? '')
    }

    return new Promise<string>((resolve) => {
      const checkState = () => {
        if (pc.iceGatheringState === 'complete') {
          pc.removeEventListener('icegatheringstatechange', checkState)
          resolve(pc.localDescription?.sdp ?? '')
        }
      }

      pc.addEventListener('icegatheringstatechange', checkState)
      setTimeout(() => {
        pc.removeEventListener('icegatheringstatechange', checkState)
        resolve(pc.localDescription?.sdp ?? '')
      }, 2000)
    })
  }, [])

  const startVoiceSession = useCallback(async () => {
    if (!realtimeSupported) {
      setVoiceError('Voice interaction is not available in this browser.')
      return
    }

    if (voiceState === 'connecting' || voiceState === 'connected') {
      return
    }

    setVoiceError(null)
    setVoiceState('connecting')

    try {
      const PeerConnectionCtor = (window as any).RTCPeerConnection || (window as any).webkitRTCPeerConnection
      const pc: RTCPeerConnection = PeerConnectionCtor ? new PeerConnectionCtor() : new RTCPeerConnection()
      peerConnectionRef.current = pc

      pc.ontrack = (event) => {
        if (remoteAudioRef.current) {
          remoteAudioRef.current.srcObject = event.streams[0]
        }
      }

      pc.onconnectionstatechange = () => {
        if (pc.connectionState === 'connected') {
          setVoiceState('connected')
        }
        if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected') {
          setVoiceError('Voice connection lost.')
          stopVoiceSession({ preserveError: true })
          setVoiceState('error')
        }
      }

      pc.ondatachannel = (event) => {
        const channel = event.channel
        channel.onmessage = (messageEvent) => {
          // Future enhancement: surface realtime transcripts or metadata in the UI.
          console.debug('Realtime event:', messageEvent.data)
        }
      }

      const controlChannel = pc.createDataChannel('oai-events')
      dataChannelRef.current = controlChannel
      controlChannel.onopen = () => {
        sendRealtimeInstructions()
      }
      controlChannel.onmessage = (event) => {
        console.debug('Realtime message:', event.data)
      }

      const localStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaStreamRef.current = localStream
      localStream.getTracks().forEach(track => pc.addTrack(track, localStream))

      const offer = await pc.createOffer({ offerToReceiveAudio: true, offerToReceiveVideo: false })
      await pc.setLocalDescription(offer)

      const localSdp = await waitForIceGathering(pc)
      if (!localSdp) {
        throw new Error('Unable to gather local SDP information.')
      }

      const answerSdp = await createRealtimeSession(localSdp, { deployment: realtimeDeployment })
      const answer: RTCSessionDescriptionInit = { type: 'answer', sdp: answerSdp }
      await pc.setRemoteDescription(answer)

      setMessages(prev => ([
        ...prev,
        { role: 'assistant', content: '🎤 Voice assistant is ready. Start speaking when you are ready and click the mic to stop.' }
      ]))
      setVoiceState('connected')
    } catch (error: any) {
      console.error('Failed to start voice session', error)
      setVoiceError(error?.message || 'Failed to start voice session.')
      stopVoiceSession({ preserveError: true })
      setVoiceState('error')
    }
  }, [realtimeDeployment, realtimeSupported, sendRealtimeInstructions, stopVoiceSession, voiceState, waitForIceGathering])

  const handleVoiceToggle = async () => {
    if (voiceState === 'connected' || voiceState === 'connecting') {
      stopVoiceSession()
      return
    }

    await startVoiceSession()
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const question = input.trim()
    if (!question) return
    setInput('')

    const userMessage: Message = { role: 'user', content: question }
    setMessages(prev => [...prev, userMessage])

    setIsLoading(true)
    try {
      const response = await getAIHelp(tenantId, question, {
        page: context.page,
        description: context.description,
        pathname: location.pathname
      })
      const answer = response.answer || 'I could not fetch a response just now.'
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: answer }
      ])
      // speakText(answer) // This function is no longer used for voice
    } catch (error: any) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: error?.message || 'Something went wrong fetching the answer.' }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleFAQClick = async (item: typeof FAQ_ITEMS[number]) => {
    const prompt = item.prompt || item.question
    setInput(prompt)
    setIsOpen(true)
  }

  const handleRunDemo = () => {
    window.dispatchEvent(new CustomEvent('secai-start-demo-script', { detail: { tenantId } }))
  }

  return (
    <div className="fixed bottom-6 right-6 z-40">
      <div className="flex flex-col items-end gap-3">
        <button
          type="button"
          className="rounded-full bg-blue-600 text-white shadow-lg w-14 h-14 flex items-center justify-center text-2xl hover:bg-blue-700 transition-colors"
          onClick={() => setIsOpen(prev => !prev)}
          aria-label="Toggle help assistant"
        >
          {isOpen ? '×' : '?'}
        </button>

        {isOpen && (
          <div className="w-80 max-h-[32rem] bg-white border border-gray-200 rounded-xl shadow-2xl overflow-hidden flex flex-col">
            <div className="bg-blue-600 text-white px-4 py-3">
              <div className="text-sm uppercase tracking-wide text-blue-200">Need help?</div>
              <div className="text-lg font-semibold">SecAI Assistant</div>
              <div className="text-xs text-blue-100 mt-1">Page: {context.page}</div>
            </div>

            <div className="px-4 py-3 border-b border-gray-200">
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Quick actions</div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className="text-xs px-3 py-1 rounded-full border border-blue-200 text-blue-600 hover:bg-blue-50"
                  onClick={handleRunDemo}
                >
                  Run Guided Demo
                </button>
                <button
                  type="button"
                  className="text-xs px-3 py-1 rounded-full border border-blue-200 text-blue-600 hover:bg-blue-50"
                  onClick={() => window.dispatchEvent(new Event('secai-restart-tour'))}
                >
                  Restart Tour
                </button>
              </div>
            </div>

            <div className="px-4 py-3 border-b border-gray-200 max-h-32 overflow-y-auto">
              <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">FAQ</div>
              <div className="flex flex-wrap gap-2">
                {FAQ_ITEMS.map(item => (
                  <button
                    key={item.question}
                    type="button"
                    className="text-xs px-3 py-1 rounded-full border border-gray-200 text-gray-700 hover:bg-gray-100"
                    onClick={() => handleFAQClick(item)}
                  >
                    {item.question}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 text-sm">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`rounded-lg px-3 py-2 ${msg.role === 'assistant' ? 'bg-blue-50 text-blue-900 self-start' : 'bg-gray-900 text-white self-end'}`}
                >
                  {msg.content}
                </div>
              ))}
              {isLoading && (
                <div className="rounded-lg px-3 py-2 bg-blue-50 text-blue-700">Thinking…</div>
              )}
            </div>

            <form onSubmit={handleSubmit} className="border-t border-gray-200 p-3">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={`Ask about ${context.page}…`}
                className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring focus:ring-blue-200"
                rows={2}
              />
              <div className="mt-2 flex justify-between items-center">
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <span>AI answers use Azure OpenAI</span>
                  {realtimeSupported && (
                    <button
                      type="button"
                      onClick={handleVoiceToggle}
                      className={`w-8 h-8 rounded-full border flex items-center justify-center transition-colors ${
                        voiceState === 'connected'
                          ? 'border-red-500 text-red-600 bg-red-50'
                          : voiceState === 'connecting'
                            ? 'border-blue-400 text-blue-600 bg-blue-50 animate-pulse'
                            : 'border-gray-300 text-gray-500 hover:bg-gray-100'
                      }`}
                      aria-label={voiceState === 'connected' ? 'Stop voice assistant' : 'Start voice assistant'}
                    >
                      {voiceState === 'connected' ? '■' : '🎤'}
                    </button>
                  )}
                </div>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 disabled:opacity-50"
                  disabled={isLoading}
                >
                  Send
                </button>
              </div>
            </form>

            {voiceState !== 'idle' && (
              <div className="px-4 pb-3 text-xs text-gray-500">
                {voiceState === 'connecting' && 'Connecting to voice assistant…'}
                {voiceState === 'connected' && 'Voice assistant active. Your microphone is live.'}
                {voiceState === 'error' && voiceError}
              </div>
            )}

            {!realtimeSupported && (
              <div className="px-4 pb-3 text-xs text-gray-500">
                Voice mode requires a WebRTC-enabled browser with microphone access.
              </div>
            )}
          </div>
        )}
      </div>
      <audio ref={remoteAudioRef} className="hidden" autoPlay />
    </div>
  )
}
