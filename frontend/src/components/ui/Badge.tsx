import type { PropsWithChildren } from 'react'
import { cn } from '../../lib/cn'

interface BadgeProps {
  tone?: 'default' | 'success' | 'warning' | 'danger'
}

const toneStyles = {
  default: 'bg-white/5 text-slate-300 border-white/10',
  success: 'bg-green-500/10 text-green-300 border-green-500/20',
  warning: 'bg-amber-500/10 text-amber-300 border-amber-500/20',
  danger: 'bg-red-500/10 text-red-300 border-red-500/20',
}

export function Badge({ children, tone = 'default' }: PropsWithChildren<BadgeProps>) {
  return (
    <span className={cn('inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium', toneStyles[tone])}>
      {children}
    </span>
  )
}
