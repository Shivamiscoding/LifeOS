import api from './api';
import type { User } from '../types';

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload { name: string; email: string; password: string }
export interface AuthResponse { access: string; refresh?: string; user: User }

export const authService = {
  login: (payload: LoginPayload) =>
    api.post<AuthResponse>('/auth/login/', payload).then((r) => r.data),

  register: (payload: RegisterPayload) =>
    api.post<AuthResponse>('/auth/register/', payload).then((r) => r.data),

  getMe: () => api.get<User>('/auth/me/').then((r) => r.data),

  updateMe: (payload: Partial<Pick<User, 'name' | 'timezone'>>) =>
    api.patch<User>('/auth/me/', payload).then((r) => r.data),

  changePassword: (payload: { oldPassword: string; newPassword: string }) =>
    api.post('/auth/change-password/', payload).then((r) => r.data),

  logout: () => api.post('/auth/logout/').then((r) => r.data),
};
