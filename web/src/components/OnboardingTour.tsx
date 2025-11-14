import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import Joyride, { Step, CallBackProps, STATUS, ACTIONS, EVENTS } from 'react-joyride'

interface OnboardingTourProps {
  runScriptMode?: boolean
  onScriptComplete?: () => void
}

const TOUR_STORAGE_KEY = 'secai-tour-completed'
const DEMO_TENANT = 'CONTOSO'

// Tour steps organized by route
const tourSteps: Record<string, Step[]> = {
  '/': [
    {
      target: 'body',
      content: 'Welcome to SecAI Radar! This interactive tour will guide you through the platform. You can skip it anytime by pressing ESC.',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '[data-tour="explore-demo"]',
      content: 'Start here to explore the interactive demo with pre-loaded sample data. Perfect for understanding the full assessment workflow.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="how-it-works"]',
      content: 'Learn about the SecAI Framework\'s capability-driven approach to security assessments.',
      placement: 'top',
    },
    {
      target: '[data-tour="demo-journey"]',
      content: 'These links take you directly to specific screens in the demo. Click any to jump to that part of the assessment.',
      placement: 'top',
    },
  ],
  [`/tenant/${DEMO_TENANT}/assessment`]: [
    {
      target: '[data-tour="progress-bar"]',
      content: 'Track your overall assessment progress here. This shows the percentage of controls completed across all security domains.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="quick-stats"]',
      content: 'Quick metrics: total controls, completed domains, identified gaps, and current status at a glance.',
      placement: 'bottom',
    },
    {
      target: '[data-tour="next-action"]',
      content: 'The system recommends your next step based on current progress. Follow this to maintain assessment momentum.',
      placement: 'top',
    },
    {
      target: '[data-tour="domain-grid"]',
      content: 'All 12 security domains are listed here. Click any domain to review its controls and enter evidence.',
      placement: 'top',
    },
  ],
  [`/tenant/${DEMO_TENANT}/dashboard`]: [
    {
      target: '[data-tour="radar-chart"]',
      content: 'The radar chart visualizes coverage across all security domains. Larger areas indicate better coverage.',
      placement: 'right',
    },
    {
      target: '[data-tour="domain-breakdown"]',
      content: 'Detailed breakdown by domain showing completion rates and capability scores.',
      placement: 'left',
    },
  ],
  [`/tenant/${DEMO_TENANT}/gaps`]: [
    {
      target: '[data-tour="ai-toggle"]',
      content: 'Enable AI-powered recommendations to get actionable guidance on addressing security gaps.',
      placement: 'left',
    },
    {
      target: '[data-tour="gap-explanation"]',
      content: 'Hard gaps are missing capabilities. Soft gaps are configuration issues with existing tools. Both need attention.',
      placement: 'top',
    },
    {
      target: '[data-tour="ai-usage"]',
      content: 'When AI is enabled, this panel shows token usage and cost metrics to help you monitor AI consumption.',
      placement: 'top',
    },
  ],
  [`/tenant/${DEMO_TENANT}/report`]: [
    {
      target: 'body',
      content: 'The executive report summarizes assessment results and AI-generated recommendations ready for export.',
      placement: 'center',
      disableBeacon: true,
    },
  ],
}

export default function OnboardingTour({ runScriptMode = false, onScriptComplete }: OnboardingTourProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const [run, setRun] = useState(false)
  const [stepIndex, setStepIndex] = useState(0)
  const [steps, setSteps] = useState<Step[]>([])
  const [scriptRoutes, setScriptRoutes] = useState<string[]>([])
  const [scriptPointer, setScriptPointer] = useState(0)

  const scriptActive = scriptRoutes.length > 0

  useEffect(() => {
    // Check if tour should run
    const tourCompleted = localStorage.getItem(TOUR_STORAGE_KEY)
    const currentPath = location.pathname

    // Get steps for current route
    const routeSteps = tourSteps[currentPath] || []

    if (routeSteps.length > 0) {
      setSteps(routeSteps)
      const shouldRun =
        scriptActive ||
        runScriptMode ||
        (!tourCompleted && currentPath === '/')

      if (shouldRun) {
        setRun(true)
        setStepIndex(0)
      } else {
        setRun(false)
      }
    } else {
      setRun(false)
    }
  }, [location.pathname, runScriptMode, scriptActive])

  const handleJoyrideCallback = (data: CallBackProps) => {
    const { status, action, index, type } = data

    if (status === STATUS.FINISHED || status === STATUS.SKIPPED) {
      setRun(false)
      
      // Mark tour as completed only in normal mode (not script mode)
      if (!runScriptMode && !scriptActive) {
        localStorage.setItem(TOUR_STORAGE_KEY, 'true')
      }
      
      // Notify script completion
      if (runScriptMode && onScriptComplete) {
        onScriptComplete()
      }

      if (scriptActive) {
        const nextIndex = scriptPointer + 1
        if (nextIndex < scriptRoutes.length) {
          setScriptPointer(nextIndex)
          setTimeout(() => navigate(scriptRoutes[nextIndex]), 150)
        } else {
          setScriptRoutes([])
          setScriptPointer(0)
          if (onScriptComplete) {
            onScriptComplete()
          }
        }
      }
    } else if (type === EVENTS.STEP_AFTER || type === EVENTS.TARGET_NOT_FOUND) {
      // Move to next step
      setStepIndex(index + (action === ACTIONS.PREV ? -1 : 1))
    }
  }

  // Expose method to restart tour
  useEffect(() => {
    const handleRestartTour = () => {
      localStorage.removeItem(TOUR_STORAGE_KEY)
      setStepIndex(0)
      setRun(true)
    }

    const handleRunScript = (event: Event) => {
      const detailTenant = (event as CustomEvent).detail?.tenantId || DEMO_TENANT
      const sequence = [
        '/',
        `/tenant/${detailTenant}/assessment`,
        `/tenant/${detailTenant}/dashboard`,
        `/tenant/${detailTenant}/gaps`,
        `/tenant/${detailTenant}/report`,
      ]
      setScriptRoutes(sequence)
      setScriptPointer(0)
      localStorage.removeItem(TOUR_STORAGE_KEY)
      setRun(true)
      setStepIndex(0)
      navigate(sequence[0])
    }

    window.addEventListener('secai-restart-tour', handleRestartTour)
    window.addEventListener('secai-start-demo-script', handleRunScript)
    return () => {
      window.removeEventListener('secai-restart-tour', handleRestartTour)
      window.removeEventListener('secai-start-demo-script', handleRunScript)
    }
  }, []);

  if (!run || steps.length === 0) {
    return null
  }

  return (
    <Joyride
      steps={steps}
      run={run}
      stepIndex={stepIndex}
      continuous
      showProgress
      showSkipButton
      disableCloseOnEsc={false}
      disableOverlayClose={false}
      callback={handleJoyrideCallback}
      styles={{
        options: {
          primaryColor: '#2563eb',
          zIndex: 10000,
        },
        tooltip: {
          borderRadius: 8,
          fontSize: 16,
        },
        buttonNext: {
          backgroundColor: '#2563eb',
          borderRadius: 6,
          padding: '8px 16px',
        },
        buttonBack: {
          color: '#6b7280',
          marginRight: 10,
        },
        buttonSkip: {
          color: '#6b7280',
        },
      }}
    />
  )
}

// Helper function to programmatically restart tour
export function restartTour() {
  window.dispatchEvent(new Event('secai-restart-tour'))
}

