import api from './api';
import type { FileDocument, PaginatedResponse } from '../types';

export const filesService = {
  list: (mimeType?: string) =>
    api
      .get<PaginatedResponse<FileDocument>>('/files/', { params: { mime_type: mimeType } })
      .then((r) => r.data),

  upload: (file: File, onProgress?: (pct: number) => void) => {
    const form = new FormData();
    form.append('file', file);
    return api
      .post<FileDocument>('/files/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
        },
      })
      .then((r) => r.data);
  },

  delete: (id: string) => api.delete(`/files/${id}/`),

  summarize: (id: string) =>
    api.post<{ summary: string }>(`/files/${id}/summarize/`).then((r) => r.data),
};
