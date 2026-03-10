"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Wand2, MessageSquare, HelpCircle, LayoutGrid, FileStack } from "lucide-react";

interface NavTab {
  label: string;
  href: string;
  icon: React.ElementType;
  matchPaths: string[];
}

const navTabs: NavTab[] = [
  {
    label: "Stream Erstellen",
    href: "/wizard",
    icon: Wand2,
    matchPaths: ["/wizard", "/xml-editor"],
  },
  {
    label: "Streams",
    href: "/streams",
    icon: LayoutGrid,
    matchPaths: ["/streams"],
  },
  {
    label: "Dokumente",
    href: "/dokumente",
    icon: FileStack,
    matchPaths: ["/dokumente"],
  },
  {
    label: "Hilfe",
    href: "/chat",
    icon: MessageSquare,
    matchPaths: ["/chat"],
  },
];

export default function Header() {
  const pathname = usePathname();

  const isActive = (tab: NavTab) =>
    tab.matchPaths.some(
      (p) => pathname === p || pathname.startsWith(p + "/")
    );

  return (
    <header className="sticky top-0 z-40 flex h-12 items-center bg-header px-4 lg:px-6">
      {/* Logo & Brand */}
      <Link href="/wizard" className="flex items-center gap-2.5 shrink-0">
        <div className="flex items-center justify-center rounded bg-white px-1.5 py-0.5">
          <Image
            src="/streamworks-logo.png"
            alt="Streamworks"
            width={735}
            height={423}
            className="h-6 w-auto"
          />
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-sm font-bold tracking-wide text-white uppercase">
            Streamworks
          </span>
          <span className="text-sm text-white/60 font-normal">
            / KI-Assistent
          </span>
        </div>
      </Link>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Navigation Tabs */}
      <nav className="flex h-full items-stretch gap-1">
        {navTabs.map((tab) => {
          const Icon = tab.icon;
          const active = isActive(tab);

          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                "flex items-center gap-2 px-4 text-sm font-medium transition-colors duration-150 border-b-2",
                active
                  ? "text-white border-white"
                  : "text-white/60 border-transparent hover:text-white hover:bg-white/10"
              )}
            >
              <Icon className="h-4 w-4" />
              <span className="hidden sm:inline">{tab.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right side: Help + User */}
      <div className="flex items-center gap-3 shrink-0">
        <button
          className="flex h-8 w-8 items-center justify-center rounded-full text-white/60 hover:text-white hover:bg-white/10 transition-colors"
          title="Hilfe"
        >
          <HelpCircle className="h-4.5 w-4.5" />
        </button>

        {/* User avatar */}
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-white/20 text-xs font-bold text-white">
            GE
          </div>
          <span className="hidden md:inline text-xs text-white/80 font-medium">
            GECK003
          </span>
        </div>
      </div>
    </header>
  );
}
