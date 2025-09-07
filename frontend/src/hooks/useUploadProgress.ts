/**
 * Simple Upload Progress Hook - Dedicated WebSocket connection for upload progress only
 * No dependencies on DocumentStore or other complex systems
 */

import { useState, useEffect, useCallback, useRef } from 'react'

export interface UploadProgressData {
  job_id: string
  progress: number // 0-100
  stage: string
  status: 'uploading' | 'analyzing' | 'processing' | 'completed' | 'error'
  error?: string
}

interface UseUploadProgressReturn {
  connect: (jobId: string) => void
  disconnect: (jobId: string) => void
  getProgress: (jobId: string) => UploadProgressData | null
  isConnected: (jobId: string) => boolean
}

export function useUploadProgress(): UseUploadProgressReturn {
  const [progressData, setProgressData] = useState<Map<string, UploadProgressData>>(new Map())
  const [connections, setConnections] = useState<Map<string, WebSocket>>(new Map())
  const progressDataRef = useRef(progressData)
  const connectionsRef = useRef(connections)

  // Keep refs updated
  useEffect(() => {
    progressDataRef.current = progressData
  }, [progressData])

  useEffect(() => {
    connectionsRef.current = connections
  }, [connections])

  const connect = useCallback((jobId: string) => {
    // Don't create duplicate connections
    if (connectionsRef.current.has(jobId)) {
      console.log(`Upload progress already connected for job: ${jobId}`)
      return
    }

    const wsUrl = `ws://localhost:8000/ws/upload-progress/${jobId}`
    console.log(`Connecting to upload progress WebSocket: ${wsUrl}`)

    try {
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log(`Upload progress connected for job: ${jobId}`)
        setConnections(prev => new Map(prev).set(jobId, ws))
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as UploadProgressData
          console.log(`Upload progress received for ${jobId}:`, data)
          
          setProgressData(prev => new Map(prev).set(jobId, data))
          
          // Auto-disconnect when completed or error
          if (data.status === 'completed' || data.status === 'error') {
            setTimeout(() => {
              disconnect(jobId)
            }, 5000) // Keep showing final state for 5 seconds
          }
        } catch (error) {
          console.error(`Failed to parse upload progress message for ${jobId}:`, error)
        }
      }

      ws.onclose = (event) => {
        console.log(`Upload progress WebSocket closed for job: ${jobId}`, event.code, event.reason)
        setConnections(prev => {
          const newMap = new Map(prev)
          newMap.delete(jobId)
          return newMap
        })
      }

      ws.onerror = (error) => {
        console.error(`Upload progress WebSocket error for job: ${jobId}:`, error)
        setConnections(prev => {
          const newMap = new Map(prev)
          newMap.delete(jobId)
          return newMap
        })
      }

    } catch (error) {
      console.error(`Failed to create upload progress WebSocket for job: ${jobId}:`, error)
    }
  }, [])

  const disconnect = useCallback((jobId: string) => {
    const ws = connectionsRef.current.get(jobId)
    if (ws) {
      console.log(`Disconnecting upload progress for job: ${jobId}`)
      ws.close(1000, 'Manual disconnect')
    }
    
    setConnections(prev => {
      const newMap = new Map(prev)
      newMap.delete(jobId)
      return newMap
    })
    
    // Keep progress data for a bit longer for display purposes
    setTimeout(() => {
      setProgressData(prev => {
        const newMap = new Map(prev)
        newMap.delete(jobId)
        return newMap
      })
    }, 1000)
  }, [])

  const getProgress = useCallback((jobId: string): UploadProgressData | null => {
    return progressDataRef.current.get(jobId) || null
  }, [])

  const isConnected = useCallback((jobId: string): boolean => {
    const ws = connectionsRef.current.get(jobId)
    return ws ? ws.readyState === WebSocket.OPEN : false
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      connectionsRef.current.forEach((ws, jobId) => {
        console.log(`Cleaning up upload progress connection for: ${jobId}`)
        ws.close()
      })
    }
  }, [])

  return {
    connect,
    disconnect,
    getProgress,
    isConnected
  }
}