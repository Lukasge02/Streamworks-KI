"use client";

import { cn } from "@/app/utils/cn";
import { ReactNode } from "react";

interface ShineBorderProps {
    borderRadius?: number;
    borderWidth?: number;
    duration?: number;
    color?: string | string[];
    className?: string;
    children: ReactNode;
}

export function ShineBorder({
    borderRadius = 12,
    borderWidth = 1,
    duration = 14,
    color = ["#0082D9", "#00D4AA", "#0082D9"],
    className,
    children,
}: ShineBorderProps) {
    return (
        <div
            style={{
                ["--border-radius" as string]: `${borderRadius}px`,
            }}
            className={cn(
                "relative rounded-[--border-radius] bg-white p-px",
                className
            )}
        >
            <div
                style={{
                    ["--border-width" as string]: `${borderWidth}px`,
                    ["--border-radius" as string]: `${borderRadius}px`,
                    ["--duration" as string]: `${duration}s`,
                    ["--background-radial-gradient" as string]: `radial-gradient(transparent,transparent, ${Array.isArray(color) ? color.join(",") : color
                        },transparent,transparent)`,
                }}
                className={cn(
                    "absolute inset-0 rounded-[--border-radius]",
                    "before:absolute before:inset-0 before:rounded-[--border-radius]",
                    "before:p-[--border-width]",
                    "before:bg-[image:--background-radial-gradient]",
                    "before:bg-[length:300%_300%]",
                    "before:animate-shine",
                    "before:![mask:linear-gradient(#fff_0_0)_content-box,linear-gradient(#fff_0_0)]",
                    "before:![mask-composite:exclude]"
                )}
            />
            <div className="relative rounded-[--border-radius] bg-white">
                {children}
            </div>
        </div>
    );
}
