'use client'

/**
 * FE-014: Responsive App Layout
 *
 * Main application layout that adapts to screen size:
 * - Desktop (>= 1024px): Side navbar
 * - Tablet (768-1023px): Collapsible navbar
 * - Mobile (< 768px): Bottom tabs
 */

import { ReactNode } from 'react'
import { Navbar } from './Navbar'
import { BottomTabs } from './BottomTabs'
import { OfflineBanner } from '@/components/ui/OfflineBanner'
import { cn } from '@/lib/utils'

// ============================================================================
// Types
// ============================================================================

interface AppLayoutProps {
  /** Page content */
  children: ReactNode
  /** Additional class names for the main content area */
  className?: string
  /** Whether to hide the navigation (for focus mode, etc.) */
  hideNav?: boolean
  /** Page title for header (mobile) */
  title?: string
}

// ============================================================================
// Component
// ============================================================================

export function AppLayout({
  children,
  className,
  hideNav = false,
  title,
}: AppLayoutProps) {
  if (hideNav) {
    return (
      <div className="min-h-screen bg-background">
        <OfflineBanner />
        <main className={cn('p-4 md:p-6', className)}>{children}</main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <OfflineBanner />

      {/* Desktop/Tablet: Side navbar */}
      <div className="hidden md:flex">
        <Navbar />
        <main className={cn('flex-1 p-6 overflow-auto', className)}>
          {children}
        </main>
      </div>

      {/* Mobile: Content + Bottom tabs */}
      <div className="md:hidden">
        {/* Mobile header (optional) */}
        {title && (
          <header className="sticky top-0 z-30 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
            <div className="px-4 h-14 flex items-center">
              <h1 className="text-lg font-medium">{title}</h1>
            </div>
          </header>
        )}

        {/* Main content with bottom padding for tabs */}
        <main className={cn('pb-20 p-4', className)}>{children}</main>

        {/* Bottom navigation */}
        <BottomTabs />
      </div>
    </div>
  )
}

// ============================================================================
// Split Layout (for planning page with inbox + today)
// ============================================================================

interface SplitLayoutProps {
  /** Left panel content */
  left: ReactNode
  /** Right panel content */
  right: ReactNode
  /** Left panel title (mobile) */
  leftTitle?: string
  /** Right panel title (mobile) */
  rightTitle?: string
  /** Currently active panel on mobile */
  activePanel?: 'left' | 'right'
  /** Callback when panel changes on mobile */
  onPanelChange?: (panel: 'left' | 'right') => void
}

export function SplitLayout({
  left,
  right,
  leftTitle = 'Inbox',
  rightTitle = 'Today',
  activePanel = 'left',
  onPanelChange,
}: SplitLayoutProps) {
  return (
    <>
      {/* Desktop: Side by side */}
      <div className="hidden md:grid md:grid-cols-2 gap-6 h-full">
        <div className="flex flex-col">
          <h2 className="text-lg font-medium mb-4">{leftTitle}</h2>
          <div className="flex-1 overflow-auto">{left}</div>
        </div>
        <div className="flex flex-col">
          <h2 className="text-lg font-medium mb-4">{rightTitle}</h2>
          <div className="flex-1 overflow-auto">{right}</div>
        </div>
      </div>

      {/* Mobile: Tabs to switch */}
      <div className="md:hidden">
        {/* Tab bar */}
        <div className="flex border-b mb-4">
          <button
            className={cn(
              'flex-1 py-3 text-sm font-medium border-b-2 transition-colors',
              activePanel === 'left'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground'
            )}
            onClick={() => onPanelChange?.('left')}
          >
            {leftTitle}
          </button>
          <button
            className={cn(
              'flex-1 py-3 text-sm font-medium border-b-2 transition-colors',
              activePanel === 'right'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground'
            )}
            onClick={() => onPanelChange?.('right')}
          >
            {rightTitle}
          </button>
        </div>

        {/* Active panel content */}
        {activePanel === 'left' ? left : right}
      </div>
    </>
  )
}

// ============================================================================
// Focus Layout (minimal chrome for focus mode)
// ============================================================================

interface FocusLayoutProps {
  children: ReactNode
  /** Exit focus mode callback */
  onExit?: () => void
}

export function FocusLayout({ children, onExit }: FocusLayoutProps) {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Minimal header with exit button */}
      <header className="p-4 flex justify-end">
        {onExit && (
          <button
            onClick={onExit}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Exit Focus
          </button>
        )}
      </header>

      {/* Centered content */}
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-lg">{children}</div>
      </main>
    </div>
  )
}

// ============================================================================
// Page Container (standard page wrapper)
// ============================================================================

interface PageContainerProps {
  children: ReactNode
  /** Page title */
  title?: string
  /** Optional action button */
  action?: ReactNode
  /** Maximum width constraint */
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  className?: string
}

export function PageContainer({
  children,
  title,
  action,
  maxWidth = 'lg',
  className,
}: PageContainerProps) {
  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-3xl',
    xl: 'max-w-5xl',
    full: 'max-w-full',
  }

  return (
    <div className={cn('mx-auto w-full', maxWidthClasses[maxWidth], className)}>
      {(title || action) && (
        <div className="flex items-center justify-between mb-6">
          {title && <h1 className="text-2xl font-semibold">{title}</h1>}
          {action}
        </div>
      )}
      {children}
    </div>
  )
}
