"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { ChevronDown, Loader2, Check, AlertCircle } from "lucide-react";

export interface FloatingSelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options?: { label: string; value: string }[];
  id?: string;
  required?: boolean;
  error?: string;
  success?: boolean;
  icon?: React.ReactNode;
  helperText?: string;
  className?: string;
  disabled?: boolean;
  isLoading?: boolean;
  placeholder?: string;
}

const FloatingSelect = React.forwardRef<HTMLSelectElement, FloatingSelectProps>(
  (
    {
      label,
      value,
      onChange,
      options = [],
      id,
      required,
      error,
      success,
      icon,
      helperText,
      className,
      disabled,
      isLoading,
      placeholder,
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = React.useState(false);
    const selectId = id || `floating-select-${React.useId()}`;
    const hasValue = value !== undefined && value !== "";
    const isActive = isFocused || hasValue;

    return (
      <div className={cn("space-y-1.5", className)}>
        <div className="floating-label-wrapper group relative">
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

          {/* Select */}
          <select
            ref={ref}
            id={selectId}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            disabled={disabled || isLoading}
            className={cn(
              "floating-select peer appearance-none",
              "flex h-12 w-full rounded-lg border bg-surface-raised text-sm cursor-pointer",
              "transition-all duration-200",
              "focus-visible:outline-none",
              icon ? "pl-10 pr-10" : "pl-3 pr-10",
              "pt-4 pb-1",
              // Default state
              "border-border/70 shadow-sm",
              // Focus state
              "focus:border-accent focus:shadow-md focus:ring-2 focus:ring-accent/10",
              // Error state
              error &&
                "border-destructive focus:border-destructive focus:ring-destructive/10",
              // Success state
              success && !error && "border-success/50",
              // Disabled state
              (disabled || isLoading) && "cursor-not-allowed opacity-50",
              // Empty value styling
              !hasValue && "text-transparent"
            )}
          >
            <option value="" disabled hidden>
              {placeholder || label}
            </option>
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          {/* Floating Label */}
          <label
            htmlFor={selectId}
            className={cn(
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

          {/* Right side icons */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
            {isLoading && (
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            )}
            {!isLoading && error && (
              <AlertCircle className="h-4 w-4 text-destructive animate-in fade-in duration-200" />
            )}
            {!isLoading && success && !error && hasValue && (
              <Check className="h-4 w-4 text-success animate-in fade-in duration-200" />
            )}
            {!isLoading && (
              <ChevronDown
                className={cn(
                  "h-4 w-4 transition-transform duration-200",
                  isFocused && "rotate-180",
                  isActive ? "text-accent" : "text-muted-foreground"
                )}
              />
            )}
          </div>
        </div>

        {/* Helper Text / Error */}
        {(helperText || error) && (
          <p
            className={cn(
              "text-xs px-1 transition-colors duration-200",
              error ? "text-destructive" : "text-muted-foreground"
            )}
          >
            {error || helperText}
          </p>
        )}
      </div>
    );
  }
);

FloatingSelect.displayName = "FloatingSelect";

export { FloatingSelect };
