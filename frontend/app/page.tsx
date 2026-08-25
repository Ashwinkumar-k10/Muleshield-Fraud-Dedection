"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function RootIndexPage() {
  const router = useRouter();

  useEffect(() => {
    // Check if already authenticated, otherwise redirect to login
    const auth = sessionStorage.getItem("muleshield_authenticated");
    if (auth === "true") {
      router.push('/dashboard');
    } else {
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center text-slate-400 font-mono text-xs">
      <span>Initializing secure session tunnel...</span>
    </div>
  );
}
