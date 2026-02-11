import { Shield, AlertTriangle, TrendingDown, Activity } from 'lucide-react';

export function RiskManagement() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">🛡️ Risk Management</h1>
        <p className="text-secondary">Portfolio risk assessment and monitoring tools</p>
      </div>

      {/* Coming Soon Banner */}
      <div className="bg-accent/10 border border-accent/20 rounded-lg p-8 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-8 h-8 text-accent" />
          <h2 className="text-2xl font-bold">Coming Soon</h2>
        </div>
        <p className="text-secondary text-lg">
          Advanced risk management features are under development. This page will include:
        </p>
      </div>

      {/* Feature Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <Activity className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">BPSP Analysis</h3>
          </div>
          <p className="text-secondary">
            Buying Power / Selling Pressure indicator for market timing and risk assessment.
          </p>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <TrendingDown className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Drawdown Analysis</h3>
          </div>
          <p className="text-secondary">
            Monitor maximum drawdowns and recovery periods for each portfolio.
          </p>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <AlertTriangle className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Volatility Metrics</h3>
          </div>
          <p className="text-secondary">
            Track portfolio volatility, beta, and standard deviation over time.
          </p>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <Shield className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Risk-Adjusted Returns</h3>
          </div>
          <p className="text-secondary">
            Calculate Sharpe ratio, Sortino ratio, and other risk-adjusted performance metrics.
          </p>
        </div>
      </div>
    </div>
  );
}
