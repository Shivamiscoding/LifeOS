import api from './api';
import type { AISession, SendCommandPayload, PaginatedResponse } from '../types';

export const aiService = {
  sendCommand: (payload: SendCommandPayload) =>
    api.post<AISession>('/ai/command/', payload).then((r) => r.data),

  getSessions: () =>
    api.get<PaginatedResponse<AISession>>('/ai/sessions/').then((r) => r.data),

  getSession: (id: string) => api.get<AISession>(`/ai/sessions/${id}/`).then((r) => r.data),

  pollSession: (id: string) =>
    api.get<AISession>(`/ai/sessions/${id}/status/`).then((r) => r.data),
};
