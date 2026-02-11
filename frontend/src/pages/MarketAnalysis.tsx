import { TrendingUp, BarChart3, PieChart, Activity } from 'lucide-react';

export function MarketAnalysis() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">🌍 Market Analysis</h1>
        <p className="text-secondary">Broad market trends and sector analysis</p>
      </div>

      {/* Coming Soon Banner */}
      <div className="bg-accent/10 border border-accent/20 rounded-lg p-8 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Activity className="w-8 h-8 text-accent" />
          <h2 className="text-2xl font-bold">Coming Soon</h2>
        </div>
        <p className="text-secondary text-lg">
          Market-wide analysis features are under development. This page will include:
        </p>
      </div>

      {/* Feature Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <TrendingUp className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Market Indices</h3>
          </div>
          <p className="text-secondary">
            Track major market indices including S&P 500, NASDAQ, Dow Jones, and international markets.
          </p>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <PieChart className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Sector Performance</h3>
          </div>
          <p className="text-secondary">
            Analyze performance across different market sectors and identify rotation trends.
          </p>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <BarChart3 className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Market Breadth</h3>
          </div>
          <p className="text-secondary">
            Monitor advance/decline ratios, new highs/lows, and other breadth indicators.
          </p>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <Activity className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Economic Indicators</h3>
          </div>
          <p className="text-secondary">
            Track key economic data including GDP, inflation, employment, and interest rates.
          </p>
        </div>
      </div>
    </div>
  );
}
