import { forwardRef } from 'react';
import type { ReactNode } from 'react';
import { Loader } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: ReactNode;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      children,
      leftIcon,
      rightIcon,
      disabled,
      className = '',
      ...props
    },
    ref
  ) => {
    const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

    const variantClasses = {
      primary: 'bg-primary-600 hover:bg-primary-700 focus:ring-primary-500 text-white shadow-sm hover:shadow-md',
      secondary: 'bg-neutral-200 dark:bg-neutral-700 hover:bg-neutral-300 dark:hover:bg-neutral-600 focus:ring-neutral-500 text-neutral-900 dark:text-neutral-100 shadow-sm',
      outline: 'border border-neutral-300 dark:border-neutral-600 bg-transparent hover:bg-neutral-50 dark:hover:bg-neutral-800 focus:ring-neutral-500 text-neutral-700 dark:text-neutral-300',
      ghost: 'bg-transparent hover:bg-neutral-100 dark:hover:bg-neutral-800 focus:ring-neutral-500 text-neutral-700 dark:text-neutral-300',
      danger: 'bg-red-600 hover:bg-red-700 focus:ring-red-500 text-white shadow-sm hover:shadow-md',
    };

    const sizeClasses = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-sm',
      lg: 'px-6 py-3 text-base',
    };

    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={`
          ${baseClasses}
          ${variantClasses[variant]}
          ${sizeClasses[size]}
          ${className}
        `}
        {...props}
      >
        {loading && (
          <Loader size={16} className="animate-spin mr-2" />
        )}
        
        {!loading && leftIcon && (
          <span className="mr-2">{leftIcon}</span>
        )}
        
        {children}
        
        {!loading && rightIcon && (
          <span className="ml-2">{rightIcon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
export type { ButtonProps };