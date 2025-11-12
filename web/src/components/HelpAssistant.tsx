import { FormEvent, useEffect, useMemo, useRef, useState } from 'react'
import { useLocation, useParams } from 'react-router-dom'
import { getAIHelp } from '../api'

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
  const [isRecording, setIsRecording] = useState(false)
  const [voiceSupported, setVoiceSupported] = useState(false)
  const recognitionRef = useRef<any>(null)
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

  // Setup voice capabilities (browser Web Speech API)
  useEffect(() => {
    const SpeechRecognitionConstructor =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (SpeechRecognitionConstructor) {
      setVoiceSupported(true)
      const recognition = new SpeechRecognitionConstructor()
      recognition.lang = 'en-US'
      recognition.interimResults = false
      recognition.maxAlternatives = 1

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = event.results[0][0].transcript
        setInput(prev => `${prev}${prev ? ' ' : ''}${transcript}`)
        setIsRecording(false)
      }

      recognition.onerror = () => {
        setIsRecording(false)
      }

      recognition.onend = () => {
        setIsRecording(false)
      }

      recognitionRef.current = recognition
    }

    return () => {
      if (recognitionRef.current?.stop) {
        recognitionRef.current.stop()
      }
      recognitionRef.current = null
    }
  }, [])

  const speakText = (text: string) => {
    if (!('speechSynthesis' in window)) {
      return
    }
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-US'
    utterance.rate = 1
    window.speechSynthesis.cancel()
    window.speechSynthesis.speak(utterance)
  }

  const handleVoiceToggle = () => {
    if (!recognitionRef.current) return
    if (isRecording) {
      recognitionRef.current.stop()
      setIsRecording(false)
    } else {
      try {
        recognitionRef.current.start()
        setIsRecording(true)
      } catch (error) {
        setIsRecording(false)
      }
    }
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
      speakText(answer)
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
                  {voiceSupported && (
                    <button
                      type="button"
                      onClick={handleVoiceToggle}
                      className={`w-8 h-8 rounded-full border flex items-center justify-center transition-colors ${
                        isRecording
                          ? 'border-red-500 text-red-600 bg-red-50'
                          : 'border-gray-300 text-gray-500 hover:bg-gray-100'
                      }`}
                      aria-label="Toggle voice input"
                    >
                      🎤
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
          </div>
        )}
      </div>
    </div>
  )
}
