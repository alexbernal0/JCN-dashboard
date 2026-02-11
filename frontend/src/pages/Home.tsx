import { TrendingUp, DollarSign, BarChart3 } from 'lucide-react';

export function Home() {
  return (
    <div className="min-h-screen bg-background text-primary p-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
        <p className="text-secondary">Overview of your investment portfolios</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Total Portfolio Value */}
        <div className="bg-surface border border-border rounded-lg p-6 hover:border-accent transition-all duration-200 hover:shadow-lg hover:shadow-accent/10">
          <div className="flex items-center gap-3 mb-4">
            <DollarSign className="w-5 h-5 text-secondary" />
            <span className="text-sm text-secondary">Total Portfolio Value</span>
          </div>
          <div className="text-3xl font-bold mb-2">$2,456,789</div>
          <div className="flex items-center gap-1 text-sm text-success">
            <TrendingUp className="w-4 h-4" />
            <span>+$12,345 (+0.52%)</span>
          </div>
        </div>

        {/* Today's Change */}
        <div className="bg-surface border border-border rounded-lg p-6 hover:border-accent transition-all duration-200 hover:shadow-lg hover:shadow-accent/10">
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className="w-5 h-5 text-secondary" />
            <span className="text-sm text-secondary">Today's Change</span>
          </div>
          <div className="text-3xl font-bold mb-2">+$8,234</div>
          <div className="flex items-center gap-1 text-sm text-success">
            <TrendingUp className="w-4 h-4" />
            <span>+0.34%</span>
          </div>
        </div>

        {/* Active Stocks */}
        <div className="bg-surface border border-border rounded-lg p-6 hover:border-accent transition-all duration-200 hover:shadow-lg hover:shadow-accent/10">
          <div className="flex items-center gap-3 mb-4">
            <BarChart3 className="w-5 h-5 text-secondary" />
            <span className="text-sm text-secondary">Active Stocks</span>
          </div>
          <div className="text-3xl font-bold mb-2">47</div>
          <div className="text-sm text-secondary">Across 3 portfolios</div>
        </div>
      </div>

      {/* Performance Chart */}
      <div className="bg-surface border border-border rounded-lg p-6 mb-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Portfolio Performance (30 Days)</h2>
          <span className="text-xs text-secondary">Last updated: Today, 4:00 PM EST</span>
        </div>
        <div className="h-[300px] bg-gradient-to-br from-accent/10 to-accent/5 rounded flex items-center justify-center text-secondary">
          [ECharts Line Chart - Portfolio Value Over Time]
        </div>
      </div>

      {/* Portfolio Summary Table */}
      <div className="bg-surface border border-border rounded-lg overflow-hidden">
        <div className="p-6 border-b border-border">
          <h2 className="text-xl font-semibold">Portfolio Summary</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-background">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-secondary uppercase tracking-wider">Portfolio</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-secondary uppercase tracking-wider">Total Value</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-secondary uppercase tracking-wider">Today's Change</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-secondary uppercase tracking-wider">% Change</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-secondary uppercase tracking-wider">Holdings</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-border/50 hover:bg-background/50 cursor-pointer transition-colors">
                <td className="px-6 py-4 font-semibold">Persistent Value</td>
                <td className="px-6 py-4">$1,234,567</td>
                <td className="px-6 py-4 text-success">+$8,234</td>
                <td className="px-6 py-4 text-success">+0.68%</td>
                <td className="px-6 py-4">23</td>
              </tr>
              <tr className="border-t border-border/50 hover:bg-background/50 cursor-pointer transition-colors">
                <td className="px-6 py-4 font-semibold">Olivia Growth</td>
                <td className="px-6 py-4">$850,123</td>
                <td className="px-6 py-4 text-success">+$3,100</td>
                <td className="px-6 py-4 text-success">+0.37%</td>
                <td className="px-6 py-4">15</td>
              </tr>
              <tr className="border-t border-border/50 hover:bg-background/50 cursor-pointer transition-colors">
                <td className="px-6 py-4 font-semibold">Pure Alpha</td>
                <td className="px-6 py-4">$372,099</td>
                <td className="px-6 py-4 text-success">+$1,011</td>
                <td className="px-6 py-4 text-success">+0.27%</td>
                <td className="px-6 py-4">9</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
