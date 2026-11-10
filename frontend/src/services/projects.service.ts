import api from './api';
import type { Project, CreateProjectPayload, PaginatedResponse } from '../types';

export const projectsService = {
  list: () => api.get<PaginatedResponse<Project>>('/projects/').then((r) => r.data),

  get: (id: string) => api.get<Project>(`/projects/${id}/`).then((r) => r.data),

  create: (payload: CreateProjectPayload) =>
    api.post<Project>('/projects/', payload).then((r) => r.data),

  update: (id: string, payload: Partial<CreateProjectPayload>) =>
    api.patch<Project>(`/projects/${id}/`, payload).then((r) => r.data),

  delete: (id: string) => api.delete(`/projects/${id}/`),
};
