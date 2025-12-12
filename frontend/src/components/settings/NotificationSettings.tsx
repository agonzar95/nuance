'use client'

/**
 * SUB-007: Notification Preferences
 *
 * Settings component for managing notification preferences.
 * Allows users to enable/disable notifications and choose channel.
 */

import { useState } from 'react'
import type { Profile, ProfileUpdate } from '@/hooks/useProfile'

interface NotificationSettingsProps {
  profile: Profile
  onUpdate: (updates: ProfileUpdate) => Promise<void>
}

export function NotificationSettings({
  profile,
  onUpdate,
}: NotificationSettingsProps) {
  const [isUpdating, setIsUpdating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleUpdate(updates: ProfileUpdate) {
    setIsUpdating(true)
    setError(null)

    try {
      await onUpdate(updates)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update settings')
    } finally {
      setIsUpdating(false)
    }
  }

  const hasEmail = true // Email is always available
  const hasTelegram = !!profile.telegram_chat_id

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">
          Notification Preferences
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Control how you receive reminders and updates.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Enable/Disable Toggle */}
      <div className="flex items-center justify-between">
        <div>
          <label
            htmlFor="notification_enabled"
            className="text-sm font-medium text-gray-900"
          >
            Enable notifications
          </label>
          <p className="text-sm text-gray-500">
            Receive morning plans and end-of-day summaries
          </p>
        </div>
        <button
          id="notification_enabled"
          type="button"
          role="switch"
          aria-checked={profile.notification_enabled}
          disabled={isUpdating}
          onClick={() =>
            handleUpdate({ notification_enabled: !profile.notification_enabled })
          }
          className={`
            relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
            ${profile.notification_enabled ? 'bg-blue-600' : 'bg-gray-200'}
            ${isUpdating ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <span
            aria-hidden="true"
            className={`
              pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out
              ${profile.notification_enabled ? 'translate-x-5' : 'translate-x-0'}
            `}
          />
        </button>
      </div>

      {/* Channel Selection */}
      <fieldset disabled={!profile.notification_enabled || isUpdating}>
        <legend className="text-sm font-medium text-gray-900">
          Notification channel
        </legend>
        <p className="text-sm text-gray-500 mb-3">
          Choose where to receive notifications
        </p>

        <div className="space-y-3">
          {/* Email Option */}
          <label
            className={`
              flex items-center p-4 border rounded-lg cursor-pointer transition-colors
              ${profile.notification_channel === 'email' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}
              ${!profile.notification_enabled ? 'opacity-50' : ''}
            `}
          >
            <input
              type="radio"
              name="notification_channel"
              value="email"
              checked={profile.notification_channel === 'email'}
              onChange={() => handleUpdate({ notification_channel: 'email' })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500"
            />
            <div className="ml-3">
              <span className="block text-sm font-medium text-gray-900">
                Email only
              </span>
              <span className="block text-sm text-gray-500">
                Receive notifications via email
              </span>
            </div>
          </label>

          {/* Telegram Option */}
          <label
            className={`
              flex items-center p-4 border rounded-lg cursor-pointer transition-colors
              ${profile.notification_channel === 'telegram' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}
              ${!profile.notification_enabled || !hasTelegram ? 'opacity-50' : ''}
            `}
          >
            <input
              type="radio"
              name="notification_channel"
              value="telegram"
              checked={profile.notification_channel === 'telegram'}
              onChange={() => handleUpdate({ notification_channel: 'telegram' })}
              disabled={!hasTelegram}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500"
            />
            <div className="ml-3">
              <span className="block text-sm font-medium text-gray-900">
                Telegram only
              </span>
              <span className="block text-sm text-gray-500">
                {hasTelegram
                  ? 'Receive notifications via Telegram'
                  : 'Connect Telegram to enable this option'}
              </span>
            </div>
          </label>

          {/* Both Option */}
          <label
            className={`
              flex items-center p-4 border rounded-lg cursor-pointer transition-colors
              ${profile.notification_channel === 'both' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}
              ${!profile.notification_enabled || !hasTelegram ? 'opacity-50' : ''}
            `}
          >
            <input
              type="radio"
              name="notification_channel"
              value="both"
              checked={profile.notification_channel === 'both'}
              onChange={() => handleUpdate({ notification_channel: 'both' })}
              disabled={!hasTelegram}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500"
            />
            <div className="ml-3">
              <span className="block text-sm font-medium text-gray-900">
                Both channels
              </span>
              <span className="block text-sm text-gray-500">
                {hasTelegram
                  ? 'Receive notifications via email and Telegram'
                  : 'Connect Telegram to enable this option'}
              </span>
            </div>
          </label>
        </div>
      </fieldset>
    </div>
  )
}
