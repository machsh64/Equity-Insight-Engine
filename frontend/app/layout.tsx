import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Equity Insight Engine',
  description: '长期股票观测与潜力筛选系统',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  )
}

