"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import { Zap } from "lucide-react";

export default function Header() {
  return (
    <header className="sticky top-0 z-40 flex h-14 items-center border-t-2 border-t-accent border-b border-border/50 bg-white/80 backdrop-blur-md shadow-soft px-4 lg:px-6">
      {/* Logo & Brand */}
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white">
          <Zap className="h-4 w-4" />
        </div>
        <span className="text-lg font-semibold tracking-tight text-primary">
          Streamworks-KI
        </span>
        <Badge variant="outline" className="hidden sm:inline-flex text-[10px] px-1.5 py-0">
          v2.0
        </Badge>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right side - reserved for future user menu, etc. */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground hidden md:inline">
          Enterprise Stream Automation
        </span>
      </div>
    </header>
  );
}
