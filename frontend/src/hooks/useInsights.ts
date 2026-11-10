import { useQuery } from '@tanstack/react-query';
import { insightsService } from '../services/insights.service';

export const INSIGHTS_KEY = 'insights';

export function useDashboardStats() {
  return useQuery({ queryKey: [INSIGHTS_KEY, 'stats'], queryFn: insightsService.dashboardStats });
}

export function useInsights(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: [INSIGHTS_KEY, startDate, endDate],
    queryFn: () => insightsService.insights(startDate, endDate),
  });
}
