'use client'

/**
 * TG-0015: Telegram Connection Page
 *
 * Handles the connection link from Telegram bot.
 * URL: /settings/telegram?token=<token>
 *
 * Flow:
 * 1. Extract token from URL params
 * 2. If no token, redirect to /dashboard/settings
 * 3. Show loading state while connecting
 * 4. Call POST /api/telegram/connect with token
 * 5. On success: Show success message, redirect to settings after 2s
 * 6. On error: Show error message with guidance to retry
 */

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useRequireAuth } from '@/hooks/useSession'
import { api } from '@/lib/api'
import { ApiError } from '@/types/api'
import { Spinner } from '@/components/ui/Loading'

type ConnectionState = 'loading' | 'connecting' | 'success' | 'error'

export default function TelegramConnectPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { isLoading: authLoading } = useRequireAuth()

  const [state, setState] = useState<ConnectionState>('loading')
  const [errorMessage, setErrorMessage] = useState<string>('')

  const token = searchParams.get('token')

  useEffect(() => {
    // Wait for auth to load
    if (authLoading) return

    // No token - redirect to settings
    if (!token) {
      router.replace('/dashboard/settings')
      return
    }

    // Start connection process
    async function connectTelegram() {
      setState('connecting')

      try {
        await api.telegram.connect(token!)
        setState('success')

        // Redirect to settings after 2 seconds
        setTimeout(() => {
          router.replace('/dashboard/settings')
        }, 2000)
      } catch (err) {
        setState('error')

        if (err instanceof ApiError) {
          if (err.status === 400) {
            // Token invalid or expired
            const message = err.data?.error || 'Invalid or expired token'
            if (message.toLowerCase().includes('expired')) {
              setErrorMessage('This connection link has expired. Please send /start to the Telegram bot again to get a new link.')
            } else {
              setErrorMessage('This connection link is invalid. Please send /start to the Telegram bot to get a new link.')
            }
          } else if (err.status === 401) {
            setErrorMessage('You need to be logged in to connect Telegram.')
          } else {
            setErrorMessage('Something went wrong. Please try again.')
          }
        } else {
          setErrorMessage('Could not connect to the server. Please check your internet connection and try again.')
        }
      }
    }

    connectTelegram()
  }, [token, authLoading, router])

  // Auth loading
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full">
        {/* Loading / Connecting State */}
        {(state === 'loading' || state === 'connecting') && (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
            <div className="flex justify-center mb-4">
              <Spinner size="lg" />
            </div>
            <h1 className="text-xl font-semibold text-gray-900 mb-2">
              Connecting Telegram
            </h1>
            <p className="text-gray-600">
              Please wait while we link your Telegram account...
            </p>
          </div>
        )}

        {/* Success State */}
        {state === 'success' && (
          <div className="bg-white rounded-xl border border-green-200 p-8 text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
            </div>
            <h1 className="text-xl font-semibold text-green-900 mb-2">
              Telegram Connected!
            </h1>
            <p className="text-gray-600 mb-4">
              Your Telegram account has been successfully linked. You can now capture tasks and receive notifications via Telegram.
            </p>
            <p className="text-sm text-gray-500">
              Redirecting to settings...
            </p>
          </div>
        )}

        {/* Error State */}
        {state === 'error' && (
          <div className="bg-white rounded-xl border border-red-200 p-8 text-center">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
            </div>
            <h1 className="text-xl font-semibold text-red-900 mb-2">
              Connection Failed
            </h1>
            <p className="text-gray-600 mb-6">
              {errorMessage}
            </p>
            <div className="space-y-3">
              <button
                onClick={() => router.push('/dashboard/settings')}
                className="w-full px-4 py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors"
              >
                Go to Settings
              </button>
              <p className="text-sm text-gray-500">
                Open Telegram and send <code className="bg-gray-100 px-1 rounded">/start</code> to @NuanceBot to get a new connection link.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
