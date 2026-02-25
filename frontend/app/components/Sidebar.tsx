"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Wand2, FileText, MessageSquare, Menu, X } from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { label: "Stream Wizard", href: "/wizard", icon: Wand2 },
  { label: "Streams", href: "/streams", icon: FileText },
  { label: "RAG Chat", href: "/chat", icon: MessageSquare },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

  const navContent = (
    <nav className="flex flex-col gap-1 px-3 py-4">
      {navItems.map((item) => {
        const Icon = item.icon;
        const active = isActive(item.href);

        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={() => setMobileOpen(false)}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200",
              active
                ? "border-l-[3px] border-accent bg-accent/8 text-accent"
                : "border-l-[3px] border-transparent text-muted-foreground hover:bg-muted hover:text-primary"
            )}
          >
            <Icon className="h-4 w-4 shrink-0" />
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );

  return (
    <>
      {/* Mobile toggle button */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed bottom-4 left-4 z-50 flex h-10 w-10 items-center justify-center rounded-full bg-primary text-white shadow-elevated lg:hidden"
        aria-label="Navigation umschalten"
      >
        {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar - mobile drawer */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-[var(--sidebar-width)] border-r border-border bg-surface-raised transition-transform duration-200 lg:hidden",
          "top-14", // Below header
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {navContent}
      </aside>

      {/* Sidebar - desktop */}
      <aside className="hidden lg:flex lg:w-[var(--sidebar-width)] lg:flex-col lg:border-r lg:border-border lg:bg-surface-raised">
        {navContent}
        <div className="mt-auto border-t border-border/50 px-4 py-3">
          <span className="text-[10px] text-muted-foreground">Streamworks-KI v2.0</span>
        </div>
      </aside>
    </>
  );
}
