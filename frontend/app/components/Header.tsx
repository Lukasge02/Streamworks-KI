'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';
import { cn } from '@/app/utils/cn';

interface HeaderProps {
  sessionId?: string | null;
}

export default function Header({ sessionId }: HeaderProps) {
  const [backendStatus, setBackendStatus] = useState<{ online: boolean; aiConfigured: boolean; model: string | null }>({
    online: false,
    aiConfigured: false,
    model: null
  });

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/chat/health", {
          method: "GET",
          signal: AbortSignal.timeout(3000)
        });
        if (response.ok) {
          const data = await response.json();
          setBackendStatus({
            online: true,
            aiConfigured: data.openai_configured || false,
            model: data.model || null
          });
        } else {
          setBackendStatus({ online: false, aiConfigured: false, model: null });
        }
      } catch {
        setBackendStatus({ online: false, aiConfigured: false, model: null });
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="relative bg-gradient-to-r from-[#0082D9] via-[#0077C8] to-[#006BB3] border-b border-white/10">
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,transparent,rgba(255,255,255,0.05),transparent)]" />

      {/* Main header content */}
      <div className="relative flex items-center justify-between h-[72px] px-6 max-w-[1600px] mx-auto">
        {/* Left: Logo & Title */}
        <Link href="/" className="flex items-center gap-3 group">
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-11 h-11 bg-white rounded-xl flex items-center justify-center shadow-lg shadow-black/10"
          >
            <Zap className="w-6 h-6 text-[#0082D9]" />
          </motion.div>
          <div className="flex flex-col">
            <span className="font-extrabold text-white text-lg tracking-tight leading-none">
              STREAMWORKS
            </span>
            <span className="text-[11px] text-white/70 font-semibold tracking-[0.2em] uppercase">
              Self Service
            </span>
          </div>
        </Link>

        {/* Center: Removed - Navigation is now in Sidebar */}
        <div className="flex-1" />

        {/* Right: Status Indicator */}
        <div className="flex items-center">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className={cn(
              "flex items-center gap-2.5 px-4 py-2 rounded-full text-sm font-semibold",
              "backdrop-blur-sm border transition-all duration-300",
              backendStatus.online
                ? "bg-emerald-500/20 border-emerald-400/30 text-white"
                : "bg-red-500/20 border-red-400/30 text-white"
            )}
          >
            <span className="relative flex h-2.5 w-2.5">
              <span className={cn(
                "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75",
                backendStatus.online ? "bg-emerald-400" : "bg-red-400"
              )} />
              <span className={cn(
                "relative inline-flex rounded-full h-2.5 w-2.5",
                backendStatus.online ? "bg-emerald-400" : "bg-red-400"
              )} />
            </span>
            <span>{backendStatus.online ? 'Backend Online' : 'Backend Offline'}</span>
          </motion.div>
        </div>
      </div>

      {/* Bottom border beam effect */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />
    </header>
  );
}
