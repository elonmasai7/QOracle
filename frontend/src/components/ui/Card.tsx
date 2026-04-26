import type { PropsWithChildren, ReactNode } from 'react'
import { cn } from '../../lib/cn'

interface CardProps {
  title?: string
  subtitle?: string
  action?: ReactNode
  className?: string
}

export function Card({ title, subtitle, action, className, children }: PropsWithChildren<CardProps>) {
  return (
    <section className={cn('surface-panel p-5', className)}>
      {(title || subtitle || action) && (
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            {title ? <h3 className="text-sm font-semibold text-white">{title}</h3> : null}
            {subtitle ? <p className="mt-1 text-sm text-slate-400">{subtitle}</p> : null}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  )
}
