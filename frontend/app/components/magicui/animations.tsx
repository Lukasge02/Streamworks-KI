"use client";

import { cn } from "@/app/utils/cn";
import { motion } from "framer-motion";

interface AnimatedCardProps {
    children: React.ReactNode;
    className?: string;
    delay?: number;
}

export function AnimatedCard({ children, className, delay = 0 }: AnimatedCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
                duration: 0.5,
                delay,
                ease: [0.21, 0.47, 0.32, 0.98],
            }}
            className={cn(
                "rounded-xl border border-gray-200 bg-white shadow-sm",
                "transition-shadow duration-300 hover:shadow-lg",
                className
            )}
        >
            {children}
        </motion.div>
    );
}

interface FadeInProps {
    children: React.ReactNode;
    delay?: number;
    direction?: "up" | "down" | "left" | "right";
    className?: string;
}

export function FadeIn({ children, delay = 0, direction = "up", className }: FadeInProps) {
    const directionMap = {
        up: { y: 20 },
        down: { y: -20 },
        left: { x: 20 },
        right: { x: -20 },
    };

    return (
        <motion.div
            initial={{ opacity: 0, ...directionMap[direction] }}
            animate={{ opacity: 1, x: 0, y: 0 }}
            transition={{
                duration: 0.5,
                delay,
                ease: [0.21, 0.47, 0.32, 0.98],
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

interface PulseProps {
    children: React.ReactNode;
    className?: string;
}

export function Pulse({ children, className }: PulseProps) {
    return (
        <motion.div
            animate={{
                scale: [1, 1.02, 1],
            }}
            transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
            }}
            className={className}
        >
            {children}
        </motion.div>
    );
}
