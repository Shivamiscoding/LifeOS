import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { calendarService } from '../services/calendar.service';
import type { CreateEventPayload } from '../types';

export const CALENDAR_KEY = 'calendar';

export function useCalendarEvents(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: [CALENDAR_KEY, startDate, endDate],
    queryFn: () => calendarService.list(startDate, endDate),
  });
}

export function useCreateEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateEventPayload) => calendarService.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [CALENDAR_KEY] }),
  });
}

export function useUpdateEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<CreateEventPayload> }) =>
      calendarService.update(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [CALENDAR_KEY] }),
  });
}

export function useDeleteEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => calendarService.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [CALENDAR_KEY] }),
  });
}
