/**
 * Sound Notification Service
 * Provides subtle audio feedback for toast notifications
 * Enterprise-grade with user preferences and accessibility support
 */

export interface SoundSettings {
  enabled: boolean
  volume: number // 0.0 to 1.0
  respectReducedMotion: boolean
}

class SoundNotificationService {
  private settings: SoundSettings = {
    enabled: true,
    volume: 0.3,
    respectReducedMotion: true
  }

  // Simple sound patterns using Web Audio API
  private audioContext: AudioContext | null = null
  private soundCache: Map<string, AudioBuffer> = new Map()

  constructor() {
    this.loadSettings()
    this.initAudioContext()
  }

  private loadSettings(): void {
    if (typeof window === 'undefined') return

    try {
      const saved = localStorage.getItem('streamworks-sound-settings')
      if (saved) {
        this.settings = { ...this.settings, ...JSON.parse(saved) }
      }
    } catch (error) {
      console.warn('Failed to load sound settings:', error)
    }
  }

  private saveSettings(): void {
    if (typeof window === 'undefined') return

    try {
      localStorage.setItem('streamworks-sound-settings', JSON.stringify(this.settings))
    } catch (error) {
      console.warn('Failed to save sound settings:', error)
    }
  }

  private initAudioContext(): void {
    if (typeof window === 'undefined') return

    try {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    } catch (error) {
      console.warn('Web Audio API not supported:', error)
    }
  }

  private shouldPlaySound(): boolean {
    if (!this.settings.enabled || !this.audioContext) return false

    // Respect user's reduced motion preference
    if (this.settings.respectReducedMotion &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return false
    }

    return true
  }

  private async createTone(frequency: number, duration: number, volume: number = 0.3): Promise<void> {
    if (!this.audioContext || !this.shouldPlaySound()) return

    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(this.audioContext.destination)

    // Configure oscillator
    oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime)
    oscillator.type = 'sine'

    // Configure envelope (fade in/out)
    const now = this.audioContext.currentTime
    gainNode.gain.setValueAtTime(0, now)
    gainNode.gain.linearRampToValueAtTime(volume * this.settings.volume, now + 0.01)
    gainNode.gain.linearRampToValueAtTime(0, now + duration)

    // Play
    oscillator.start(now)
    oscillator.stop(now + duration)
  }

  private async playChord(frequencies: number[], duration: number, volume: number = 0.2): Promise<void> {
    if (!this.shouldPlaySound()) return

    const promises = frequencies.map(freq =>
      this.createTone(freq, duration, volume / frequencies.length)
    )

    await Promise.all(promises)
  }

  // Sound patterns for different notification types
  async playSuccess(): Promise<void> {
    // Pleasant ascending chord (C major)
    await this.playChord([523.25, 659.25, 783.99], 0.3, 0.2)
  }

  async playError(): Promise<void> {
    // More attention-grabbing but not harsh (minor chord)
    await this.playChord([440, 523.25, 622.25], 0.4, 0.25)
  }

  async playWarning(): Promise<void> {
    // Neutral tone
    await this.createTone(659.25, 0.2, 0.2)
  }

  async playInfo(): Promise<void> {
    // Soft, subtle tone
    await this.createTone(523.25, 0.15, 0.15)
  }

  async playLoading(): Promise<void> {
    // Very subtle ascending notes
    if (!this.shouldPlaySound()) return

    const notes = [523.25, 587.33, 659.25]
    for (let i = 0; i < notes.length; i++) {
      setTimeout(() => this.createTone(notes[i], 0.1, 0.1), i * 50)
    }
  }

  // Settings management
  updateSettings(newSettings: Partial<SoundSettings>): void {
    this.settings = { ...this.settings, ...newSettings }
    this.saveSettings()
  }

  getSettings(): SoundSettings {
    return { ...this.settings }
  }

  setEnabled(enabled: boolean): void {
    this.updateSettings({ enabled })
  }

  setVolume(volume: number): void {
    const clampedVolume = Math.max(0, Math.min(1, volume))
    this.updateSettings({ volume: clampedVolume })
  }

  // Test sound for settings
  async testSound(): Promise<void> {
    await this.playSuccess()
  }
}

// Export singleton
export const soundNotificationService = new SoundNotificationService()

/**
 * React hook for sound notifications
 */
import { useState, useCallback } from 'react'

export function useSoundNotifications() {
  const [settings, setSettings] = useState(soundNotificationService.getSettings())

  const updateSettings = useCallback((newSettings: Partial<SoundSettings>) => {
    soundNotificationService.updateSettings(newSettings)
    setSettings(soundNotificationService.getSettings())
  }, [])

  const playSound = useCallback(async (type: 'success' | 'error' | 'warning' | 'info' | 'loading') => {
    switch (type) {
      case 'success':
        return soundNotificationService.playSuccess()
      case 'error':
        return soundNotificationService.playError()
      case 'warning':
        return soundNotificationService.playWarning()
      case 'info':
        return soundNotificationService.playInfo()
      case 'loading':
        return soundNotificationService.playLoading()
    }
  }, [])

  return {
    settings,
    updateSettings,
    playSound,
    testSound: soundNotificationService.testSound.bind(soundNotificationService)
  }
}