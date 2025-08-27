/**
 * API service for Nova backend integration
 * Handles all communication with the Flask backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'

export interface LockInfo {
  file_path: string
  user_name: string
  computer_name: string
  lock_time: string
  process_id?: number
  lock_id?: string
}

export interface LockStats {
  total_locks: number
  unique_users: number
  unique_computers: number
  extensions: Record<string, number>
  users: string[]
  computers: string[]
}

export interface CleanupResult {
  message: string
  removed_count: number
}

/**
 * Fetch all active locks
 */
export async function fetchLocks(): Promise<LockInfo[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/locks`)
    if (!response.ok) {
      throw new Error(`Failed to fetch locks: ${response.statusText}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching locks:', error)
    throw error
  }
}

/**
 * Fetch lock statistics
 */
export async function fetchStats(): Promise<LockStats> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stats`)
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching stats:', error)
    throw error
  }
}

/**
 * Remove a specific lock
 */
export async function removeLock(filePath: string, userName: string = 'admin'): Promise<void> {
  try {
    const url = `${API_BASE_URL}/api/locks/${encodeURIComponent(filePath)}?user_name=${encodeURIComponent(userName)}`
    const response = await fetch(url, {
      method: 'DELETE',
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || `Failed to remove lock: ${response.statusText}`)
    }
  } catch (error) {
    console.error('Error removing lock:', error)
    throw error
  }
}

/**
 * Clean up stale locks
 */
export async function cleanupStaleLocks(maxAgeHours: number = 24): Promise<CleanupResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/cleanup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ max_age_hours: maxAgeHours }),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to cleanup locks: ${response.statusText}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error cleaning up locks:', error)
    throw error
  }
}

/**
 * Get lock information for a specific file
 */
export async function getLock(filePath: string): Promise<LockInfo | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/locks/${encodeURIComponent(filePath)}`)
    
    if (response.status === 404) {
      return null // File not locked
    }
    
    if (!response.ok) {
      throw new Error(`Failed to get lock: ${response.statusText}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error getting lock:', error)
    throw error
  }
}

/**
 * Create a WebSocket connection for real-time updates
 */
export function createWebSocket(onMessage: (event: MessageEvent) => void): WebSocket | null {
  try {
    const wsUrl = API_BASE_URL.replace('http', 'ws')
    const socket = new WebSocket(`${wsUrl}/socket.io/?EIO=4&transport=websocket`)
    
    socket.onmessage = onMessage
    
    socket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    return socket
  } catch (error) {
    console.error('Failed to create WebSocket connection:', error)
    return null
  }
}