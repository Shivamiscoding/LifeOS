import api from './api';
import type { Task, CreateTaskPayload, UpdateTaskPayload, TaskFilters, PaginatedResponse } from '../types';

export const tasksService = {
  list: (filters?: TaskFilters) =>
    api.get<PaginatedResponse<Task>>('/tasks/', { params: filters }).then((r) => r.data),

  get: (id: string) => api.get<Task>(`/tasks/${id}/`).then((r) => r.data),

  create: (payload: CreateTaskPayload) =>
    api.post<Task>('/tasks/', payload).then((r) => r.data),

  update: ({ id, ...payload }: UpdateTaskPayload) =>
    api.patch<Task>(`/tasks/${id}/`, payload).then((r) => r.data),

  delete: (id: string) => api.delete(`/tasks/${id}/`),

  bulkUpdateStatus: (ids: string[], status: Task['status']) =>
    api.post('/tasks/bulk-status/', { ids, status }).then((r) => r.data),
};
