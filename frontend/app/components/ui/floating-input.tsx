"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Check, AlertCircle } from "lucide-react";

export interface FloatingInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  id?: string;
  required?: boolean;
  error?: string;
  success?: boolean;
  icon?: React.ReactNode;
  maxLength?: number;
  type?: "text" | "email" | "tel" | "number";
  helperText?: string;
  className?: string;
  disabled?: boolean;
  min?: number;
  max?: number;
  transformValue?: (value: string) => string;
}

const FloatingInput = React.forwardRef<HTMLInputElement, FloatingInputProps>(
  (
    {
      label,
      value,
      onChange,
      id,
      required,
      error,
      success,
      icon,
      maxLength,
      type = "text",
      helperText,
      className,
      disabled,
      min,
      max,
      transformValue,
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = React.useState(false);
    const inputId = id || `floating-input-${React.useId()}`;
    const hasValue = value !== undefined && value !== "";
    const isActive = isFocused || hasValue;

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      let newValue = e.target.value;
      if (transformValue) {
        newValue = transformValue(newValue);
      }
      onChange(newValue);
    };

    return (
      <div className={cn("space-y-1.5", className)}>
        <div className="floating-label-wrapper group">
          {/* Icon (left) */}
          {icon && (
            <div
              className={cn(
                "absolute left-3 top-1/2 -translate-y-1/2 z-10 transition-colors duration-200",
                isActive ? "text-accent" : "text-muted-foreground",
                error && "text-destructive"
              )}
            >
              {icon}
            </div>
          )}

          {/* Input */}
          <input
            ref={ref}
            id={inputId}
            type={type}
            value={value}
            onChange={handleChange}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            disabled={disabled}
            maxLength={maxLength}
            min={min}
            max={max}
            className={cn(
              "floating-input peer",
              "flex h-12 w-full rounded-lg border bg-surface-raised text-sm",
              "transition-all duration-200",
              "focus-visible:outline-none",
              icon ? "pl-10 pr-10" : "px-3 pr-10",
              "pt-4 pb-1",
              // Default state
              "border-border/70 shadow-sm",
              // Focus state
              "focus:border-accent focus:shadow-md focus:ring-2 focus:ring-accent/10",
              // Error state
              error && "border-destructive focus:border-destructive focus:ring-destructive/10",
              // Success state
              success && !error && "border-success/50",
              // Disabled state
              disabled && "cursor-not-allowed opacity-50"
            )}
          />

          {/* Floating Label */}
          <label
            htmlFor={inputId}
            className={cn(
              "floating-label",
              "absolute pointer-events-none transition-all duration-200 ease-out",
              icon ? "left-10" : "left-3",
              // Inactive state (acts as placeholder)
              !isActive && "top-1/2 -translate-y-1/2 text-muted-foreground text-sm",
              // Active state (floated up)
              isActive && "top-1 translate-y-0 text-xs font-medium",
              isActive && !error && "text-accent",
              // Error state
              error && "text-destructive"
            )}
          >
            {label}
            {required && <span className="text-destructive ml-0.5">*</span>}
          </label>

          {/* Status Icon (right) */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            {error && (
              <AlertCircle className="h-4 w-4 text-destructive animate-in fade-in duration-200" />
            )}
            {success && !error && hasValue && (
              <Check className="h-4 w-4 text-success animate-in fade-in duration-200" />
            )}
          </div>
        </div>

        {/* Helper Text / Error */}
        {(helperText || error || maxLength) && (
          <div className="flex justify-between items-start px-1">
            <p
              className={cn(
                "text-xs transition-colors duration-200",
                error ? "text-destructive" : "text-muted-foreground"
              )}
            >
              {error || helperText}
            </p>
            {maxLength && (
              <span className="text-xs text-muted-foreground ml-2">
                {value?.length || 0}/{maxLength}
              </span>
            )}
          </div>
        )}
      </div>
    );
  }
);

FloatingInput.displayName = "FloatingInput";

export { FloatingInput };
