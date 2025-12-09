"use client";

import { useState } from "react";
import { Info } from "lucide-react";
import { cn } from "@/app/utils/cn";

interface FormFieldProps {
    label: string;
    hint?: string;
    required?: boolean;
    children: React.ReactNode;
    className?: string;
}

export function FormField({ label, hint, required, children, className }: FormFieldProps) {
    const [showTooltip, setShowTooltip] = useState(false);

    return (
        <div className={cn("space-y-2", className)}>
            <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">
                    {label}
                    {required && <span className="text-red-500 ml-0.5">*</span>}
                </label>
                {hint && (
                    <div className="relative">
                        <button
                            type="button"
                            onMouseEnter={() => setShowTooltip(true)}
                            onMouseLeave={() => setShowTooltip(false)}
                            onFocus={() => setShowTooltip(true)}
                            onBlur={() => setShowTooltip(false)}
                            className="w-4 h-4 rounded-full bg-gray-200 hover:bg-[#0082D9] hover:text-white flex items-center justify-center transition-colors"
                        >
                            <Info className="w-3 h-3" />
                        </button>
                        {showTooltip && (
                            <div className="absolute left-6 top-1/2 -translate-y-1/2 z-50 w-64 p-2.5 bg-gray-900 text-white text-xs rounded-lg shadow-lg whitespace-normal">
                                {hint}
                                <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-900 rotate-45" />
                            </div>
                        )}
                    </div>
                )}
            </div>
            {children}
        </div>
    );
}

interface InputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
    error?: string;
}

export function InputField({ error, className, ...props }: InputFieldProps) {
    return (
        <input
            {...props}
            className={cn(
                "w-full px-4 py-3 rounded-xl border transition-all duration-200",
                "focus:outline-none focus:ring-2 focus:ring-[#0082D9]/20 focus:border-[#0082D9]",
                "placeholder:text-gray-400",
                error ? "border-red-300 bg-red-50" : "border-gray-200 bg-white hover:border-gray-300",
                className
            )}
        />
    );
}

interface TextAreaFieldProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
    error?: string;
}

export function TextAreaField({ error, className, ...props }: TextAreaFieldProps) {
    return (
        <textarea
            {...props}
            className={cn(
                "w-full px-4 py-3 rounded-xl border transition-all duration-200 resize-none",
                "focus:outline-none focus:ring-2 focus:ring-[#0082D9]/20 focus:border-[#0082D9]",
                "placeholder:text-gray-400",
                error ? "border-red-300 bg-red-50" : "border-gray-200 bg-white hover:border-gray-300",
                className
            )}
        />
    );
}

interface SelectFieldProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
    error?: string;
    options: { value: string; label: string }[];
}

export function SelectField({ error, options, className, ...props }: SelectFieldProps) {
    return (
        <select
            {...props}
            className={cn(
                "w-full px-4 py-3 rounded-xl border transition-all duration-200 appearance-none bg-white",
                "focus:outline-none focus:ring-2 focus:ring-[#0082D9]/20 focus:border-[#0082D9]",
                error ? "border-red-300 bg-red-50" : "border-gray-200 hover:border-gray-300",
                className
            )}
        >
            {options.map((opt) => (
                <option key={opt.value} value={opt.value}>
                    {opt.label}
                </option>
            ))}
        </select>
    );
}
