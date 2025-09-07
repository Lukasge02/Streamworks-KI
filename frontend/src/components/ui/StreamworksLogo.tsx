/**
 * Original Streamworks Logo Component
 * Recreated from the professional brand asset
 */

interface StreamworksLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'full' | 'icon-only'
  className?: string
}

export function StreamworksLogo({ 
  size = 'md', 
  variant = 'full', 
  className = '' 
}: StreamworksLogoProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12', 
    lg: 'w-16 h-16',
    xl: 'w-24 h-24'
  }

  const textSizes = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg', 
    xl: 'text-2xl'
  }

  // Original Streamworks Icon - Network/Flow Pattern
  const StreamworksIcon = () => (
    <div className={`${sizeClasses[size]} bg-slate-800 rounded-full flex items-center justify-center ${className}`}>
      <svg 
        className="w-3/5 h-3/5 text-white" 
        viewBox="0 0 100 100" 
        fill="currentColor"
      >
        {/* Network nodes */}
        <circle cx="20" cy="20" r="6" />
        <circle cx="80" cy="20" r="6" />
        <circle cx="50" cy="50" r="6" />
        <circle cx="20" cy="80" r="6" />
        <circle cx="80" cy="80" r="6" />
        
        {/* Connection lines with workflow arrows */}
        <path d="M26 20 L44 50 M56 50 L74 20" stroke="currentColor" strokeWidth="2" fill="none" />
        <path d="M20 26 L20 74 M80 26 L80 74" stroke="currentColor" strokeWidth="2" fill="none" />
        <path d="M26 80 L44 50 M56 50 L74 80" stroke="currentColor" strokeWidth="2" fill="none" />
        
        {/* Workflow direction arrows */}
        <path d="M42 48 L46 50 L42 52" stroke="currentColor" strokeWidth="1.5" fill="none" />
        <path d="M54 52 L58 50 L54 48" stroke="currentColor" strokeWidth="1.5" fill="none" />
      </svg>
    </div>
  )

  if (variant === 'icon-only') {
    return <StreamworksIcon />
  }

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <StreamworksIcon />
      
      <div className="text-center mt-3">
        <div className={`${textSizes[size]} font-bold text-slate-800 tracking-[0.2em] leading-none`}>
          STREAMWORKS
        </div>
        <div className={`${size === 'sm' ? 'text-xs' : size === 'xl' ? 'text-sm' : 'text-xs'} text-slate-600 tracking-wider font-medium mt-1`}>
          WORKLOAD AUTOMATION
        </div>
      </div>
    </div>
  )
}

// Branded version for headers
export function StreamworksHeader({ className = '' }: { className?: string }) {
  return (
    <div className={`flex items-center space-x-4 ${className}`}>
      <StreamworksLogo size="lg" variant="icon-only" />
      <div>
        <h1 className="text-3xl font-bold text-slate-800 tracking-wide">
          STREAMWORKS
        </h1>
        <p className="text-slate-600 text-sm tracking-wider font-medium -mt-1">
          WORKLOAD AUTOMATION
        </p>
      </div>
    </div>
  )
}