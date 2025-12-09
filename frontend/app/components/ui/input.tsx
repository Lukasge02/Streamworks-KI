"use client";

import * as React from "react";
import { cn } from "@/app/utils/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> { }

const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, type, ...props }, ref) => {
        return (
            <input
                type={type}
                className={cn(
                    "flex h-11 w-full rounded-lg border-2 border-gray-200 bg-white px-4 py-2 text-sm text-gray-900 placeholder:text-gray-400",
                    "transition-all duration-200",
                    "focus:border-[#0082D9] focus:outline-none focus:ring-2 focus:ring-[#0082D9]/20",
                    "hover:border-gray-300",
                    "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50",
                    className
                )}
                ref={ref}
                {...props}
            />
        );
    }
);
Input.displayName = "Input";

export { Input };
