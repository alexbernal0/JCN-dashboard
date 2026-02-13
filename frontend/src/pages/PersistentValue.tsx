import ReactECharts from 'echarts-for-react';
import { TrendingUp, TrendingDown, DollarSign, Package, Wallet, RefreshCw } from 'lucide-react';
import { usePortfolio } from '../hooks/usePortfolio';

export function PersistentValue() {
  const { data: portfolio, isLoading, isError, error, refetch } = usePortfolio('persistent_value');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-accent" />
          <p className="text-secondary">Loading portfolio data...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6">
        <p className="text-red-500">Error: {error instanceof Error ? error.message : 'An error occurred'}</p>
        <button 
          onClick={() => refetch()}
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
        lineStyle: { color: '#6246ea', width: 2 },
        itemStyle: { color: '#6246ea' }
      },
      {
        name: 'S&P 500',
        type: 'line',
        data: portfolio.performance.sp500_values,
        smooth: true,
        lineStyle: { color: '#999', width: 2 },
        itemStyle: { color: '#999' }
      }
    ]
  };

  // Allocation chart options
  const allocationChartOptions = {
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
        name: 'Allocation',
        type: 'pie',
        radius: '50%',
        data: Object.entries(portfolio.allocation.by_stock).map(([name, value]) => ({
          name,
          value
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
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">{portfolio.name}</h1>
          <p className="text-secondary mt-1">{portfolio.description}</p>
          <p className="text-sm text-secondary mt-1">Last updated: {new Date(portfolio.last_updated).toLocaleString()}</p>
        </div>
        <button 
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-accent text-white rounded hover:bg-accent/80 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-surface rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-secondary text-sm">Total Value</span>
            <DollarSign className="w-5 h-5 text-accent" />
          </div>
          <div className="text-2xl font-bold">{formatCurrency(portfolio.metrics.total_value)}</div>
          <div className={`text-sm mt-1 ${portfolio.metrics.day_change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {formatPercent(portfolio.metrics.day_change_percent)} today
          </div>
        </div>

        <div className="bg-surface rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-secondary text-sm">Total Gain/Loss</span>
            {portfolio.metrics.total_gain_loss >= 0 ? (
              <TrendingUp className="w-5 h-5 text-green-500" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-500" />
            )}
          </div>
          <div className={`text-2xl font-bold ${portfolio.metrics.total_gain_loss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {formatCurrency(portfolio.metrics.total_gain_loss)}
          </div>
          <div className={`text-sm mt-1 ${portfolio.metrics.total_gain_loss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {formatPercent(portfolio.metrics.total_gain_loss_percent)}
          </div>
        </div>

        <div className="bg-surface rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-secondary text-sm">Holdings</span>
            <Package className="w-5 h-5 text-accent" />
          </div>
          <div className="text-2xl font-bold">{portfolio.metrics.num_holdings}</div>
          <div className="text-sm text-secondary mt-1">Active positions</div>
        </div>

        <div className="bg-surface rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-secondary text-sm">Cash</span>
            <Wallet className="w-5 h-5 text-accent" />
          </div>
          <div className="text-2xl font-bold">{formatCurrency(portfolio.metrics.cash)}</div>
          <div className="text-sm text-secondary mt-1">Available</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-surface rounded-lg p-6 border border-border">
          <h2 className="text-xl font-semibold mb-4">Performance</h2>
          <ReactECharts option={performanceChartOptions} style={{ height: '300px' }} />
        </div>

        <div className="bg-surface rounded-lg p-6 border border-border">
          <h2 className="text-xl font-semibold mb-4">Allocation</h2>
          <ReactECharts option={allocationChartOptions} style={{ height: '300px' }} />
        </div>
      </div>

      {/* Holdings Table */}
      <div className="bg-surface rounded-lg p-6 border border-border">
        <h2 className="text-xl font-semibold mb-4">Holdings</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 text-secondary font-medium">Symbol</th>
                <th className="text-left py-3 px-4 text-secondary font-medium">Company</th>
                <th className="text-right py-3 px-4 text-secondary font-medium">Shares</th>
                <th className="text-right py-3 px-4 text-secondary font-medium">Price</th>
                <th className="text-right py-3 px-4 text-secondary font-medium">Value</th>
                <th className="text-right py-3 px-4 text-secondary font-medium">Gain/Loss</th>
                <th className="text-right py-3 px-4 text-secondary font-medium">Weight</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.holdings.map((holding) => (
                <tr key={holding.symbol} className="border-b border-border hover:bg-background/50 transition-colors">
                  <td className="py-3 px-4 font-semibold">{holding.symbol}</td>
                  <td className="py-3 px-4 text-secondary">{holding.company_name}</td>
                  <td className="py-3 px-4 text-right">{holding.shares.toLocaleString()}</td>
                  <td className="py-3 px-4 text-right">{formatCurrency(holding.current_price)}</td>
                  <td className="py-3 px-4 text-right font-semibold">{formatCurrency(holding.position_value)}</td>
                  <td className={`py-3 px-4 text-right font-semibold ${holding.gain_loss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {formatCurrency(holding.gain_loss)} ({formatPercent(holding.gain_loss_percent)})
                  </td>
                  <td className="py-3 px-4 text-right">{holding.weight.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Portfolio Input */}
      <div className="mt-8 bg-surface rounded-lg p-6 border border-border">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-xl font-semibold">Portfolio Input</h2>
            <p className="text-sm text-secondary mt-1">Edit your portfolio holdings</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 text-sm font-semibold">Symbol</th>
                <th className="text-right py-3 px-4 text-sm font-semibold">Cost Basis ($)</th>
                <th className="text-right py-3 px-4 text-sm font-semibold">Shares</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.holdings.map((holding) => (
                <tr key={holding.symbol} className="border-b border-border/50">
                  <td className="py-3 px-4 font-semibold">{holding.symbol}</td>
                  <td className="py-3 px-4 text-right">${holding.cost_basis.toFixed(2)}</td>
                  <td className="py-3 px-4 text-right">{holding.shares}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
