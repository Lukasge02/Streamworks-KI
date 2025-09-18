/**
 * Micro-Interactions Service
 * Professional micro-interactions for enhanced user experience
 * Includes ripple effects, smart loading states, and visual feedback
 */

export interface RippleOptions {
  color?: string
  duration?: number
  size?: number
  opacity?: number
  easing?: string
}

export interface MicroInteractionSettings {
  rippleEnabled: boolean
  animationSpeed: 'slow' | 'normal' | 'fast'
  reducedMotion: boolean
  hapticFeedback: boolean
}

class MicroInteractionsService {
  private settings: MicroInteractionSettings = {
    rippleEnabled: true,
    animationSpeed: 'normal',
    reducedMotion: false,
    hapticFeedback: true
  }

  private animationSpeedMap = {
    slow: 1.5,
    normal: 1,
    fast: 0.7
  }

  constructor() {
    this.loadSettings()
    this.checkReducedMotionPreference()
  }

  private loadSettings(): void {
    if (typeof window === 'undefined') return

    try {
      const saved = localStorage.getItem('streamworks-micro-interactions')
      if (saved) {
        this.settings = { ...this.settings, ...JSON.parse(saved) }
      }
    } catch (error) {
      console.warn('Failed to load micro-interactions settings:', error)
    }
  }

  private saveSettings(): void {
    try {
      localStorage.setItem('streamworks-micro-interactions', JSON.stringify(this.settings))
    } catch (error) {
      console.warn('Failed to save micro-interactions settings:', error)
    }
  }

  private checkReducedMotionPreference(): void {
    if (typeof window !== 'undefined') {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
      this.settings.reducedMotion = mediaQuery.matches

      mediaQuery.addEventListener('change', (e) => {
        this.settings.reducedMotion = e.matches
      })
    }
  }

  /**
   * Create ripple effect on element
   */
  createRipple(
    element: HTMLElement,
    event: MouseEvent | TouchEvent,
    options: RippleOptions = {}
  ): void {
    if (!this.settings.rippleEnabled || this.settings.reducedMotion) return

    const {
      color = 'rgba(255, 255, 255, 0.6)',
      duration = 600,
      size = 0,
      opacity = 0.6,
      easing = 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
    } = options

    const rect = element.getBoundingClientRect()
    const clientX = 'clientX' in event ? event.clientX : event.touches[0].clientX
    const clientY = 'clientY' in event ? event.clientY : event.touches[0].clientY

    const x = clientX - rect.left
    const y = clientY - rect.top

    // Calculate ripple size
    const rippleSize = size || Math.max(rect.width, rect.height) * 2

    // Create ripple element
    const ripple = document.createElement('div')
    ripple.className = 'streamworks-ripple'
    ripple.style.cssText = `
      position: absolute;
      border-radius: 50%;
      pointer-events: none;
      transform: scale(0);
      animation: streamworks-ripple-animation ${duration * this.animationSpeedMap[this.settings.animationSpeed]}ms ${easing} forwards;
      background: ${color};
      opacity: ${opacity};
      width: ${rippleSize}px;
      height: ${rippleSize}px;
      left: ${x - rippleSize / 2}px;
      top: ${y - rippleSize / 2}px;
      z-index: 1000;
    `

    // Ensure parent has position relative
    const computedStyle = window.getComputedStyle(element)
    if (computedStyle.position === 'static') {
      element.style.position = 'relative'
    }

    // Ensure overflow is hidden
    element.style.overflow = 'hidden'

    element.appendChild(ripple)

    // Remove ripple after animation
    setTimeout(() => {
      if (ripple.parentNode) {
        ripple.parentNode.removeChild(ripple)
      }
    }, duration * this.animationSpeedMap[this.settings.animationSpeed])

    // Haptic feedback on supported devices
    this.triggerHapticFeedback('light')
  }

  /**
   * Create button press feedback
   */
  createButtonPress(element: HTMLElement): void {
    if (this.settings.reducedMotion) return

    element.style.transform = 'scale(0.95)'
    element.style.transition = `transform ${150 * this.animationSpeedMap[this.settings.animationSpeed]}ms ease-out`

    setTimeout(() => {
      element.style.transform = 'scale(1)'
    }, 150 * this.animationSpeedMap[this.settings.animationSpeed])
  }

