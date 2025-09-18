/**
 * Mobile-First Responsive Service
 * Professional responsive design with touch optimization and mobile UX patterns
 */

export interface BreakpointConfig {
  name: string
  minWidth: number
  maxWidth?: number
  columns: number
  spacing: string
  fontSize: string
}

export interface TouchGesture {
  type: 'tap' | 'long-press' | 'swipe' | 'pinch' | 'double-tap'
  element: HTMLElement
  callback: (details: any) => void
  options?: {
    threshold?: number
    timeout?: number
    direction?: 'left' | 'right' | 'up' | 'down' | 'any'
  }
}

export interface DeviceInfo {
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  hasTouch: boolean
  orientation: 'portrait' | 'landscape'
  screenSize: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
  devicePixelRatio: number
  connectionSpeed: 'slow' | 'fast' | 'unknown'
}

class MobileResponsiveService {
  private breakpoints: BreakpointConfig[] = [
    { name: 'xs', minWidth: 0, maxWidth: 639, columns: 1, spacing: '4px', fontSize: '14px' },
    { name: 'sm', minWidth: 640, maxWidth: 767, columns: 2, spacing: '8px', fontSize: '14px' },
    { name: 'md', minWidth: 768, maxWidth: 1023, columns: 3, spacing: '12px', fontSize: '16px' },
    { name: 'lg', minWidth: 1024, maxWidth: 1279, columns: 4, spacing: '16px', fontSize: '16px' },
    { name: 'xl', minWidth: 1280, maxWidth: 1535, columns: 5, spacing: '20px', fontSize: '16px' },
    { name: '2xl', minWidth: 1536, columns: 6, spacing: '24px', fontSize: '16px' }
  ]

  private currentBreakpoint: BreakpointConfig = this.breakpoints[0]
  private deviceInfo: DeviceInfo
  private touchGestures: Map<HTMLElement, TouchGesture[]> = new Map()
  private listeners: ((info: DeviceInfo) => void)[] = []
  private resizeObserver?: ResizeObserver

  constructor() {
    this.deviceInfo = this.detectDevice()
    this.setupEventListeners()
    this.initializeResponsiveFeatures()
    this.setupTouchOptimizations()
  }

  private detectDevice(): DeviceInfo {
    const userAgent = navigator.userAgent.toLowerCase()
    const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0

    // Device detection
    const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent) ||
      (hasTouch && window.innerWidth < 768)

    const isTablet = /ipad|android(?!.*mobile)|tablet/i.test(userAgent) ||
      (hasTouch && window.innerWidth >= 768 && window.innerWidth <= 1024)

    const isDesktop = !isMobile && !isTablet

    // Screen size detection
    const screenSize = this.getScreenSize()

    // Orientation detection
    const orientation = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'

    // Connection speed detection
    const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection
    let connectionSpeed: 'slow' | 'fast' | 'unknown' = 'unknown'

    if (connection) {
      const effectiveType = connection.effectiveType
      connectionSpeed = effectiveType === 'slow-2g' || effectiveType === '2g' ? 'slow' : 'fast'
    }

