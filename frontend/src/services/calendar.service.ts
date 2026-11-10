import api from './api';
import type { CalendarEvent, CreateEventPayload, PaginatedResponse } from '../types';

export const calendarService = {
  list: (startDate?: string, endDate?: string) =>
    api
      .get<PaginatedResponse<CalendarEvent>>('/calendar/', { params: { start: startDate, end: endDate } })
      .then((r) => r.data),

  get: (id: string) => api.get<CalendarEvent>(`/calendar/${id}/`).then((r) => r.data),

  create: (payload: CreateEventPayload) =>
    api.post<CalendarEvent>('/calendar/', payload).then((r) => r.data),

  update: (id: string, payload: Partial<CreateEventPayload>) =>
    api.patch<CalendarEvent>(`/calendar/${id}/`, payload).then((r) => r.data),

  delete: (id: string) => api.delete(`/calendar/${id}/`),
};
