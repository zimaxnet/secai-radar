import { ReactNode } from 'react'

interface PageHeaderProps {
  title: string
  subtitle?: string
  parentLink?: { to: string; label: string }
  action?: ReactNode
}

export default function PageHeader({ title, subtitle, parentLink, action }: PageHeaderProps) {
  return (
    <div className="mb-8 relative">
      {/* Background Glow */}
      <div className="absolute -top-20 -left-20 w-64 h-64 bg-blue-600/20 rounded-full blur-[100px] pointer-events-none" />
      
      <div className="relative z-10 flex items-end justify-between">
        <div>
          {parentLink && (
            <a 
              href={parentLink.to} 
              className="text-xs font-medium text-blue-400 hover:text-blue-300 uppercase tracking-wider mb-2 block"
            >
              ← {parentLink.label}
            </a>
          )}
          <h1 className="text-4xl font-bold text-white tracking-tight mb-2">
            {title}
          </h1>
          {subtitle && (
            <p className="text-lg text-slate-400 max-w-2xl">
              {subtitle}
            </p>
          )}
        </div>
        {action && (
          <div className="mb-1">
            {action}
          </div>
        )}
      </div>
    </div>
  )
}

