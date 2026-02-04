/**
 * Login Page Component
 * ====================
 * Handles user authentication with toggle between login and register modes.
 * 
 * Features:
 * - Form validation
 * - Loading states during API calls
 * - Error message display
 * - Redirect after successful auth
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
    const [isRegister, setIsRegister] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [localError, setLocalError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const { login, register, error: authError } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLocalError('');

        // Basic validation
        if (!username || !password) {
            setLocalError('Please fill in all fields');
            return;
        }

        if (isRegister) {
            if (password !== confirmPassword) {
                setLocalError('Passwords do not match');
                return;
            }
            if (password.length < 8) {
                setLocalError('Password must be at least 8 characters');
                return;
            }
        }

        setIsLoading(true);

        try {
            const result = isRegister
                ? await register(username, password)
                : await login(username, password);

            if (result.success) {
                navigate('/dashboard');
            } else {
                setLocalError(result.error);
            }
        } finally {
            setIsLoading(false);
        }
    };

    const errorMessage = localError || authError;

    return (
        <div className="min-h-screen flex items-center justify-center bg-dark-bg p-4">
            <div className="w-full max-w-md">
                {/* Logo/Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">
                        📈 Crypto Trade Logger
                    </h1>
                    <p className="text-slate-400">
                        Track your trading positions and analyze performance
                    </p>
                </div>

                {/* Auth Card */}
                <div className="card p-8">
                    {/* Tab Toggle */}
                    <div className="flex mb-6 bg-slate-700/50 rounded-lg p-1">
                        <button
                            type="button"
                            onClick={() => { setIsRegister(false); setLocalError(''); }}
                            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${!isRegister
                                    ? 'bg-blue-600 text-white shadow-sm'
                                    : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            Sign In
                        </button>
                        <button
                            type="button"
                            onClick={() => { setIsRegister(true); setLocalError(''); }}
                            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${isRegister
                                    ? 'bg-blue-600 text-white shadow-sm'
                                    : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            Register
                        </button>
                    </div>

                    {/* Error Message */}
                    {errorMessage && (
                        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm animate-slide-in">
                            {errorMessage}
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="label" htmlFor="username">
                                Username
                            </label>
                            <input
                                id="username"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="input-field"
                                placeholder="Enter your username"
                                autoComplete="username"
                                disabled={isLoading}
                            />
                        </div>

                        <div>
                            <label className="label" htmlFor="password">
                                Password
                            </label>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="input-field"
                                placeholder="Enter your password"
                                autoComplete={isRegister ? 'new-password' : 'current-password'}
                                disabled={isLoading}
                            />
                        </div>

                        {isRegister && (
                            <div className="animate-slide-in">
                                <label className="label" htmlFor="confirmPassword">
                                    Confirm Password
                                </label>
                                <input
                                    id="confirmPassword"
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="input-field"
                                    placeholder="Confirm your password"
                                    autoComplete="new-password"
                                    disabled={isLoading}
                                />
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full btn-primary py-3 mt-2 flex items-center justify-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                        <circle
                                            className="opacity-25"
                                            cx="12"
                                            cy="12"
                                            r="10"
                                            stroke="currentColor"
                                            strokeWidth="4"
                                            fill="none"
                                        />
                                        <path
                                            className="opacity-75"
                                            fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                        />
                                    </svg>
                                    {isRegister ? 'Creating Account...' : 'Signing In...'}
                                </>
                            ) : (
                                isRegister ? 'Create Account' : 'Sign In'
                            )}
                        </button>
                    </form>

                    {/* Footer */}
                    <p className="text-center text-slate-500 text-sm mt-6">
                        {isRegister ? 'Already have an account? ' : "Don't have an account? "}
                        <button
                            type="button"
                            onClick={() => { setIsRegister(!isRegister); setLocalError(''); }}
                            className="text-blue-400 hover:text-blue-300 font-medium"
                        >
                            {isRegister ? 'Sign In' : 'Register'}
                        </button>
                    </p>
                </div>

                {/* Branding */}
                <p className="text-center text-slate-600 text-xs mt-6">
                    Built for Primetrade.ai · Take-Home Assignment
                </p>
            </div>
        </div>
    );
}
