/**
 * Tier Badge Component
 * Displays Trust Score tier with appropriate styling
 */

import { getTierBadge } from '../../utils/copy'

interface TierBadgeProps {
  tier: 'A' | 'B' | 'C' | 'D'
  size?: 'sm' | 'md' | 'lg'
  showDescription?: boolean
}

export default function TierBadge({ tier, size = 'md', showDescription = false }: TierBadgeProps) {
  const badge = getTierBadge(tier)
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  }

  const colorClasses = {
    A: 'bg-green-500/20 text-green-400 border-green-500/30',
    B: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    C: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    D: 'bg-red-500/20 text-red-400 border-red-500/30',
  }

  return (
    <div className="inline-flex items-center gap-2">
      <span className={`${sizeClasses[size]} rounded-lg font-semibold border ${colorClasses[tier]}`}>
        Tier {tier}
      </span>
      {showDescription && (
        <span className="text-sm text-slate-400">{badge.description}</span>
      )}
    </div>
  )
}
