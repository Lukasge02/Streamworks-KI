import { forwardRef } from 'react';
import type { ReactNode } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  variant?: 'default' | 'filled';
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      variant = 'default',
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    const baseInputClasses = `
      block w-full px-3 py-2 text-sm transition-colors duration-200
      border rounded-lg shadow-sm placeholder-neutral-400 dark:placeholder-neutral-500
      focus:outline-none focus:ring-2 focus:ring-offset-0
      disabled:opacity-50 disabled:cursor-not-allowed
    `;

    const variantClasses = {
      default: `
        bg-white dark:bg-neutral-900 
        border-neutral-300 dark:border-neutral-600
        text-neutral-900 dark:text-neutral-100
        focus:border-primary-500 focus:ring-primary-500
      `,
      filled: `
        bg-neutral-100 dark:bg-neutral-800 
        border-transparent
        text-neutral-900 dark:text-neutral-100
        focus:bg-white dark:focus:bg-neutral-900
        focus:border-primary-500 focus:ring-primary-500
      `,
    };

    const errorClasses = error
      ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
      : '';

    const inputClasses = `
      ${baseInputClasses}
      ${variantClasses[variant]}
      ${errorClasses}
      ${leftIcon ? 'pl-10' : ''}
      ${rightIcon ? 'pr-10' : ''}
      ${className}
    `;

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
            {label}
            {props.required && (
              <span className="text-red-500 ml-1">*</span>
            )}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div className="text-neutral-400 dark:text-neutral-500">
                {leftIcon}
              </div>
            </div>
          )}
          
          <input
            ref={ref}
            disabled={disabled}
            className={inputClasses}
            {...props}
          />
          
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <div className="text-neutral-400 dark:text-neutral-500">
                {rightIcon}
              </div>
            </div>
          )}
        </div>
        
        {error && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        )}
        
        {helperText && !error && (
          <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
export type { InputProps };