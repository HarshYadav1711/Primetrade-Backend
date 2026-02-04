/**
 * API Service Module
 * ==================
 * Centralized Axios instance for all API calls.
 * 
 * Features:
 * - Base URL configuration for backend
 * - Automatic JWT token injection via interceptors
 * - Response error handling
 * - API versioning support (/api/v1)
 */

import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
    // In development, we use Vite's proxy (/api -> localhost:8000)
    // In production, this would point to the actual API server
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - Add auth token to requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor - Handle common errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle 401 Unauthorized - Token expired or invalid
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            // Redirect to login if not already there
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

// API endpoints - All under /api/v1
export const authAPI = {
    login: (username, password) =>
        api.post('/api/v1/auth/login', new URLSearchParams({ username, password }), {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        }),
    register: (username, password) =>
        api.post('/api/v1/auth/register', { username, password }),
};

export const tradesAPI = {
    getAll: (status = null) =>
        api.get('/api/v1/trades', { params: status ? { status } : {} }),
    create: (tradeData) => api.post('/api/v1/trades', tradeData),
    close: (tradeId, exitPrice) =>
        api.patch(`/api/v1/trades/${tradeId}/close`, { exit_price: exitPrice }),
};

export const portfolioAPI = {
    getSummary: () => api.get('/api/v1/portfolio/summary'),
};

// Admin API - Requires admin privileges
export const adminAPI = {
    getAllTrades: () => api.get('/api/v1/admin/trades'),
};

export default api;
