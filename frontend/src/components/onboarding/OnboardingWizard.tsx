'use client'

/**
 * INF-009: Onboarding Flow
 *
 * Multi-step onboarding wizard for new users.
 * Steps:
 * 1. Welcome - Brief intro to Nuance
 * 2. Timezone - Confirm/set user timezone
 * 3. Telegram - Instructions for linking Telegram (optional)
 * 4. Tutorial - Quick overview of the workflow
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { detectTimezone, COMMON_TIMEZONES, type ProfileUpdate } from '@/hooks/useProfile'
import { cn } from '@/lib/utils'

// ============================================================================
// Types
// ============================================================================

type OnboardingStep = 'welcome' | 'timezone' | 'telegram' | 'tutorial'

interface OnboardingWizardProps {
  /** Initial timezone from profile or browser detection */
  initialTimezone?: string
  /** Callback to update profile */
  onUpdateProfile: (updates: ProfileUpdate) => Promise<void>
  /** Callback when onboarding completes */
  onComplete: () => void
}

// ============================================================================
// Step Components
// ============================================================================

function WelcomeStep({ onNext }: { onNext: () => void }) {
  return (
    <div className="text-center space-y-6">
      <div className="text-6xl mb-4">&#x1F9E0;</div>
      <h1 className="text-3xl font-bold text-gray-900">Welcome to Nuance</h1>
      <p className="text-lg text-gray-600 max-w-md mx-auto">
        Your executive function prosthetic. We help you capture, plan, and execute
        without the shame and overwhelm of traditional productivity tools.
      </p>
      <div className="space-y-3 text-left max-w-sm mx-auto">
        <div className="flex items-start gap-3">
          <span className="text-xl">&#x1F4AD;</span>
          <div>
            <p className="font-medium text-gray-900">Capture freely</p>
            <p className="text-sm text-gray-500">Voice or text, we extract the structure</p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <span className="text-xl">&#x1F4CB;</span>
          <div>
            <p className="font-medium text-gray-900">Plan without pressure</p>
            <p className="text-sm text-gray-500">AI suggests what matters today</p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <span className="text-xl">&#x1F3AF;</span>
          <div>
            <p className="font-medium text-gray-900">Execute with support</p>
            <p className="text-sm text-gray-500">Coaching when you&apos;re stuck, celebration when you finish</p>
          </div>
        </div>
      </div>
      <button
        onClick={onNext}
        className="mt-4 px-8 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
      >
        Get Started
      </button>
    </div>
  )
}

