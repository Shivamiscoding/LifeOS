import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { projectsService } from '../services/projects.service';
import type { CreateProjectPayload } from '../types';

export const PROJECTS_KEY = 'projects';

export function useProjects() {
  return useQuery({ queryKey: [PROJECTS_KEY], queryFn: () => projectsService.list() });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: [PROJECTS_KEY, id],
    queryFn: () => projectsService.get(id),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateProjectPayload) => projectsService.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [PROJECTS_KEY] }),
  });
}

export function useUpdateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<CreateProjectPayload> }) =>
      projectsService.update(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [PROJECTS_KEY] }),
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => projectsService.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: [PROJECTS_KEY] }),
  });
}
