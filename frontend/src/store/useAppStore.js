import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAppStore = create(
  persist(
    (set) => ({
      currentDataset: null,
      qualityMetrics: null,
      anomalyResults: null,
      recommendations: null,
      dashboardData: null,  // Add this
      loading: false,
      error: null,
      
      setCurrentDataset: (dataset) => set({ currentDataset: dataset }),
      setQualityMetrics: (metrics) => set({ qualityMetrics: metrics }),
      setAnomalyResults: (results) => set({ anomalyResults: results }),
      setRecommendations: (recs) => set({ recommendations: recs }),
      setDashboardData: (data) => set({ dashboardData: data }),  // Add this
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      
      reset: () => set({
        currentDataset: null,
        qualityMetrics: null,
        anomalyResults: null,
        recommendations: null,
        dashboardData: null,  // Add this
        loading: false,
        error: null,
      }),
    }),
    {
      name: 'app-storage', // Storage key name
      partialize: (state) => ({
        currentDataset: state.currentDataset,
        qualityMetrics: state.qualityMetrics,
        anomalyResults: state.anomalyResults,
        recommendations: state.recommendations,
        dashboardData: state.dashboardData,  // Add this
      }),
    }
  )
);

export default useAppStore;