function TimezoneStep({
  timezone,
  onTimezoneChange,
  onNext,
  onBack,
}: {
  timezone: string
  onTimezoneChange: (tz: string) => void
  onNext: () => void
  onBack: () => void
}) {
  const detectedTimezone = detectTimezone()
  const [showAll, setShowAll] = useState(false)

  // All IANA timezones for full selection
  const allTimezones = Intl.supportedValuesOf
    ? Intl.supportedValuesOf('timeZone')
    : COMMON_TIMEZONES

  const displayedTimezones = showAll ? allTimezones : COMMON_TIMEZONES

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="text-5xl mb-4">&#x1F30D;</div>
        <h2 className="text-2xl font-bold text-gray-900">Set Your Timezone</h2>
        <p className="text-gray-600 mt-2">
          We&apos;ll use this to send notifications at the right time.
        </p>
      </div>

      {detectedTimezone && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <span className="font-medium">Detected:</span> {detectedTimezone}
          </p>
          {timezone !== detectedTimezone && (
            <button
              onClick={() => onTimezoneChange(detectedTimezone)}
              className="text-sm text-blue-600 hover:text-blue-800 mt-1"
            >
              Use detected timezone
            </button>
          )}
        </div>
      )}

      <div>
        <label
          htmlFor="timezone"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Your timezone
        </label>
        <select
          id="timezone"
          value={timezone}
          onChange={(e) => onTimezoneChange(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {displayedTimezones.map((tz) => (
            <option key={tz} value={tz}>
              {tz.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
        {!showAll && (
          <button
            onClick={() => setShowAll(true)}
            className="text-sm text-blue-600 hover:text-blue-800 mt-2"
          >
            Show all timezones
          </button>
        )}
      </div>

      <div className="flex gap-3">
        <button
          onClick={onBack}
          className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
        <button
          onClick={onNext}
          className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Continue
        </button>
      </div>
    </div>
  )
}

function TelegramStep({
  onNext,
  onBack,
  onSkip,
}: {
  onNext: () => void
  onBack: () => void
  onSkip: () => void
}) {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="text-5xl mb-4">&#x1F4F1;</div>
        <h2 className="text-2xl font-bold text-gray-900">Connect Telegram</h2>
        <p className="text-gray-600 mt-2">
          Get notifications and capture tasks on the go. (Optional)
        </p>
      </div>

      <div className="bg-gray-50 rounded-lg p-6 space-y-4">
        <h3 className="font-medium text-gray-900">How to connect:</h3>
        <ol className="space-y-3 text-gray-700">
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
              1
            </span>
            <span>Open Telegram and search for <strong>@NuanceBot</strong></span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
              2
            </span>
            <span>Send <code className="bg-gray-200 px-1 rounded">/start</code> to the bot</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
              3
            </span>
            <span>The bot will give you a code - enter it in Settings later</span>
          </li>
        </ol>
      </div>

      <p className="text-sm text-gray-500 text-center">
        You can always connect Telegram later in Settings.
      </p>

      <div className="flex gap-3">
        <button
          onClick={onBack}
          className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
        <button
          onClick={onSkip}
          className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
        >
          Skip for now
        </button>
        <button
          onClick={onNext}
          className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          I&apos;ve connected
        </button>
      </div>
    </div>
  )
}

function TutorialStep({
  onComplete,
  onBack,
}: {
  onComplete: () => void
  onBack: () => void
}) {
  const [currentSlide, setCurrentSlide] = useState(0)

  const slides = [
    {
      icon: '&#x1F4AD;',
      title: 'Capture',
      description:
        'Dump your thoughts without organizing. Use voice or text - we\'ll extract the tasks automatically.',
    },
    {
      icon: '&#x1F4CB;',
      title: 'Plan',
      description:
        'Each morning, choose what to tackle. We suggest tasks based on importance, not due dates.',
    },
    {
      icon: '&#x1F3AF;',
      title: 'Execute',
      description:
        'Focus on one task at a time. Get support when stuck, celebration when you finish.',
    },
    {
      icon: '&#x1F319;',
      title: 'Reflect',
      description:
        'End your day by reviewing wins and deciding what rolls to tomorrow. No shame, just progress.',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">How Nuance Works</h2>
        <p className="text-gray-600 mt-2">
          A simple daily workflow for your brain.
        </p>
      </div>

      {/* Slide content */}
      <div className="bg-gray-50 rounded-lg p-8 text-center min-h-[200px] flex flex-col items-center justify-center">
        <div
          className="text-5xl mb-4"
          dangerouslySetInnerHTML={{ __html: slides[currentSlide].icon }}
        />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {slides[currentSlide].title}
        </h3>
        <p className="text-gray-600 max-w-sm">
          {slides[currentSlide].description}
        </p>
      </div>

      {/* Slide indicators */}
      <div className="flex justify-center gap-2">
        {slides.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={cn(
              'w-2 h-2 rounded-full transition-colors',
              index === currentSlide ? 'bg-blue-600' : 'bg-gray-300'
            )}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>

      {/* Navigation */}
      <div className="flex gap-3">
        {currentSlide === 0 ? (
          <button
            onClick={onBack}
            className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            Back
          </button>
        ) : (
          <button
            onClick={() => setCurrentSlide((c) => c - 1)}
            className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            Previous
          </button>
        )}

        {currentSlide < slides.length - 1 ? (
          <button
            onClick={() => setCurrentSlide((c) => c + 1)}
            className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Next
          </button>
        ) : (
          <button
            onClick={onComplete}
            className="flex-1 px-4 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            Start Using Nuance
          </button>
        )}
      </div>
    </div>
  )
}

// ============================================================================
// Main Component
// ============================================================================

export function OnboardingWizard({
  initialTimezone,
  onUpdateProfile,
  onComplete,
}: OnboardingWizardProps) {
  const router = useRouter()
  const [step, setStep] = useState<OnboardingStep>('welcome')
  const [timezone, setTimezone] = useState(initialTimezone || detectTimezone())
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Update timezone from initial if it changes
  useEffect(() => {
    if (initialTimezone) {
      setTimezone(initialTimezone)
    }
  }, [initialTimezone])

  const steps: OnboardingStep[] = ['welcome', 'timezone', 'telegram', 'tutorial']
  const currentIndex = steps.indexOf(step)

  async function handleComplete() {
    setIsSubmitting(true)
    setError(null)

    try {
      await onUpdateProfile({
        timezone,
        onboarding_completed: true,
      })
      onComplete()
      router.push('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete onboarding')
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            {steps.map((s, index) => (
              <div
                key={s}
                className={cn(
                  'flex-1 h-1 mx-1 rounded-full transition-colors',
                  index <= currentIndex ? 'bg-blue-600' : 'bg-gray-200'
                )}
              />
            ))}
          </div>
          <p className="text-center text-sm text-gray-500">
            Step {currentIndex + 1} of {steps.length}
          </p>
        </div>

        {/* Error display */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Step content */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          {step === 'welcome' && (
            <WelcomeStep onNext={() => setStep('timezone')} />
          )}

          {step === 'timezone' && (
            <TimezoneStep
              timezone={timezone}
              onTimezoneChange={setTimezone}
              onNext={() => setStep('telegram')}
              onBack={() => setStep('welcome')}
            />
          )}

          {step === 'telegram' && (
            <TelegramStep
              onNext={() => setStep('tutorial')}
              onBack={() => setStep('timezone')}
              onSkip={() => setStep('tutorial')}
            />
          )}

          {step === 'tutorial' && (
            <TutorialStep
              onComplete={handleComplete}
              onBack={() => setStep('telegram')}
            />
          )}

          {/* Loading overlay */}
          {isSubmitting && (
            <div className="absolute inset-0 bg-white/80 flex items-center justify-center rounded-xl">
              <div className="text-center">
                <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-2" />
                <p className="text-gray-600">Setting up your account...</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
