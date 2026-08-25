import React from 'react';
import './globals.css';

export const metadata = {
  title: 'MuleShield PRO — Enterprise Fraud Risk & Compliance Console',
  description: 'AI-Powered Money Mule Detection and Regulatory Compliance Operations Center.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        {/* FontAwesome 6 CDN */}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
        {/* Vis Network CDN for graph visualizations */}
        <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/standalone/umd/vis-network.min.js" defer></script>
      </head>
      <body className="antialiased min-h-screen bg-slate-50 font-sans text-slate-900">
        {children}
      </body>
    </html>
  );
}
