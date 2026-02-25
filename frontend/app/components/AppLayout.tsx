"use client";

import React from "react";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import { cn } from "@/lib/utils";

interface AppLayoutProps {
  children: React.ReactNode;
  fullWidth?: boolean;
  noScroll?: boolean;
}

export default function AppLayout({ children, fullWidth, noScroll }: AppLayoutProps) {
  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <Header />
      <div className="flex flex-1 min-h-0">
        <Sidebar />
        <main className={cn(
          "flex-1",
          noScroll ? "overflow-hidden" : "overflow-y-auto scrollbar-thin"
        )}>
          {noScroll ? (
            <div className="h-full">
              {children}
            </div>
          ) : (
            <div className={cn(
              fullWidth
                ? "w-full p-4"
                : "mx-auto w-full max-w-7xl p-4 sm:p-6 lg:p-8"
            )}>
              {children}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
