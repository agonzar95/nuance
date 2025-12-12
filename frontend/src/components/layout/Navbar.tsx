'use client'

/**
 * FE-015: Desktop Navbar Component
 *
 * Side navigation for desktop/tablet screens.
 * Shows navigation icons with labels and quick add button.
 */

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  MessageSquare,
  Calendar,
  Target,
  BarChart3,
  Plus,
  type LucideIcon,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavItem {
  href: string
  label: string
  icon: LucideIcon
}

const navItems: NavItem[] = [
  { href: '/capture', label: 'Capture', icon: MessageSquare },
  { href: '/plan', label: 'Plan', icon: Calendar },
  { href: '/focus', label: 'Focus', icon: Target },
  { href: '/reflect', label: 'Reflect', icon: BarChart3 },
]

export function Navbar() {
  const pathname = usePathname()

  return (
    <nav className="w-20 border-r border-border bg-background flex flex-col items-center py-4 gap-2">
      {/* Logo/Brand */}
      <div className="mb-4">
        <Link
          href="/"
          className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold text-lg"
        >
          N
        </Link>
      </div>

      {/* Navigation Items */}
      {navItems.map((item) => {
        const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
        const Icon = item.icon

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex flex-col items-center justify-center w-16 h-16 rounded-lg',
              'hover:bg-muted transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
              isActive && 'bg-muted text-primary'
            )}
            aria-current={isActive ? 'page' : undefined}
          >
            <Icon className="w-6 h-6" aria-hidden="true" />
            <span className="text-xs mt-1">{item.label}</span>
          </Link>
        )
      })}

      {/* Spacer */}
      <div className="flex-1" />

      {/* Quick Add Button */}
      <QuickAddButton />
    </nav>
  )
}

/**
 * Quick Add Button
 *
 * Floating action button for quickly capturing thoughts.
 */
export function QuickAddButton({ variant = 'desktop' }: { variant?: 'desktop' | 'mobile' }) {
  // TODO: This will open a quick capture overlay (CAP-008)
  const handleClick = () => {
    // Placeholder - will navigate to capture or open overlay
    window.location.href = '/capture'
  }

  if (variant === 'mobile') {
    return (
      <button
        onClick={handleClick}
        className={cn(
          'flex items-center justify-center w-12 h-12',
          'bg-primary text-primary-foreground rounded-full',
          'shadow-lg hover:shadow-xl transition-shadow',
          'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2'
        )}
        aria-label="Quick capture"
      >
        <Plus className="w-6 h-6" aria-hidden="true" />
      </button>
    )
  }

  return (
    <button
      onClick={handleClick}
      className={cn(
        'flex flex-col items-center justify-center w-14 h-14',
        'bg-primary text-primary-foreground rounded-xl',
        'hover:bg-primary/90 transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2'
      )}
      aria-label="Quick capture"
    >
      <Plus className="w-6 h-6" aria-hidden="true" />
    </button>
  )
}
