'use client'

import { useEffect, useRef, useState } from 'react'

/**
 * 👆 useSwipeGesture Hook
 *
 * Features:
 * - Touch gesture detection for swipe navigation
 * - Configurable swipe threshold and velocity
 * - Support for horizontal and vertical swipes
 * - Mobile-optimized with proper touch handling
 */

interface SwipeGestureOptions {
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
  onSwipeUp?: () => void
  onSwipeDown?: () => void
  threshold?: number // Minimum distance for swipe
  velocityThreshold?: number // Minimum velocity for swipe
  preventScroll?: boolean // Prevent default scroll behavior
}

interface TouchPosition {
  x: number
  y: number
  time: number
}

export function useSwipeGesture(options: SwipeGestureOptions) {
  const {
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown,
    threshold = 50,
    velocityThreshold = 0.3,
    preventScroll = false
  } = options

  const [touchStart, setTouchStart] = useState<TouchPosition | null>(null)
  const [touchEnd, setTouchEnd] = useState<TouchPosition | null>(null)
  const elementRef = useRef<HTMLElement | null>(null)

  // Handle touch start
  const onTouchStart = (e: TouchEvent) => {
    const touch = e.targetTouches[0]
    setTouchStart({
      x: touch.clientX,
      y: touch.clientY,
      time: Date.now()
    })
    setTouchEnd(null)
  }

  // Handle touch move
  const onTouchMove = (e: TouchEvent) => {
    if (preventScroll) {
      e.preventDefault()
    }
  }

  // Handle touch end
  const onTouchEnd = (e: TouchEvent) => {
    const touch = e.changedTouches[0]
    setTouchEnd({
      x: touch.clientX,
      y: touch.clientY,
      time: Date.now()
    })
  }

  // Process swipe gesture
  useEffect(() => {
    if (!touchStart || !touchEnd) return

    const deltaX = touchEnd.x - touchStart.x
    const deltaY = touchEnd.y - touchStart.y
    const deltaTime = touchEnd.time - touchStart.time

    const distanceX = Math.abs(deltaX)
    const distanceY = Math.abs(deltaY)
    const velocity = Math.max(distanceX, distanceY) / deltaTime

    // Check if gesture meets threshold requirements
    if (Math.max(distanceX, distanceY) < threshold || velocity < velocityThreshold) {
      return
    }

    // Determine swipe direction (prioritize the axis with greater movement)
    if (distanceX > distanceY) {
      // Horizontal swipe
      if (deltaX > 0 && onSwipeRight) {
        onSwipeRight()
      } else if (deltaX < 0 && onSwipeLeft) {
        onSwipeLeft()
      }
    } else {
      // Vertical swipe
      if (deltaY > 0 && onSwipeDown) {
        onSwipeDown()
      } else if (deltaY < 0 && onSwipeUp) {
        onSwipeUp()
      }
    }
  }, [touchStart, touchEnd, threshold, velocityThreshold, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown])

  // Attach event listeners
  useEffect(() => {
    const element = elementRef.current
    if (!element) return

    // Add touch event listeners
    element.addEventListener('touchstart', onTouchStart, { passive: !preventScroll })
    element.addEventListener('touchmove', onTouchMove, { passive: !preventScroll })
    element.addEventListener('touchend', onTouchEnd, { passive: true })

    // Cleanup
    return () => {
      element.removeEventListener('touchstart', onTouchStart)
      element.removeEventListener('touchmove', onTouchMove)
      element.removeEventListener('touchend', onTouchEnd)
    }
  }, [preventScroll])

  return {
    ref: elementRef,
    isActive: touchStart !== null,
    swipeData: {
      start: touchStart,
      end: touchEnd,
      deltaX: touchStart && touchEnd ? touchEnd.x - touchStart.x : 0,
      deltaY: touchStart && touchEnd ? touchEnd.y - touchStart.y : 0
    }
  }
}