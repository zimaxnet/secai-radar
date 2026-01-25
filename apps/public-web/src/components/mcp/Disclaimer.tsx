/**
 * Disclaimer Component
 * Shows standard disclaimers about risk posture assessment
 */

import { DISCLAIMERS } from '../../utils/copy'

interface DisclaimerProps {
  variant?: 'short' | 'long' | 'methodology'
  className?: string
}

export default function Disclaimer({ variant = 'short', className = '' }: DisclaimerProps) {
  const text = DISCLAIMERS[variant]

  return (
    <div className={`text-xs text-slate-500 ${className}`}>
      <p>{text}</p>
    </div>
  )
}
