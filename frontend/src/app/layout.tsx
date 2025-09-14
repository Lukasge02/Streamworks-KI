import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { AppLayout } from '@/components/layout/AppLayout'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'Streamworks RAG MVP',
    template: '%s | Streamworks RAG MVP'
  },
  description: 'Professional RAG System mit Docling Layout-Aware Parsing',
  keywords: ['RAG', 'Streamworks', 'Arvato Systems', 'Document Processing', 'AI'],
  authors: [{ name: 'Arvato Systems' }],
  creator: 'Arvato Systems',
  metadataBase: new URL(process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3000'),
  openGraph: {
    title: 'Streamworks RAG MVP',
    description: 'Professional RAG System mit Docling Layout-Aware Parsing',
    url: '/',
    siteName: 'Streamworks RAG MVP',
    locale: 'de_DE',
    type: 'website',
  },
  robots: {
    index: false,
    follow: false,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="de" className={`${inter.variable} h-full`} data-scroll-behavior="smooth" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="min-h-full bg-gray-50 dark:bg-gray-900" suppressHydrationWarning={true}>
        <Providers>
          <AppLayout>
            {children}
          </AppLayout>
        </Providers>
      </body>
    </html>
  )
}