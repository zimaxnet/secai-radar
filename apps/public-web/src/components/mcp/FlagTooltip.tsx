/**
 * Flag Tooltip Component
 * Shows flag definition on hover/click
 */

import { getFlagDefinition } from '../../utils/copy'
import { useState } from 'react'

interface FlagTooltipProps {
  flagName: string
  children: React.ReactNode
}

export default function FlagTooltip({ flagName, children }: FlagTooltipProps) {
  const [showTooltip, setShowTooltip] = useState(false)
  const definition = getFlagDefinition(flagName)

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setShowTooltip(!showTooltip)}
      >
        {children}
      </div>
      {showTooltip && (
        <div className="absolute z-50 mt-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg shadow-lg">
          <div className="text-sm font-semibold text-white mb-1">{flagName}</div>
          <div className="text-xs text-slate-300">{definition}</div>
        </div>
      )}
    </div>
  )
}