  /**
   * Create loading shimmer effect
   */
  createShimmer(element: HTMLElement, duration: number = 1500): void {
    if (this.settings.reducedMotion) {
      element.style.background = '#f3f4f6'
      return
    }

    element.classList.add('streamworks-shimmer')
    element.style.background = `
      linear-gradient(
        90deg,
        #f0f0f0 25%,
        #e0e0e0 50%,
        #f0f0f0 75%
      )
    `
    element.style.backgroundSize = '200% 100%'
    element.style.animation = `streamworks-shimmer ${duration * this.animationSpeedMap[this.settings.animationSpeed]}ms ease-in-out infinite`
  }

  /**
   * Create pulsing effect for loading states
   */
  createPulse(element: HTMLElement, intensity: 'light' | 'medium' | 'strong' = 'medium'): void {
    if (this.settings.reducedMotion) return

    const opacityMap = {
      light: '0.7',
      medium: '0.5',
      strong: '0.3'
    }

    element.style.animation = `streamworks-pulse ${1000 * this.animationSpeedMap[this.settings.animationSpeed]}ms ease-in-out infinite`
    element.style.setProperty('--pulse-opacity', opacityMap[intensity])
  }

  /**
   * Create floating action animation
   */
  createFloatAnimation(element: HTMLElement): void {
    if (this.settings.reducedMotion) return

    element.style.animation = `streamworks-float ${3000 * this.animationSpeedMap[this.settings.animationSpeed]}ms ease-in-out infinite`
  }

  /**
   * Create stagger animation for lists
   */
  createStaggerAnimation(elements: NodeListOf<Element> | Element[], delay: number = 100): void {
    if (this.settings.reducedMotion) {
      elements.forEach(el => {
        (el as HTMLElement).style.opacity = '1'
        ;(el as HTMLElement).style.transform = 'translateY(0)'
      })
      return
    }

    elements.forEach((el, index) => {
      const htmlEl = el as HTMLElement
      htmlEl.style.opacity = '0'
      htmlEl.style.transform = 'translateY(20px)'
      htmlEl.style.transition = `all ${400 * this.animationSpeedMap[this.settings.animationSpeed]}ms ease-out`

      setTimeout(() => {
        htmlEl.style.opacity = '1'
        htmlEl.style.transform = 'translateY(0)'
      }, index * delay * this.animationSpeedMap[this.settings.animationSpeed])
    })
  }

  /**
   * Trigger haptic feedback (if supported)
   */
  private triggerHapticFeedback(type: 'light' | 'medium' | 'heavy' = 'light'): void {
    if (!this.settings.hapticFeedback) return

    if ('vibrate' in navigator) {
      const intensityMap = {
        light: [10],
        medium: [20],
        heavy: [30]
      }
      navigator.vibrate(intensityMap[type])
    }
  }

  /**
   * Update settings
   */
  updateSettings(newSettings: Partial<MicroInteractionSettings>): void {
    this.settings = { ...this.settings, ...newSettings }
    this.saveSettings()
  }

  /**
   * Get current settings
   */
  getSettings(): MicroInteractionSettings {
    return { ...this.settings }
  }

  /**
   * Initialize CSS animations
   */
  initializeStyles(): void {
    if (document.getElementById('streamworks-micro-interactions-styles')) return

    const style = document.createElement('style')
    style.id = 'streamworks-micro-interactions-styles'
    style.textContent = `
      @keyframes streamworks-ripple-animation {
        to {
          transform: scale(1);
          opacity: 0;
        }
      }

      @keyframes streamworks-shimmer {
        0% {
          background-position: -200% 0;
        }
        100% {
          background-position: 200% 0;
        }
      }

      @keyframes streamworks-pulse {
        0%, 100% {
          opacity: 1;
        }
        50% {
          opacity: var(--pulse-opacity, 0.5);
        }
      }

      @keyframes streamworks-float {
        0%, 100% {
          transform: translateY(0px);
        }
        50% {
          transform: translateY(-10px);
        }
      }

      .streamworks-ripple {
        will-change: transform, opacity;
      }

      .streamworks-shimmer {
        will-change: background-position;
      }

      .streamworks-interactive {
        transition: all 200ms ease-out;
        cursor: pointer;
        user-select: none;
        -webkit-tap-highlight-color: transparent;
      }

      .streamworks-interactive:hover {
        transform: translateY(-1px);
      }

      .streamworks-interactive:active {
        transform: scale(0.98);
      }

      @media (prefers-reduced-motion: reduce) {
        .streamworks-interactive,
        .streamworks-interactive:hover,
        .streamworks-interactive:active {
          transform: none !important;
          animation: none !important;
        }
      }
    `

    document.head.appendChild(style)
  }
}

// Export singleton
export const microInteractionsService = new MicroInteractionsService()

// Initialize styles when service is imported
if (typeof window !== 'undefined') {
  microInteractionsService.initializeStyles()
}