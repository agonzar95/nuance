'use client'

/**
 * INF-010: Settings Page
 *
 * User settings page for managing:
 * - Profile settings (timezone)
 * - Notification preferences (channel, enabled)
 * - Telegram connection status
 */

import { useState } from 'react'
import Link from 'next/link'
import { useProfile, COMMON_TIMEZONES, detectTimezone } from '@/hooks/useProfile'
import { useSession } from '@/hooks/useSession'
import { NotificationSettings } from '@/components/settings/NotificationSettings'
import { Spinner } from '@/components/ui/Loading'
import { api } from '@/lib/api'

export default function SettingsPage() {
  const { user } = useSession()
  const { profile, isLoading, error, updateProfile, refetch } = useProfile()
  const [timezoneUpdating, setTimezoneUpdating] = useState(false)
  const [timezoneError, setTimezoneError] = useState<string | null>(null)
  const [showAllTimezones, setShowAllTimezones] = useState(false)

  // Telegram disconnect state
  const [showDisconnectConfirm, setShowDisconnectConfirm] = useState(false)
  const [disconnecting, setDisconnecting] = useState(false)
  const [disconnectError, setDisconnectError] = useState<string | null>(null)

  async function handleDisconnectTelegram() {
    setDisconnecting(true)
    setDisconnectError(null)

    try {
      await api.telegram.disconnect()
      // Refetch profile to update UI
      await refetch()
      setShowDisconnectConfirm(false)
    } catch (err) {
      setDisconnectError(err instanceof Error ? err.message : 'Failed to disconnect Telegram')
    } finally {
      setDisconnecting(false)
    }
  }

  // All IANA timezones for full selection
  const allTimezones = typeof Intl !== 'undefined' && Intl.supportedValuesOf
    ? Intl.supportedValuesOf('timeZone')
    : COMMON_TIMEZONES

  const displayedTimezones = showAllTimezones ? allTimezones : COMMON_TIMEZONES

  async function handleTimezoneChange(newTimezone: string) {
    setTimezoneUpdating(true)
    setTimezoneError(null)

    try {
      await updateProfile({ timezone: newTimezone })
    } catch (err) {
      setTimezoneError(err instanceof Error ? err.message : 'Failed to update timezone')
    } finally {
      setTimezoneUpdating(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Failed to load settings</p>
          <Link
            href="/dashboard"
            className="text-blue-600 hover:text-blue-800"
          >
            Return to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  if (!profile) {
    return null
  }

  const detectedTimezone = detectTimezone()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link
            href="/dashboard"
            className="text-gray-500 hover:text-gray-700"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </Link>
          <h1 className="text-xl font-semibold text-gray-900">Settings</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4 py-8 space-y-8">
        {/* Account Section */}
        <section className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Account</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <p className="mt-1 text-gray-900">{user?.email}</p>
            </div>
          </div>
        </section>

        {/* Timezone Section */}
        <section className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">Timezone</h2>
          <p className="text-sm text-gray-500 mb-4">
            Used for scheduling notifications and daily transitions.
          </p>

          {timezoneError && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {timezoneError}
            </div>
          )}

          {detectedTimezone && detectedTimezone !== profile.timezone && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <span className="font-medium">Detected:</span> {detectedTimezone}
              </p>
              <button
                onClick={() => handleTimezoneChange(detectedTimezone)}
                disabled={timezoneUpdating}
                className="text-sm text-blue-600 hover:text-blue-800 mt-1 disabled:opacity-50"
              >
                Use detected timezone
              </button>
            </div>
          )}

          <div className="relative">
            <select
              value={profile.timezone}
              onChange={(e) => handleTimezoneChange(e.target.value)}
              disabled={timezoneUpdating}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:bg-gray-100"
            >
              {displayedTimezones.map((tz) => (
                <option key={tz} value={tz}>
                  {tz.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
            {timezoneUpdating && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <Spinner size="sm" />
              </div>
            )}
          </div>

          {!showAllTimezones && (
            <button
              onClick={() => setShowAllTimezones(true)}
              className="text-sm text-blue-600 hover:text-blue-800 mt-2"
            >
              Show all timezones
            </button>
          )}
        </section>

        {/* Telegram Connection Section */}
        <section className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">
            Telegram Connection
          </h2>
          <p className="text-sm text-gray-500 mb-4">
            Connect Telegram to capture tasks and receive notifications on the go.
          </p>

          {disconnectError && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {disconnectError}
            </div>
          )}

          {profile.telegram_chat_id ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-green-600"
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
                <div className="flex-1">
                  <p className="font-medium text-green-900">Connected</p>
                  <p className="text-sm text-green-700">
                    You can send messages to the Nuance bot to capture tasks.
                  </p>
                </div>
              </div>

              {/* Disconnect Confirmation Dialog */}
              {showDisconnectConfirm ? (
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                  <p className="font-medium text-amber-900 mb-2">
                    Disconnect Telegram?
                  </p>
                  <p className="text-sm text-amber-800 mb-4">
                    You won&apos;t be able to capture tasks or receive notifications via Telegram until you reconnect.
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={handleDisconnectTelegram}
                      disabled={disconnecting}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {disconnecting && <Spinner size="sm" />}
                      {disconnecting ? 'Disconnecting...' : 'Yes, Disconnect'}
                    </button>
                    <button
                      onClick={() => setShowDisconnectConfirm(false)}
                      disabled={disconnecting}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors disabled:opacity-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setShowDisconnectConfirm(true)}
                  className="text-sm text-red-600 hover:text-red-800 font-medium"
                >
                  Disconnect Telegram
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                <p className="font-medium text-gray-900 mb-2">
                  How to connect:
                </p>
                <ol className="space-y-2 text-sm text-gray-700">
                  <li className="flex gap-2">
                    <span className="font-medium text-gray-900">1.</span>
                    <span>
                      Open Telegram and search for{' '}
                      <strong>@NuanceBot</strong>
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-medium text-gray-900">2.</span>
                    <span>
                      Send{' '}
                      <code className="bg-gray-200 px-1 rounded">/start</code>{' '}
                      to the bot
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-medium text-gray-900">3.</span>
                    <span>
                      Follow the bot&apos;s instructions to link your account
                    </span>
                  </li>
                </ol>
              </div>
            </div>
          )}
        </section>

        {/* Notification Settings Section */}
        <section className="bg-white rounded-xl border border-gray-200 p-6">
          <NotificationSettings profile={profile} onUpdate={updateProfile} />
        </section>

        {/* Danger Zone */}
        <section className="bg-white rounded-xl border border-red-200 p-6">
          <h2 className="text-lg font-semibold text-red-900 mb-1">
            Danger Zone
          </h2>
          <p className="text-sm text-gray-500 mb-4">
            Irreversible actions. Be careful.
          </p>

          <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
            <div>
              <p className="font-medium text-red-900">Delete Account</p>
              <p className="text-sm text-red-700">
                Permanently delete your account and all data.
              </p>
            </div>
            <button
              className="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
              onClick={() => {
                // TODO: Implement account deletion
                alert('Account deletion is not yet implemented.')
              }}
            >
              Delete
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}
