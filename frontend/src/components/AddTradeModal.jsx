/**
 * Add Trade Modal Component
 * =========================
 * Form for creating new trading positions.
 * 
 * Features:
 * - Input validation before submit
 * - Loading state during API call
 * - Error handling with user feedback
 */

import { useState } from 'react';
import { tradesAPI } from '../services/api';

export default function AddTradeModal({ isOpen, onClose, onTradeAdded }) {
    const [symbol, setSymbol] = useState('');
    const [entryPrice, setEntryPrice] = useState('');
    const [quantity, setQuantity] = useState('');
    const [tradeType, setTradeType] = useState('BUY');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const resetForm = () => {
        setSymbol('');
        setEntryPrice('');
        setQuantity('');
        setTradeType('BUY');
        setError('');
    };

    const handleClose = () => {
        resetForm();
        onClose();
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validation
        if (!symbol || !entryPrice || !quantity) {
            setError('Please fill in all fields');
            return;
        }

        if (!symbol.includes('/')) {
            setError('Symbol must be in BASE/QUOTE format (e.g., BTC/USDT)');
            return;
        }

        if (parseFloat(entryPrice) <= 0) {
            setError('Entry price must be greater than 0');
            return;
        }

        if (parseFloat(quantity) <= 0) {
            setError('Quantity must be greater than 0');
            return;
        }

        setIsLoading(true);

        try {
            const response = await tradesAPI.create({
                symbol: symbol.toUpperCase(),
                entry_price: parseFloat(entryPrice),
                quantity: parseFloat(quantity),
                trade_type: tradeType,
            });

            onTradeAdded(response.data);
            resetForm();
        } catch (err) {
            const message =
                err.response?.data?.error?.message || 'Failed to create trade';
            setError(message);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
            <div className="card glass p-6 w-full max-w-md animate-slide-in">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-white">Add New Trade</h3>
                    <button
                        onClick={handleClose}
                        className="text-slate-400 hover:text-white transition-colors"
                    >
                        ✕
                    </button>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm animate-slide-in">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Symbol */}
                    <div>
                        <label className="label" htmlFor="symbol">
                            Trading Pair
                        </label>
                        <input
                            id="symbol"
                            type="text"
                            value={symbol}
                            onChange={(e) => setSymbol(e.target.value)}
                            className="input-field"
                            placeholder="BTC/USDT"
                            disabled={isLoading}
                        />
                        <p className="text-xs text-slate-500 mt-1">
                            Format: BASE/QUOTE (e.g., BTC/USDT, ETH/USDT)
                        </p>
                    </div>

                    {/* Trade Type */}
                    <div>
                        <label className="label">Trade Type</label>
                        <div className="flex gap-2">
                            <button
                                type="button"
                                onClick={() => setTradeType('BUY')}
                                className={`flex-1 py-2.5 px-4 rounded-lg font-medium transition-all ${tradeType === 'BUY'
                                        ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30'
                                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                    }`}
                            >
                                🟢 BUY (Long)
                            </button>
                            <button
                                type="button"
                                onClick={() => setTradeType('SELL')}
                                className={`flex-1 py-2.5 px-4 rounded-lg font-medium transition-all ${tradeType === 'SELL'
                                        ? 'bg-red-600 text-white shadow-lg shadow-red-600/30'
                                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                                    }`}
                            >
                                🔴 SELL (Short)
                            </button>
                        </div>
                    </div>

                    {/* Entry Price */}
                    <div>
                        <label className="label" htmlFor="entryPrice">
                            Entry Price (USD)
                        </label>
                        <input
                            id="entryPrice"
                            type="number"
                            step="0.00000001"
                            min="0"
                            value={entryPrice}
                            onChange={(e) => setEntryPrice(e.target.value)}
                            className="input-field"
                            placeholder="50000.00"
                            disabled={isLoading}
                        />
                    </div>

                    {/* Quantity */}
                    <div>
                        <label className="label" htmlFor="quantity">
                            Quantity
                        </label>
                        <input
                            id="quantity"
                            type="number"
                            step="0.00000001"
                            min="0"
                            value={quantity}
                            onChange={(e) => setQuantity(e.target.value)}
                            className="input-field"
                            placeholder="0.1"
                            disabled={isLoading}
                        />
                    </div>

                    {/* Position Value Preview */}
                    {entryPrice && quantity && parseFloat(entryPrice) > 0 && parseFloat(quantity) > 0 && (
                        <div className="p-3 bg-slate-700/50 rounded-lg text-sm animate-slide-in">
                            <div className="flex justify-between">
                                <span className="text-slate-400">Position Value:</span>
                                <span className="text-white font-medium">
                                    $
                                    {new Intl.NumberFormat('en-US', {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2,
                                    }).format(parseFloat(entryPrice) * parseFloat(quantity))}
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Submit Button */}
                    <div className="flex gap-3 pt-2">
                        <button
                            type="button"
                            onClick={handleClose}
                            className="flex-1 py-2.5 px-4 bg-slate-600 hover:bg-slate-500 text-white rounded-lg transition-colors"
                            disabled={isLoading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="flex-1 btn-success flex items-center justify-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
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
                                    Creating...
                                </>
                            ) : (
                                'Add Trade'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
