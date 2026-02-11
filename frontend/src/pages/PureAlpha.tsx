import { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { TrendingUp, TrendingDown, DollarSign, Package, Wallet, RefreshCw } from 'lucide-react';

interface StockHolding {
  symbol: string;
  company_name: string;
  shares: number;
  cost_basis: number;
  current_price: number;
  position_value: number;
  total_cost: number;
  gain_loss: number;
  gain_loss_percent: number;
  weight: number;
  day_change?: number;
  day_change_percent?: number;
  sector?: string;
  industry?: string;
}

interface PortfolioData {
  portfolio_id: string;
  name: string;
  description: string;
  last_updated: string;
  holdings: StockHolding[];
  performance: {
    dates: string[];
    portfolio_values: number[];
    sp500_values: number[];
  };
  allocation: {
    by_stock: Record<string, number>;
    by_sector: Record<string, number>;
    by_industry: Record<string, number>;
  };
  metrics: {
    total_value: number;
    total_cost: number;
    total_gain_loss: number;
    total_gain_loss_percent: number;
    cash: number;
    num_holdings: number;
    day_change: number;
    day_change_percent: number;
  };
}

export function PureAlpha() {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPortfolio = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('https://jcn-dashboard-production.up.railway.app/api/v1/portfolios/pure_alpha');
      if (!response.ok) {
        throw new Error('Failed to fetch portfolio data');
      }
      const data = await response.json();
      setPortfolio(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-accent" />
          <p className="text-secondary">Loading portfolio data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6">
        <p className="text-red-500">Error: {error}</p>
        <button 
          onClick={fetchPortfolio}
          className="mt-4 px-4 py-2 bg-accent text-white rounded hover:bg-accent/80"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!portfolio) {
    return <div>No data available</div>;
  }

  // Format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Format percent
  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  // Performance chart options
  const performanceChartOptions = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#333',
      textStyle: { color: '#fff' }
    },
    legend: {
      data: ['Portfolio', 'S&P 500'],
      textStyle: { color: 'var(--color-text-primary)' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: portfolio.performance.dates,
      axisLine: { lineStyle: { color: '#666' } },
      axisLabel: { color: '#999' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#666' } },
      axisLabel: { color: '#999' },
      splitLine: { lineStyle: { color: '#333' } }
    },
    series: [
      {
        name: 'Portfolio',
        type: 'line',
        data: portfolio.performance.portfolio_values,
        smooth: true,
        lineStyle: { color: '#8b5cf6', width: 2 },
        itemStyle: { color: '#8b5cf6' }
      },
      {
        name: 'S&P 500',
        type: 'line',
        data: portfolio.performance.sp500_values,
        smooth: true,
        lineStyle: { color: '#3b82f6', width: 2 },
        itemStyle: { color: '#3b82f6' }
      }
    ]
  };

  // Sector allocation chart
  const sectorChartOptions = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#333',
      textStyle: { color: '#fff' }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: 'var(--color-text-primary)' }
    },
    series: [
      {
        name: 'Sector Allocation',
        type: 'pie',
        radius: '50%',
        data: Object.entries(portfolio.allocation.by_sector).map(([name, value]) => ({
          name,
          value: value.toFixed(2)
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">⚡ {portfolio.name}</h1>
          <p className="text-secondary">{portfolio.description}</p>
        </div>
        <button
          onClick={fetchPortfolio}
          className="flex items-center gap-2 px-4 py-2 bg-surface border border-border rounded hover:border-accent transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Metrics Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-5 h-5 text-accent" />
            <span className="text-sm text-secondary">Total Value</span>
          </div>
          <div className="text-2xl font-bold">{formatCurrency(portfolio.metrics.total_value)}</div>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            {portfolio.metrics.total_gain_loss >= 0 ? (
              <TrendingUp className="w-5 h-5 text-green-500" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-500" />
            )}
            <span className="text-sm text-secondary">Total Gain/Loss</span>
          </div>
          <div className={`text-2xl font-bold ${portfolio.metrics.total_gain_loss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {formatCurrency(portfolio.metrics.total_gain_loss)}
          </div>
          <div className={`text-sm ${portfolio.metrics.total_gain_loss_percent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {formatPercent(portfolio.metrics.total_gain_loss_percent)}
          </div>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            <Package className="w-5 h-5 text-accent" />
            <span className="text-sm text-secondary">Holdings</span>
          </div>
          <div className="text-2xl font-bold">{portfolio.metrics.num_holdings}</div>
          <div className="text-sm text-secondary">stocks</div>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-2">
            <Wallet className="w-5 h-5 text-accent" />
            <span className="text-sm text-secondary">Cash</span>
          </div>
          <div className="text-2xl font-bold">{formatCurrency(portfolio.metrics.cash)}</div>
        </div>
      </div>

      {/* Holdings Table */}
      <div className="bg-surface border border-border rounded-lg overflow-hidden mb-8">
        <div className="p-6 border-b border-border">
          <h2 className="text-xl font-semibold">Portfolio Holdings</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-background">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-secondary uppercase">Symbol</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-secondary uppercase">Company</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-secondary uppercase">Shares</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-secondary uppercase">Cost Basis</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-secondary uppercase">Current Price</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-secondary uppercase">Position Value</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-secondary uppercase">Gain/Loss</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-secondary uppercase">Weight</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.holdings.map((holding) => (
                <tr key={holding.symbol} className="border-t border-border/50 hover:bg-background/50">
                  <td className="px-4 py-3 font-semibold">{holding.symbol}</td>
                  <td className="px-4 py-3">{holding.company_name}</td>
                  <td className="px-4 py-3 text-right">{holding.shares.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right">${holding.cost_basis.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right">${holding.current_price.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right">{formatCurrency(holding.position_value)}</td>
                  <td className={`px-4 py-3 text-right ${holding.gain_loss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {formatCurrency(holding.gain_loss)}
                    <div className="text-xs">{formatPercent(holding.gain_loss_percent)}</div>
                  </td>
                  <td className="px-4 py-3 text-right">{holding.weight.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Chart */}
      {portfolio.performance.dates.length > 0 && (
        <div className="bg-surface border border-border rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Performance vs S&P 500</h2>
          <ReactECharts option={performanceChartOptions} style={{ height: '400px' }} />
        </div>
      )}

      {/* Sector Allocation */}
      {Object.keys(portfolio.allocation.by_sector).length > 0 && (
        <div className="bg-surface border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Sector Allocation</h2>
          <ReactECharts option={sectorChartOptions} style={{ height: '400px' }} />
        </div>
      )}
    </div>
  );
}