    return {
      isMobile,
      isTablet,
      isDesktop,
      hasTouch,
      orientation,
      screenSize,
      devicePixelRatio: window.devicePixelRatio || 1,
      connectionSpeed
    }
  }

  private getScreenSize(): DeviceInfo['screenSize'] {
    const width = window.innerWidth

    if (width < 640) return 'xs'
    if (width < 768) return 'sm'
    if (width < 1024) return 'md'
    if (width < 1280) return 'lg'
    if (width < 1536) return 'xl'
    return '2xl'
  }

  private setupEventListeners(): void {
    if (typeof window === 'undefined') return

    // Resize listener
    window.addEventListener('resize', () => {
      this.updateDeviceInfo()
    })

    // Orientation change
    window.addEventListener('orientationchange', () => {
      setTimeout(() => {
        this.updateDeviceInfo()
      }, 100)
    })

    // Connection change
    if ('connection' in navigator) {
      (navigator as any).connection.addEventListener('change', () => {
        this.updateDeviceInfo()
      })
    }

    // Setup ResizeObserver for component-level responsiveness
    if ('ResizeObserver' in window) {
      this.resizeObserver = new ResizeObserver((entries) => {
        entries.forEach(entry => {
          this.handleElementResize(entry.target as HTMLElement, entry.contentRect)
        })
      })
    }
  }

  private updateDeviceInfo(): void {
    const oldInfo = this.deviceInfo
    this.deviceInfo = this.detectDevice()

    // Update breakpoint
    this.currentBreakpoint = this.getCurrentBreakpoint()

    // Apply responsive CSS
    this.applyResponsiveCSS()

    // Notify listeners if device info changed
    if (JSON.stringify(oldInfo) !== JSON.stringify(this.deviceInfo)) {
      this.notifyListeners()
    }
  }

  private getCurrentBreakpoint(): BreakpointConfig {
    const width = window.innerWidth
    return this.breakpoints.find(bp =>
      width >= bp.minWidth && (bp.maxWidth === undefined || width <= bp.maxWidth)
    ) || this.breakpoints[0]
  }

  private initializeResponsiveFeatures(): void {
    // Apply initial responsive CSS
    this.applyResponsiveCSS()

    // Setup mobile-specific features
    if (this.deviceInfo.isMobile) {
      this.setupMobileFeatures()
    }

    // Setup touch-specific features
    if (this.deviceInfo.hasTouch) {
      this.setupTouchFeatures()
    }

    // Setup connection-aware features
    if (this.deviceInfo.connectionSpeed === 'slow') {
      this.setupSlowConnectionFeatures()
    }
  }

  private applyResponsiveCSS(): void {
    const css = `
      :root {
        --current-columns: ${this.currentBreakpoint.columns};
        --current-spacing: ${this.currentBreakpoint.spacing};
        --current-font-size: ${this.currentBreakpoint.fontSize};
        --screen-size: ${this.deviceInfo.screenSize};
      }

      /* Mobile-first responsive utilities */
      .responsive-grid {
        display: grid;
        grid-template-columns: repeat(var(--current-columns), 1fr);
        gap: var(--current-spacing);
      }

      .responsive-text {
        font-size: var(--current-font-size);
      }

      /* Touch optimizations */
      ${this.deviceInfo.hasTouch ? `
        .touch-target {
          min-height: 44px;
          min-width: 44px;
          padding: 12px;
        }

        .touch-feedback {
          transition: transform 0.1s ease;
        }

        .touch-feedback:active {
          transform: scale(0.95);
        }

        /* Larger tap targets on mobile */
        button, .button, [role="button"] {
          min-height: 44px;
          min-width: 44px;
        }

        /* Better scrolling */
        .scroll-area {
          -webkit-overflow-scrolling: touch;
          scroll-behavior: smooth;
        }
      ` : ''}

      /* Mobile-specific styles */
      ${this.deviceInfo.isMobile ? `
        /* Hide complex interactions on mobile */
        .desktop-only {
          display: none !important;
        }

        /* Simplified mobile layouts */
        .mobile-stack {
          flex-direction: column !important;
        }

        .mobile-full-width {
          width: 100% !important;
        }

        /* Safe area handling for mobile */
        .mobile-safe-area {
          padding-top: env(safe-area-inset-top);
          padding-bottom: env(safe-area-inset-bottom);
          padding-left: env(safe-area-inset-left);
          padding-right: env(safe-area-inset-right);
        }
      ` : ''}

      /* Tablet-specific styles */
      ${this.deviceInfo.isTablet ? `
        .tablet-adapt {
          max-width: 768px;
          margin: 0 auto;
        }
      ` : ''}

      /* Connection-aware styles */
      ${this.deviceInfo.connectionSpeed === 'slow' ? `
        /* Disable animations on slow connections */
        *, *::before, *::after {
          animation-duration: 0.01ms !important;
          transition-duration: 0.01ms !important;
        }

        /* Hide non-essential images */
        .decorative-image {
          display: none !important;
        }
      ` : ''}
    `

    this.injectCSS('responsive-core', css)
  }

  private setupMobileFeatures(): void {
    // Prevent zoom on input focus (iOS)
    const viewport = document.querySelector('meta[name="viewport"]')
    if (viewport) {
      viewport.setAttribute('content',
        'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
      )
    }

    // Add mobile-specific classes
    document.body.classList.add('mobile-device')

    // Setup pull-to-refresh prevention on web
    document.body.style.overscrollBehavior = 'none'
  }

  private setupTouchFeatures(): void {
    document.body.classList.add('touch-device')

    // Improve touch scrolling
    const scrollAreas = document.querySelectorAll('.scroll-area')
    scrollAreas.forEach(area => {
      (area as HTMLElement).style.webkitOverflowScrolling = 'touch'
    })
  }

  private setupSlowConnectionFeatures(): void {
    document.body.classList.add('slow-connection')

    // Lazy load images more aggressively
    const images = document.querySelectorAll('img[data-src]')
    images.forEach(img => {
      (img as HTMLElement).style.display = 'none'
    })
  }

  private setupTouchOptimizations(): void {
    if (!this.deviceInfo.hasTouch) return

    // Add touch feedback to interactive elements
    const interactiveElements = document.querySelectorAll(
      'button, .button, [role="button"], [tabindex], input, textarea, select'
    )

    interactiveElements.forEach(element => {
      element.classList.add('touch-feedback')
    })
  }

  // Touch Gesture System
  addTouchGesture(gesture: TouchGesture): void {
    if (!this.deviceInfo.hasTouch) return

    const existing = this.touchGestures.get(gesture.element) || []
    existing.push(gesture)
    this.touchGestures.set(gesture.element, existing)

    this.attachGestureListeners(gesture.element)
  }

  private attachGestureListeners(element: HTMLElement): void {
    let startX = 0, startY = 0, startTime = 0
    let isLongPressing = false
    let longPressTimer: NodeJS.Timeout

    const handleTouchStart = (e: TouchEvent) => {
      const touch = e.touches[0]
      startX = touch.clientX
      startY = touch.clientY
      startTime = Date.now()

      // Setup long press detection
      longPressTimer = setTimeout(() => {
        isLongPressing = true
        this.handleGesture(element, 'long-press', { x: startX, y: startY })
      }, 500)
    }

    const handleTouchMove = (e: TouchEvent) => {
      clearTimeout(longPressTimer)
      isLongPressing = false
    }

    const handleTouchEnd = (e: TouchEvent) => {
      clearTimeout(longPressTimer)

      if (isLongPressing) return

      const touch = e.changedTouches[0]
      const endX = touch.clientX
      const endY = touch.clientY
      const endTime = Date.now()

      const deltaX = endX - startX
      const deltaY = endY - startY
      const deltaTime = endTime - startTime
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)

      // Tap detection
      if (distance < 10 && deltaTime < 300) {
        this.handleGesture(element, 'tap', { x: endX, y: endY })
      }
      // Swipe detection
      else if (distance > 50 && deltaTime < 500) {
        let direction: 'left' | 'right' | 'up' | 'down'

        if (Math.abs(deltaX) > Math.abs(deltaY)) {
          direction = deltaX > 0 ? 'right' : 'left'
        } else {
          direction = deltaY > 0 ? 'down' : 'up'
        }

        this.handleGesture(element, 'swipe', {
          direction,
          distance,
          deltaX,
          deltaY,
          velocity: distance / deltaTime
        })
      }
    }

    element.addEventListener('touchstart', handleTouchStart, { passive: false })
    element.addEventListener('touchmove', handleTouchMove, { passive: false })
    element.addEventListener('touchend', handleTouchEnd, { passive: false })
  }

  private handleGesture(element: HTMLElement, type: string, details: any): void {
    const gestures = this.touchGestures.get(element) || []

    gestures.forEach(gesture => {
      if (gesture.type === type) {
        // Check direction constraints for swipes
        if (type === 'swipe' && gesture.options?.direction) {
          if (gesture.options.direction !== 'any' &&
              gesture.options.direction !== details.direction) {
            return
          }
        }

        gesture.callback(details)
      }
    })
  }

  // Responsive Component Observer
  observeElement(element: HTMLElement, callback: (size: { width: number, height: number }) => void): void {
    if (!this.resizeObserver) return

    element.setAttribute('data-responsive-observed', 'true')
    element.setAttribute('data-responsive-callback', callback.toString())

    this.resizeObserver.observe(element)
  }

  private handleElementResize(element: HTMLElement, rect: DOMRectReadOnly): void {
    const callback = element.getAttribute('data-responsive-callback')
    if (!callback) return

    try {
      const fn = new Function('return ' + callback)()
      fn({ width: rect.width, height: rect.height })
    } catch (error) {
      console.warn('Error executing responsive callback:', error)
    }
  }

  // Utility Methods
  private injectCSS(id: string, css: string): void {
    const existing = document.getElementById(`mobile-responsive-${id}`)
    if (existing) {
      existing.remove()
    }

    const style = document.createElement('style')
    style.id = `mobile-responsive-${id}`
    style.textContent = css
    document.head.appendChild(style)
  }

  // Public API
  getDeviceInfo(): DeviceInfo {
    return { ...this.deviceInfo }
  }

  getCurrentBreakpoint(): BreakpointConfig {
    return { ...this.currentBreakpoint }
  }

  isBreakpoint(name: string): boolean {
    return this.currentBreakpoint.name === name
  }

  isAtLeast(breakpoint: string): boolean {
    const bp = this.breakpoints.find(b => b.name === breakpoint)
    if (!bp) return false
    return window.innerWidth >= bp.minWidth
  }

  isAtMost(breakpoint: string): boolean {
    const bp = this.breakpoints.find(b => b.name === breakpoint)
    if (!bp) return false
    return bp.maxWidth ? window.innerWidth <= bp.maxWidth : false
  }

  subscribe(listener: (info: DeviceInfo) => void): () => void {
    this.listeners.push(listener)
    return () => {
      const index = this.listeners.indexOf(listener)
      if (index > -1) {
        this.listeners.splice(index, 1)
      }
    }
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.deviceInfo))
  }

  // Adaptive loading based on device capabilities
  loadResourceAdaptively(
    resources: {
      mobile?: string
      tablet?: string
      desktop?: string
      slowConnection?: string
    }
  ): string | undefined {
    if (this.deviceInfo.connectionSpeed === 'slow' && resources.slowConnection) {
      return resources.slowConnection
    }

    if (this.deviceInfo.isMobile && resources.mobile) {
      return resources.mobile
    }

    if (this.deviceInfo.isTablet && resources.tablet) {
      return resources.tablet
    }

    if (this.deviceInfo.isDesktop && resources.desktop) {
      return resources.desktop
    }

    return resources.mobile || resources.tablet || resources.desktop
  }
}

export const mobileResponsiveService = new MobileResponsiveService()

import React from 'react'

// React hook
export const useResponsive = () => {
  const [deviceInfo, setDeviceInfo] = React.useState<DeviceInfo>(
    mobileResponsiveService.getDeviceInfo()
  )

  React.useEffect(() => {
    const unsubscribe = mobileResponsiveService.subscribe(setDeviceInfo)
    return unsubscribe
  }, [])

  return {
    ...deviceInfo,
    breakpoint: mobileResponsiveService.getCurrentBreakpoint(),
    isBreakpoint: (name: string) => mobileResponsiveService.isBreakpoint(name),
    isAtLeast: (breakpoint: string) => mobileResponsiveService.isAtLeast(breakpoint),
    isAtMost: (breakpoint: string) => mobileResponsiveService.isAtMost(breakpoint),
    addTouchGesture: (gesture: TouchGesture) => mobileResponsiveService.addTouchGesture(gesture),
    observeElement: (element: HTMLElement, callback: (size: any) => void) =>
      mobileResponsiveService.observeElement(element, callback),
    loadResource: (resources: any) => mobileResponsiveService.loadResourceAdaptively(resources)
  }
}