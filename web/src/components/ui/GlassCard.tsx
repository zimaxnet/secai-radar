import { ReactNode, MouseEventHandler } from 'react'

interface GlassCardProps {
  children: ReactNode
  className?: string
  hoverEffect?: boolean
  onClick?: MouseEventHandler<HTMLDivElement>
}

export default function GlassCard({ children, className = '', hoverEffect = false, onClick }: GlassCardProps) {
  return (
    <div 
      onClick={onClick}
      className={`
        relative overflow-hidden rounded-xl border border-white/10 bg-slate-900/60 backdrop-blur-xl shadow-2xl
        ${hoverEffect ? 'hover:border-blue-500/30 hover:shadow-blue-500/10 hover:-translate-y-1 transition-all duration-300' : ''}
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
    >
      {/* Subtle gradient sheen */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
      
      {/* Content */}
      <div className="relative z-10 h-full">
        {children}
      </div>
    </div>
  )
}
