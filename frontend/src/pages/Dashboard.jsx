/**
 * Dashboard Page Component
 * ========================
 * Main trading dashboard displaying portfolio summary and trades table.
 * 
 * Features:
 * - Portfolio summary with P&L display
 * - Trades table with color-coded sides
 * - Add trade modal
 * - Close trade functionality
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { tradesAPI, portfolioAPI } from '../services/api';
import TradeTable from '../components/TradeTable';
import AddTradeModal from '../components/AddTradeModal';
import PortfolioSummary from '../components/PortfolioSummary';

export default function Dashboard() {
    const [trades, setTrades] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [showAdminPanel, setShowAdminPanel] = useState(false);

    const { logout, user } = useAuth();
    const navigate = useNavigate();

    // Fetch trades and portfolio summary
    const fetchData = useCallback(async () => {
        try {
            setError(null);
            const [tradesRes, summaryRes] = await Promise.all([
                tradesAPI.getAll(),
                portfolioAPI.getSummary(),
            ]);
            setTrades(tradesRes.data);
            setSummary(summaryRes.data);
        } catch (err) {
            console.error('Failed to fetch data:', err);
            setError('Failed to load data. Please try again.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Handle adding a new trade
    const handleTradeAdded = (newTrade) => {
        setTrades((prev) => [newTrade, ...prev]);
        setIsModalOpen(false);
        // Refresh summary to include new position
        portfolioAPI.getSummary().then((res) => setSummary(res.data));
    };

    // Handle closing a trade
    const handleCloseTrade = async (tradeId, exitPrice) => {
        try {
            const response = await tradesAPI.close(tradeId, exitPrice);
            const updatedTrade = response.data;

            // Update trade in list
            setTrades((prev) =>
                prev.map((t) => (t.id === tradeId ? updatedTrade : t))
            );

            // Refresh summary
            const summaryRes = await portfolioAPI.getSummary();
            setSummary(summaryRes.data);

            return { success: true };
        } catch (err) {
            const message = err.response?.data?.error?.message || 'Failed to close trade';
            return { success: false, error: message };
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-dark-bg flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <svg className="animate-spin h-10 w-10 text-blue-500" viewBox="0 0 24 24">
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
                    <p className="text-slate-400">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-dark-bg">
            {/* Navigation Bar */}
            <nav className="bg-slate-800 border-b border-slate-700">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">📈</span>
                            <h1 className="text-xl font-bold text-white">
                                Crypto Trade Logger
                            </h1>
                        </div>
                        <div className="flex items-center gap-4">
                            {user?.isAdmin && (
                                <button
                                    onClick={() => setShowAdminPanel(!showAdminPanel)}
                                    className="text-sm bg-purple-600 hover:bg-purple-700 text-white px-3 py-1.5 rounded-lg flex items-center gap-2 transition-colors"
                                >
                                    <span>👑</span>
                                    <span>Admin Panel</span>
                                </button>
                            )}
                            <span className="text-slate-400 text-sm">
                                Welcome, <span className="text-white font-medium">{user?.username || 'Trader'}</span>
                                {user?.isAdmin && <span className="ml-1 text-purple-400">(Admin)</span>}
                            </span>
                            <button
                                onClick={handleLogout}
                                className="text-sm text-slate-400 hover:text-white transition-colors"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Error Alert */}
                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 flex items-center justify-between">
                        <span>{error}</span>
                        <button
                            onClick={() => setError(null)}
                            className="text-red-400 hover:text-red-300"
                        >
                            ✕
                        </button>
                    </div>
                )}

                {/* Portfolio Summary */}
                {summary && (
                    <PortfolioSummary summary={summary} />
                )}

                {/* Trades Section */}
                <div className="card mt-6">
                    <div className="p-6 border-b border-slate-700 flex items-center justify-between">
                        <div>
                            <h2 className="text-lg font-semibold text-white">Your Trades</h2>
                            <p className="text-sm text-slate-400 mt-1">
                                {trades.length} total position{trades.length !== 1 ? 's' : ''}
                            </p>
                        </div>
                        <button
                            onClick={() => setIsModalOpen(true)}
                            className="btn-success flex items-center gap-2"
                        >
                            <span>+</span>
                            <span>Add Trade</span>
                        </button>
                    </div>

                    <TradeTable trades={trades} onCloseTrade={handleCloseTrade} />
                </div>
            </main>

            {/* Add Trade Modal */}
            <AddTradeModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onTradeAdded={handleTradeAdded}
            />
        </div>
    );
}
