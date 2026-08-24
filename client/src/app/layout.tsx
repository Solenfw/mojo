import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Mojo',
  description: 'AI-powered Japanese language learning',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans">
        {children}
      </body>
    </html>
  )
}