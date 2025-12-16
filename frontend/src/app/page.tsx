import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center max-w-lg">
        <h1 className="text-4xl font-bold text-foreground mb-4">
          Nuance
        </h1>
        <p className="text-xl text-gray-600 mb-4">
          Executive Function Prosthetic
        </p>
        <p className="text-gray-500 mb-8">
          AI-powered productivity for neurodivergent minds.
          Capture thoughts, plan effectively, execute with support.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/login"
            className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Sign in
          </Link>
          <Link
            href="/signup"
            className="px-6 py-3 bg-white text-gray-700 font-medium rounded-lg border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Create account
          </Link>
        </div>
      </div>
    </main>
  )
}
