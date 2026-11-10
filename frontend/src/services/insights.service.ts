import api from './api';
import type { DashboardStats, InsightsData } from '../types';

export const insightsService = {
  dashboardStats: () => api.get<DashboardStats>('/insights/stats/').then((r) => r.data),

  insights: (startDate?: string, endDate?: string) =>
    api
      .get<InsightsData>('/insights/', { params: { start: startDate, end: endDate } })
      .then((r) => r.data),
};
