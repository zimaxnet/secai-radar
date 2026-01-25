/**
 * Evidence Confidence Badge Component
 * Displays evidence confidence level (0-3) with tooltip
 */

import { getEvidenceConfidenceBadge, formatEvidenceConfidence } from '../../utils/copy'
import { useState } from 'react'

interface EvidenceConfidenceBadgeProps {
  confidence: 0 | 1 | 2 | 3
  showTooltip?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export default function EvidenceConfidenceBadge({
  confidence,
  showTooltip = true,
  size = 'md',
}: EvidenceConfidenceBadgeProps) {
  const [showTooltipState, setShowTooltipState] = useState(false)
  const badge = getEvidenceConfidenceBadge(confidence)

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  }

  const colorClasses = {
    0: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
    1: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    2: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    3: 'bg-green-500/20 text-green-400 border-green-500/30',
  }

  return (
    <div className="relative inline-block">
      <button
        className={`${sizeClasses[size]} rounded-lg font-medium border ${colorClasses[confidence]} hover:opacity-80 transition-opacity`}
        onMouseEnter={() => showTooltip && setShowTooltipState(true)}
        onMouseLeave={() => setShowTooltipState(false)}
        onClick={() => showTooltip && setShowTooltipState(!showTooltipState)}
      >
        {confidence}/3
      </button>
      {showTooltip && showTooltipState && (
        <div className="absolute z-50 mt-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg shadow-lg">
          <div className="text-sm font-semibold text-white mb-1">{badge.label}</div>
          <div className="text-xs text-slate-300">{badge.description}</div>
        </div>
      )}
    </div>
  )
}
