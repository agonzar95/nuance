'use client'

/**
 * FE-015: Mobile Bottom Tabs Component
 *
 * Bottom navigation for mobile screens.
 * Shows navigation icons with a floating quick add button.
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

export function BottomTabs() {
  const pathname = usePathname()

  return (
    <nav className="fixed bottom-0 left-0 right-0 border-t border-border bg-background safe-area-inset-bottom z-40">
      <div className="flex justify-around items-center h-16 px-2 relative">
        {/* Left nav items */}
        {navItems.slice(0, 2).map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
          const Icon = item.icon

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex flex-col items-center justify-center flex-1 h-full',
                'hover:text-primary transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-inset',
                isActive ? 'text-primary' : 'text-muted-foreground'
              )}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon className="w-6 h-6" aria-hidden="true" />
              <span className="text-xs mt-1">{item.label}</span>
            </Link>
          )
        })}

        {/* Center: Quick Add Button */}
        <div className="flex-1 flex items-center justify-center">
          <QuickAddFab />
        </div>

        {/* Right nav items */}
        {navItems.slice(2).map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
          const Icon = item.icon

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex flex-col items-center justify-center flex-1 h-full',
                'hover:text-primary transition-colors',
                'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-inset',
                isActive ? 'text-primary' : 'text-muted-foreground'
              )}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon className="w-6 h-6" aria-hidden="true" />
              <span className="text-xs mt-1">{item.label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}

/**
 * Floating Action Button for Quick Add
 */
function QuickAddFab() {
  const handleClick = () => {
    // TODO: This will open a quick capture overlay (CAP-008)
    window.location.href = '/capture'
  }

  return (
    <button
      onClick={handleClick}
      className={cn(
        'absolute -top-6',
        'flex items-center justify-center w-14 h-14',
        'bg-primary text-primary-foreground rounded-full',
        'shadow-lg hover:shadow-xl transition-shadow',
        'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2'
      )}
      aria-label="Quick capture"
    >
      <Plus className="w-7 h-7" aria-hidden="true" />
    </button>
  )
}
