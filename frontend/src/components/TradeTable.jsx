/**
 * Trade Table Component
 * =====================
 * Displays trades in a table with color-coded side indicators.
 * 
 * Features:
 * - BUY trades shown in green, SELL in red
 * - Close trade functionality for open positions
 * - Responsive design
 * - P&L display for closed trades
 */

import { useState } from 'react';

export default function TradeTable({ trades, onCloseTrade }) {
    const [closingTrade, setClosingTrade] = useState(null);
    const [exitPrice, setExitPrice] = useState('');
    const [closeError, setCloseError] = useState('');

    const handleCloseClick = (trade) => {
        setClosingTrade(trade);
        setExitPrice('');
        setCloseError('');
    };

    const handleCloseSubmit = async () => {
        if (!exitPrice || parseFloat(exitPrice) <= 0) {
            setCloseError('Please enter a valid exit price');
            return;
        }

        const result = await onCloseTrade(closingTrade.id, parseFloat(exitPrice));

        if (result.success) {
            setClosingTrade(null);
            setExitPrice('');
        } else {
            setCloseError(result.error);
        }
    };

    const formatPrice = (price) => {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 8,
        }).format(price);
    };

    const formatPnL = (pnl) => {
        const formatted = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            signDisplay: 'always',
        }).format(pnl);
        return pnl >= 0 ? (
            <span className="text-emerald-400">{formatted}</span>
        ) : (
            <span className="text-red-400">{formatted}</span>
        );
    };

    if (trades.length === 0) {
        return (
            <div className="p-12 text-center">
                <div className="text-4xl mb-4">📊</div>
                <h3 className="text-lg font-medium text-white mb-2">No trades yet</h3>
                <p className="text-slate-400">
                    Start by adding your first trade to track your positions.
                </p>
            </div>
        );
    }

    return (
        <div className="overflow-x-auto">
            <table className="w-full">
                <thead>
                    <tr className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                        <th className="px-6 py-4">Symbol</th>
                        <th className="px-6 py-4">Side</th>
                        <th className="px-6 py-4">Entry Price</th>
                        <th className="px-6 py-4">Quantity</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4">Exit Price</th>
                        <th className="px-6 py-4">P&L</th>
                        <th className="px-6 py-4">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                    {trades.map((trade) => (
                        <tr
                            key={trade.id}
                            className="hover:bg-slate-700/30 transition-colors"
                        >
                            <td className="px-6 py-4">
                                <span className="font-medium text-white">{trade.symbol}</span>
                            </td>
                            <td className="px-6 py-4">
                                <span
                                    className={
                                        trade.trade_type === 'BUY' ? 'badge-buy' : 'badge-sell'
                                    }
                                >
                                    {trade.trade_type}
                                </span>
                            </td>
                            <td className="px-6 py-4 text-slate-300">
                                ${formatPrice(trade.entry_price)}
                            </td>
                            <td className="px-6 py-4 text-slate-300">
                                {formatPrice(trade.quantity)}
                            </td>
                            <td className="px-6 py-4">
                                <span
                                    className={
                                        trade.status === 'OPEN' ? 'badge-open' : 'badge-closed'
                                    }
                                >
                                    {trade.status}
                                </span>
                            </td>
                            <td className="px-6 py-4 text-slate-300">
                                {trade.exit_price ? `$${formatPrice(trade.exit_price)}` : '—'}
                            </td>
                            <td className="px-6 py-4">
                                {trade.realized_pnl !== null
                                    ? formatPnL(trade.realized_pnl)
                                    : '—'}
                            </td>
                            <td className="px-6 py-4">
                                {trade.status === 'OPEN' && (
                                    <button
                                        onClick={() => handleCloseClick(trade)}
                                        className="text-sm text-blue-400 hover:text-blue-300 font-medium"
                                    >
                                        Close
                                    </button>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Close Trade Modal */}
            {closingTrade && (
                <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
                    <div className="card glass p-6 w-full max-w-md animate-slide-in">
                        <h3 className="text-lg font-semibold text-white mb-4">
                            Close Trade: {closingTrade.symbol}
                        </h3>

                        <div className="mb-4 p-3 bg-slate-700/50 rounded-lg text-sm">
                            <div className="flex justify-between mb-2">
                                <span className="text-slate-400">Entry Price:</span>
                                <span className="text-white">
                                    ${formatPrice(closingTrade.entry_price)}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-400">Quantity:</span>
                                <span className="text-white">
                                    {formatPrice(closingTrade.quantity)}
                                </span>
                            </div>
                        </div>

                        {closeError && (
                            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                                {closeError}
                            </div>
                        )}

                        <div className="mb-4">
                            <label className="label">Exit Price</label>
                            <input
                                type="number"
                                step="0.00000001"
                                value={exitPrice}
                                onChange={(e) => setExitPrice(e.target.value)}
                                className="input-field"
                                placeholder="Enter exit price"
                                autoFocus
                            />
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={() => setClosingTrade(null)}
                                className="flex-1 py-2 px-4 bg-slate-600 hover:bg-slate-500 text-white rounded-lg transition-colors"
                            >
                                Cancel
                            </button>
                            <button onClick={handleCloseSubmit} className="flex-1 btn-primary">
                                Confirm Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
