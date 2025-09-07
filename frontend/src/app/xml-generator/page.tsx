import { XMLGenerator } from '@/components/xml/XMLGenerator'

export default function XMLGeneratorPage() {
  return (
    <div className="h-screen">
      <XMLGenerator />
    </div>
  )
}

export const metadata = {
  title: 'XML Generator - Streamworks Self-Service',
  description: 'KI-gestützte Erstellung und Verwaltung von Streamworks XML-Konfigurationen',
}