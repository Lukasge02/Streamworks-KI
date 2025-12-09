"use client";

import { cn } from "@/app/utils/cn";

interface BorderBeamProps {
    className?: string;
    size?: number;
    duration?: number;
    borderWidth?: number;
    anchor?: number;
    colorFrom?: string;
    colorTo?: string;
    delay?: number;
}

export function BorderBeam({
    className,
    size = 200,
    duration = 15,
    anchor = 90,
    borderWidth = 1.5,
    colorFrom = "#0082D9",
    colorTo = "#00D4AA",
    delay = 0,
}: BorderBeamProps) {
    return (
        <div
            style={{
                ["--size" as string]: size,
                ["--duration" as string]: duration,
                ["--anchor" as string]: anchor,
                ["--border-width" as string]: borderWidth,
                ["--color-from" as string]: colorFrom,
                ["--color-to" as string]: colorTo,
                ["--delay" as string]: `-${delay}s`,
            }}
            className={cn(
                "pointer-events-none absolute inset-0 rounded-[inherit]",
                "![mask-clip:padding-box,border-box] ![mask-composite:intersect]",
                "[mask:linear-gradient(transparent,transparent),linear-gradient(white,white)]",
                "after:absolute after:aspect-square after:w-[calc(var(--size)*1px)]",
                "after:animate-border-beam",
                "after:[animation-delay:var(--delay)]",
                "after:[background:linear-gradient(to_left,var(--color-from),var(--color-to),transparent)]",
                "after:[offset-anchor:calc(var(--anchor)*1%)_50%]",
                "after:[offset-path:rect(0_auto_auto_0_round_calc(var(--size)*1px))]",
                "border-[calc(var(--border-width)*1px)] border-transparent",
                className
            )}
        />
    );
}
