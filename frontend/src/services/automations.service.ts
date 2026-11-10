import api from './api';
import type { Automation, CreateAutomationPayload, ExecutionLog, PaginatedResponse } from '../types';

export const automationsService = {
  list: () => api.get<PaginatedResponse<Automation>>('/automations/').then((r) => r.data),

  get: (id: string) => api.get<Automation>(`/automations/${id}/`).then((r) => r.data),

  create: (payload: CreateAutomationPayload) =>
    api.post<Automation>('/automations/', payload).then((r) => r.data),

  update: (id: string, payload: Partial<CreateAutomationPayload> & { isActive?: boolean }) =>
    api.patch<Automation>(`/automations/${id}/`, payload).then((r) => r.data),

  delete: (id: string) => api.delete(`/automations/${id}/`),

  execute: (id: string) =>
    api.post<ExecutionLog>(`/automations/${id}/execute/`).then((r) => r.data),

  history: (id: string) =>
    api.get<PaginatedResponse<ExecutionLog>>(`/automations/${id}/history/`).then((r) => r.data),
};
