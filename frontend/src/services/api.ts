import axios from 'axios';

import { API_BASE_URL } from '@/config';

// Create Axios Instance
const api = axios.create({
    baseURL: API_BASE_URL, // Backend URL
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Types
export interface DashboardKPI {
    total_spend: number;
    total_plans: number;
    currency: string;
}

export interface ActivityItem {
    id: string;
    sku_id: string;
    order_id: string;
    status: string;
    amount: number;
    currency: string;
    date: string;
}

export interface PurchasePlan {
    id: number;
    plan_date: string;
    sku_id: string;
    vendor_id: string;
    suggested_quantity: number;
    final_quantity: number;
    total_amount: number;
    status: string;
    notes: string;
}

export const DashboardService = {
    getSpendingAnalytics: async () => {
        try {
            const response = await api.get('/api/dashboard/spending');
            return response.data;
        } catch (error) {
            console.error('Error fetching spending analytics:', error);
            throw error;
        }
    },

    getRecentActivity: async () => {
        try {
            const response = await api.get('/api/dashboard/recent-activity');
            return response.data; // Expected { status: 'success', data: [...] }
        } catch (error) {
            console.error('Error fetching recent activity:', error);
            // Return empty structure on error to prevent UI crash
            return { status: 'error', data: [] };
        }
    }
};

export const PlanningService = {
    getPlans: async () => {
        try {
            const response = await api.get('/api/planning/plans');
            return response.data; // Expected { status: 'success', data: [...] }
        } catch (error) {
            console.error('Error fetching plans:', error);
            return { status: 'error', data: [] };
        }
    },

    generatePlans: async () => {
        try {
            const response = await api.post('/api/planning/generate-plans');
            return response.data;
        } catch (error) {
            console.error('Error generating plans:', error);
            throw error;
        }
    }
};

export default api;
