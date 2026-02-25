"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Check, AlertCircle } from "lucide-react";

export interface FloatingTextareaProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  id?: string;
  required?: boolean;
  error?: string;
  success?: boolean;
  maxLength?: number;
  helperText?: string;
  className?: string;
  disabled?: boolean;
  rows?: number;
}

const FloatingTextarea = React.forwardRef<
  HTMLTextAreaElement,
  FloatingTextareaProps
>(
  (
    {
      label,
      value,
      onChange,
      id,
      required,
      error,
      success,
      maxLength,
      helperText,
      className,
      disabled,
      rows = 4,
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = React.useState(false);
    const textareaId = id || `floating-textarea-${React.useId()}`;
    const hasValue = value !== undefined && value !== "";
    const isActive = isFocused || hasValue;

    return (
      <div className={cn("space-y-1.5", className)}>
        <div className="floating-label-wrapper group relative">
          {/* Textarea */}
          <textarea
            ref={ref}
            id={textareaId}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            disabled={disabled}
            maxLength={maxLength}
            rows={rows}
            className={cn(
              "floating-textarea peer",
              "flex w-full rounded-lg border bg-surface-raised text-sm resize-y",
              "transition-all duration-200",
              "focus-visible:outline-none",
              "px-3 pt-6 pb-2",
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
              disabled && "cursor-not-allowed opacity-50"
            )}
          />

          {/* Floating Label */}
          <label
            htmlFor={textareaId}
            className={cn(
              "absolute pointer-events-none transition-all duration-200 ease-out left-3",
              // Inactive state (acts as placeholder)
              !isActive && "top-4 text-muted-foreground text-sm",
              // Active state (floated up)
              isActive && "top-1.5 text-xs font-medium",
              isActive && !error && "text-accent",
              // Error state
              error && "text-destructive"
            )}
          >
            {label}
            {required && <span className="text-destructive ml-0.5">*</span>}
          </label>

          {/* Status Icon (top right) */}
          <div className="absolute right-3 top-2">
            {error && (
              <AlertCircle className="h-4 w-4 text-destructive animate-in fade-in duration-200" />
            )}
            {success && !error && hasValue && (
              <Check className="h-4 w-4 text-success animate-in fade-in duration-200" />
            )}
          </div>
        </div>

        {/* Helper Text / Error / Character Count */}
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
              <span
                className={cn(
                  "text-xs ml-2",
                  value?.length > maxLength * 0.9
                    ? "text-warning"
                    : "text-muted-foreground"
                )}
              >
                {value?.length || 0}/{maxLength}
              </span>
            )}
          </div>
        )}
      </div>
    );
  }
);

FloatingTextarea.displayName = "FloatingTextarea";

export { FloatingTextarea };
