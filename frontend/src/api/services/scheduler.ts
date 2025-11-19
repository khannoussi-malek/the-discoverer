/**
 * Scheduler API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'

export interface ScheduledQuery {
  id: string
  name: string
  description?: string
  query: string
  database_ids?: string[]
  schedule: string // Cron expression
  frequency?: string
  status?: string // 'active' | 'paused' | 'completed'
  enabled?: boolean // Derived from status
  last_run?: string
  last_run_at?: string
  next_run?: string
  next_run_at?: string
  run_count?: number
  success_count?: number
  failure_count?: number
  created_at?: string
  updated_at?: string
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const schedulerService = {
  /**
   * List all scheduled queries
   */
  listSchedules: async (): Promise<ScheduledQuery[]> => {
    const response = await apiClient.get<PaginatedResponse<ScheduledQuery>>(API_ENDPOINTS.SCHEDULER.LIST)
    // Backend returns paginated response, extract items array and map enabled from status
    const items = response.data.items || []
    return items.map(item => ({
      ...item,
      enabled: item.status === 'active' || item.enabled === true,
      last_run: item.last_run_at,
      next_run: item.next_run_at,
    }))
  },

  /**
   * Get schedule by ID
   * Note: Backend doesn't have a GET endpoint for individual schedules,
   * so we fetch all and filter by ID
   */
  getSchedule: async (id: string): Promise<ScheduledQuery> => {
    const schedules = await schedulerService.listSchedules()
    const schedule = schedules.find(s => s.id === id)
    if (!schedule) {
      throw new Error(`Schedule with id ${id} not found`)
    }
    return schedule
  },

  /**
   * Create a new schedule
   */
  createSchedule: async (schedule: Omit<ScheduledQuery, 'id' | 'created_at' | 'updated_at' | 'last_run' | 'next_run' | 'last_run_at' | 'next_run_at' | 'run_count' | 'success_count' | 'failure_count' | 'status'>): Promise<ScheduledQuery> => {
    const response = await apiClient.post<ScheduledQuery>(API_ENDPOINTS.SCHEDULER.CREATE, {
      name: schedule.name,
      query: schedule.query,
      schedule: schedule.schedule,
      frequency: schedule.frequency || 'daily',
      database_ids: schedule.database_ids,
      description: schedule.description,
      parameters: undefined,
    })
    const result = response.data
    return {
      ...result,
      enabled: result.status === 'active' || result.enabled === true,
      last_run: result.last_run_at,
      next_run: result.next_run_at,
    }
  },

  /**
   * Update schedule
   * Note: Backend doesn't support updates, this will throw an error
   */
  updateSchedule: async (_id: string, _schedule: Partial<ScheduledQuery>): Promise<ScheduledQuery> => {
    throw new Error('Update schedule is not supported by the backend API. Delete and recreate the schedule instead.')
  },

  /**
   * Delete schedule
   */
  deleteSchedule: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.SCHEDULER.DELETE(id))
  },

  /**
   * Resume schedule (enable)
   */
  enableSchedule: async (id: string): Promise<ScheduledQuery> => {
    await apiClient.post<{ message: string }>(API_ENDPOINTS.SCHEDULER.RESUME(id))
    // Resume returns a message, so we need to refetch the schedule
    return schedulerService.getSchedule(id)
  },

  /**
   * Pause schedule (disable)
   */
  disableSchedule: async (id: string): Promise<ScheduledQuery> => {
    await apiClient.post<{ message: string }>(API_ENDPOINTS.SCHEDULER.PAUSE(id))
    // Pause returns a message, so we need to refetch the schedule
    return schedulerService.getSchedule(id)
  },
}

