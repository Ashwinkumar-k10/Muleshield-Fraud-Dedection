import React from 'react';
import './globals.css';

export const metadata = {
  title: 'LoomProof Origin — Digital Trust Passport for Authentic Handlooms',
  description: 'Every thread has proof. Establish absolute trust through cryptographic weaver registration, three-checkpoint weave continuity analysis, OpenCV FabricPrint matching, and AI-summarized heritage storytelling.',
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
      </head>
      <body className="antialiased min-h-screen bg-cream-50 font-sans text-indigo-900 selection:bg-gold-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
