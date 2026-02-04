/**
 * Portfolio Summary Component
 * ===========================
 * Displays key trading performance metrics.
 * 
 * Features:
 * - Total P&L with color coding (green/red)
 * - Position counts (open/closed)
 * - Win rate percentage
 * - Visual indicators for quick assessment
 */

export default function PortfolioSummary({ summary }) {
    const formatPnL = (value) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            signDisplay: 'always',
        }).format(value);
    };

    const pnlColor =
        summary.total_realized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400';
    const pnlBgColor =
        summary.total_realized_pnl >= 0
            ? 'bg-emerald-500/10 border-emerald-500/30'
            : 'bg-red-500/10 border-red-500/30';

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total P&L */}
            <div className={`card p-6 border ${pnlBgColor}`}>
                <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">💰</span>
                    <span className="text-sm font-medium text-slate-400">
                        Realized P&L
                    </span>
                </div>
                <p className={`text-2xl font-bold ${pnlColor}`}>
                    {formatPnL(summary.total_realized_pnl)}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                    From {summary.closed_positions} closed trade
                    {summary.closed_positions !== 1 ? 's' : ''}
                </p>
            </div>

            {/* Open Positions */}
            <div className="card p-6">
                <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">📊</span>
                    <span className="text-sm font-medium text-slate-400">
                        Open Positions
                    </span>
                </div>
                <p className="text-2xl font-bold text-white">
                    {summary.open_positions}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                    Active trades
                </p>
            </div>

            {/* Win Rate */}
            <div className="card p-6">
                <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">🎯</span>
                    <span className="text-sm font-medium text-slate-400">Win Rate</span>
                </div>
                <p className="text-2xl font-bold text-white">
                    {summary.win_rate.toFixed(1)}%
                </p>
                <p className="text-xs text-slate-500 mt-1">
                    {summary.winning_trades}W / {summary.losing_trades}L
                </p>
            </div>

            {/* Total Trades */}
            <div className="card p-6">
                <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">📈</span>
                    <span className="text-sm font-medium text-slate-400">
                        Total Trades
                    </span>
                </div>
                <p className="text-2xl font-bold text-white">
                    {summary.open_positions + summary.closed_positions}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                    All time positions
                </p>
            </div>
        </div>
    );
}
