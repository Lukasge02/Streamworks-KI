"use client";

import { Shield, ShieldAlert, Globe, Lock, Users } from "lucide-react";
import { cn } from "@/app/utils/cn";

export type AccessLevel = "public" | "internal" | "restricted" | "project";

interface DocumentAccessBadgeProps {
  level: AccessLevel;
  className?: string;
  showLabel?: boolean;
}

export default function DocumentAccessBadge({
  level,
  className,
  showLabel = true,
}: DocumentAccessBadgeProps) {
  const config = {
    public: {
      icon: Globe,
      label: "Öffentlich",
      color: "text-green-600 bg-green-50 border-green-200",
      iconColor: "text-green-500",
    },
    internal: {
      icon: Shield,
      label: "Intern",
      color: "text-blue-600 bg-blue-50 border-blue-200",
      iconColor: "text-blue-500",
    },
    restricted: {
      icon: Lock,
      label: "Eingeschränkt",
      color: "text-amber-600 bg-amber-50 border-amber-200",
      iconColor: "text-amber-500",
    },
    project: {
      icon: Users,
      label: "Projekt",
      color: "text-purple-600 bg-purple-50 border-purple-200",
      iconColor: "text-purple-500",
    },
  };

  const style = config[level] || config.internal;
  const Icon = style.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border",
        style.color,
        className,
      )}
    >
      <Icon className={cn("w-3 h-3", style.iconColor)} />
      {showLabel && style.label}
    </span>
  );
}
