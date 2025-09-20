/**
 * WebSocket Upload Hook for Real-time Progress Tracking
 * Connects to backend WebSocket for upload progress updates
 */

import { useState, useRef, useCallback, useEffect } from 'react'
import { v4 as uuidv4 } from 'uuid'

interface UploadProgress {
  job_id: string
  filename: string
  file_size_bytes: number
  status: string
  progress_percentage: number
  current_stage: string
  stage_details: string
  current_stage_index: number
  total_stages: number
  chunk_count: number
  processed_bytes: number
  error_message?: string
  estimated_completion?: string
}

interface WebSocketMessage {
  type: string
  job_id: string
  timestamp: string
  data?: UploadProgress | any
  message?: string
}

interface UseWebSocketUploadOptions {
  onProgress?: (progress: UploadProgress) => void
  onComplete?: (jobId: string, success: boolean, documentId?: string, error?: string) => void
  onError?: (error: string) => void
}

export const useWebSocketUpload = (options: UseWebSocketUploadOptions = {}) => {
  const [connections, setConnections] = useState<Map<string, WebSocket>>(new Map())
  const [activeJobs, setActiveJobs] = useState<Map<string, UploadProgress>>(new Map())
  const [isConnecting, setIsConnecting] = useState(false)
  const connectionsRef = useRef(connections)
  const activeJobsRef = useRef(activeJobs)

  // Update refs when state changes
  useEffect(() => {
    connectionsRef.current = connections
  }, [connections])

  useEffect(() => {
    activeJobsRef.current = activeJobs
  }, [activeJobs])

  const createWebSocketConnection = useCallback((jobId: string): Promise<WebSocket> => {
    return new Promise((resolve, reject) => {
      try {
        const ws = new WebSocket(`ws://localhost:8000/ws/upload-progress/${jobId}`)
        
        ws.onopen = () => {
          console.log(`WebSocket connected for job ${jobId}`)
          setConnections(prev => new Map(prev).set(jobId, ws))
          resolve(ws)
        }

        ws.onmessage = (event) => {
          try {
            const progressData = JSON.parse(event.data)
            console.log(`WebSocket progress data for ${jobId}:`, progressData)

            // Direct progress data from upload_progress_websocket.py
            if (progressData.job_id && progressData.progress !== undefined) {
              const progress: UploadProgress = {
                job_id: progressData.job_id,
                filename: progressData.filename || '',
                file_size_bytes: progressData.file_size_bytes || 0,
                status: progressData.status || 'uploading',
                progress_percentage: Math.round(progressData.progress || 0),
                current_stage: progressData.stage || 'Hochladen...',
                stage_details: progressData.stage_details || '',
                current_stage_index: 0,
                total_stages: 3,
                chunk_count: 0,
                processed_bytes: 0,
                error_message: progressData.error,
                estimated_completion: ''
              }
              
              setActiveJobs(prev => new Map(prev).set(jobId, progress))
              options.onProgress?.(progress)

              // Check for completion and auto-disconnect
              if (progressData.status === 'ready') {
                setTimeout(() => {
                  options.onComplete?.(jobId, true, progressData.document_id, undefined)
                  // Auto-disconnect after successful completion
                  setTimeout(() => {
                    const ws = connectionsRef.current.get(jobId)
                    if (ws) {
                      ws.close()
                    }
                  }, 1000)
                }, 100)
              } else if (progressData.status === 'error') {
                options.onComplete?.(jobId, false, undefined, progressData.error)
                // Auto-disconnect after error
                setTimeout(() => {
                  const ws = connectionsRef.current.get(jobId)
                  if (ws) {
                    ws.close()
                  }
                }, 1000)
              }
            }
          } catch (error) {
            console.error('Failed to parse WebSocket progress data:', error)
          }
        }

        ws.onerror = (error) => {
          console.error(`WebSocket error for job ${jobId}:`, error)
          options.onError?.(`WebSocket connection error for ${jobId}`)
          reject(error)
        }

        ws.onclose = (event) => {
          console.log(`WebSocket closed for job ${jobId}`, event.code, event.reason)
          setConnections(prev => {
            const newMap = new Map(prev)
            newMap.delete(jobId)
            return newMap
          })
          setActiveJobs(prev => {
            const newMap = new Map(prev)
            newMap.delete(jobId)
            return newMap
          })
        }

      } catch (error) {
        console.error(`Failed to create WebSocket for ${jobId}:`, error)
        reject(error)
      }
    })
  }, [options])

  const connectToJob = useCallback(async (jobId: string): Promise<WebSocket | null> => {
    if (connections.has(jobId)) {
      return connections.get(jobId)!
    }

    setIsConnecting(true)
    try {
      const ws = await createWebSocketConnection(jobId)
      return ws
    } catch (error) {
      console.error(`Failed to connect to WebSocket for ${jobId}:`, error)
      return null
    } finally {
      setIsConnecting(false)
    }
  }, [connections, createWebSocketConnection])

  const disconnectJob = useCallback((jobId: string) => {
    const ws = connections.get(jobId)
    if (ws) {
      ws.close()
      setConnections(prev => {
        const newMap = new Map(prev)
        newMap.delete(jobId)
        return newMap
      })
    }
  }, [connections])

  const sendMessage = useCallback((jobId: string, message: any) => {
    const ws = connections.get(jobId)
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message))
    }
  }, [connections])

  const ping = useCallback((jobId: string) => {
    sendMessage(jobId, { type: 'ping' })
  }, [sendMessage])

  const requestStatus = useCallback((jobId: string) => {
    sendMessage(jobId, { type: 'status_request' })
  }, [sendMessage])

  const getJobProgress = useCallback((jobId: string): UploadProgress | null => {
    return activeJobs.get(jobId) || null
  }, [activeJobs])

  const getAllActiveJobs = useCallback((): UploadProgress[] => {
    return Array.from(activeJobs.values())
  }, [activeJobs])

  const generateJobId = useCallback((): string => {
    return `upload_${uuidv4()}`
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Close all connections
      connectionsRef.current.forEach((ws) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close()
        }
      })
    }
  }, [])

  return {
    connectToJob,
    disconnectJob,
    ping,
    requestStatus,
    getJobProgress,
    getAllActiveJobs,
    generateJobId,
    isConnecting,
    activeJobs: Array.from(activeJobs.values()),
    connectionCount: connections.size
  }
}