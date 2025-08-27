/**
 * React hook for managing lock data and operations
 */

import { useState, useEffect, useCallback } from 'react'
import { 
  fetchLocks, 
  fetchStats, 
  removeLock, 
  cleanupStaleLocks, 
  type LockInfo, 
  type LockStats 
} from '@/lib/api'

export interface UseLocks {
  locks: LockInfo[]
  stats: LockStats | null
  isLoading: boolean
  error: string | null
  refreshLocks: () => Promise<void>
  refreshStats: () => Promise<void>
  handleRemoveLock: (filePath: string) => Promise<void>
  handleCleanup: (maxAgeHours?: number) => Promise<void>
}

export function useLocks(): UseLocks {
  const [locks, setLocks] = useState<LockInfo[]>([])
  const [stats, setStats] = useState<LockStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refreshLocks = useCallback(async () => {
    try {
      setError(null)
      const locksData = await fetchLocks()
      setLocks(locksData)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch locks'
      setError(errorMessage)
      console.error('Error refreshing locks:', err)
    }
  }, [])

  const refreshStats = useCallback(async () => {
    try {
      setError(null)
      const statsData = await fetchStats()
      setStats(statsData)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch stats'
      setError(errorMessage)
      console.error('Error refreshing stats:', err)
    }
  }, [])

  const handleRemoveLock = useCallback(async (filePath: string) => {
    try {
      setError(null)
      await removeLock(filePath)
      // Remove the lock from local state immediately for better UX
      setLocks(prev => prev.filter(lock => lock.file_path !== filePath))
      // Refresh both locks and stats to get updated data
      await Promise.all([refreshLocks(), refreshStats()])
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to remove lock'
      setError(errorMessage)
      console.error('Error removing lock:', err)
      // Refresh to ensure UI is in sync with server state
      await refreshLocks()
    }
  }, [refreshLocks, refreshStats])

  const handleCleanup = useCallback(async (maxAgeHours: number = 24) => {
    try {
      setError(null)
      const result = await cleanupStaleLocks(maxAgeHours)
      console.log(`Cleaned up ${result.removed_count} stale locks`)
      // Refresh both locks and stats after cleanup
      await Promise.all([refreshLocks(), refreshStats()])
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to cleanup locks'
      setError(errorMessage)
      console.error('Error cleaning up locks:', err)
      throw err
    }
  }, [refreshLocks, refreshStats])

  // Initial load
  useEffect(() => {
    const loadInitialData = async () => {
      setIsLoading(true)
      try {
        await Promise.all([refreshLocks(), refreshStats()])
      } catch (err) {
        console.error('Error loading initial data:', err)
      } finally {
        setIsLoading(false)
      }
    }

    loadInitialData()
  }, [refreshLocks, refreshStats])

  // Set up periodic refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refreshLocks()
      refreshStats()
    }, 30000) // 30 seconds

    return () => clearInterval(interval)
  }, [refreshLocks, refreshStats])

  return {
    locks,
    stats,
    isLoading,
    error,
    refreshLocks,
    refreshStats,
    handleRemoveLock,
    handleCleanup,
  }
}