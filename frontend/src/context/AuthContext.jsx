/**
 * Authentication Context
 * ======================
 * Provides auth state and functions throughout the app.
 * 
 * Features:
 * - Stores JWT token in localStorage for persistence
 * - Decodes JWT to extract user info including admin status
 * - Provides login/logout functions
 * - Exposes auth state to all components
 */

import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

// Helper function to decode JWT payload (base64)
function decodeJwtPayload(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split('')
                .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(jsonPayload);
    } catch {
        return null;
    }
}

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Check if we have a valid token on mount
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setToken(storedToken);
            // Decode token to get user info
            const payload = decodeJwtPayload(storedToken);
            if (payload) {
                setUser({
                    username: payload.sub,
                    isAdmin: payload.is_admin || false,
                    authenticated: true
                });
            } else {
                setUser({ authenticated: true });
            }
        }
        setLoading(false);
    }, []);

    const login = async (username, password) => {
        setError(null);
        try {
            const response = await authAPI.login(username, password);
            const { access_token } = response.data;

            localStorage.setItem('token', access_token);
            setToken(access_token);

            // Decode token to get admin status
            const payload = decodeJwtPayload(access_token);
            setUser({
                username,
                isAdmin: payload?.is_admin || false,
                authenticated: true
            });

            return { success: true };
        } catch (err) {
            const message = err.response?.data?.error?.message || 'Login failed';
            setError(message);
            return { success: false, error: message };
        }
    };

    const register = async (username, password) => {
        setError(null);
        try {
            await authAPI.register(username, password);
            // Automatically log in after registration
            return await login(username, password);
        } catch (err) {
            const message = err.response?.data?.error?.message || 'Registration failed';
            setError(message);
            return { success: false, error: message };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    const value = {
        user,
        token,
        loading,
        error,
        isAuthenticated: !!token,
        isAdmin: user?.isAdmin || false,
        login,
        register,
        logout,
        clearError: () => setError(null),
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
