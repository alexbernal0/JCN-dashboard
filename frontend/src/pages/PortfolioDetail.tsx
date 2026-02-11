import { useQuery } from '@tanstack/react-query';
import { PortfolioPerformanceChart } from '../components/charts/PortfolioPerformanceChart';
import { SectorAllocationChart } from '../components/charts/SectorAllocationChart';
import { PortfolioRadarChart } from '../components/charts/PortfolioRadarChart';
import { StockTable, Stock } from '../components/tables/StockTable';
import { MetricsTable } from '../components/tables/MetricsTable';
import { Loading } from '../components/layout/Loading';
import { ErrorMessage } from '../components/layout/ErrorMessage';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK !== 'false'; // Default to mock data

interface PortfolioDetailProps {
  portfolioId: string;
  portfolioName: string;
}

export function PortfolioDetail({ portfolioId, portfolioName }: PortfolioDetailProps) {
  // Fetch portfolio data
  const { data: portfolio, isLoading, error, refetch } = useQuery({
    queryKey: ['portfolio', portfolioId],
    queryFn: async () => {
      const endpoint = USE_MOCK_DATA 
        ? `${API_BASE_URL}/api/v1/mock/portfolios/${portfolioId}`
        : `${API_BASE_URL}/api/v1/portfolios/${portfolioId}`;
      const response = await axios.get(endpoint);
      return response.data;
    },
  });

  if (isLoading) {
    return <Loading message={`Loading ${portfolioName} portfolio...`} />;
  }

  if (error) {
    return (
      <ErrorMessage
        title="Failed to load portfolio"
        message={error instanceof Error ? error.message : 'An error occurred'}
        onRetry={() => refetch()}
      />
    );
  }

  if (!portfolio) {
    return <ErrorMessage title="Portfolio not found" message="The requested portfolio could not be found." />;
  }

  // Prepare data for charts
  const performanceData = portfolio.performance || [];
  const sectorData = portfolio.sector_allocation || [];
  const stocks: Stock[] = portfolio.stocks || [];

  // Radar chart metrics
  const radarMetrics = [
    { name: 'Quality', max: 100 },
    { name: 'Value', max: 100 },
    { name: 'Growth', max: 100 },
    { name: 'Momentum', max: 100 },
    { name: 'Stability', max: 100 },
  ];

  const radarData = [
    {
      name: portfolioName,
      value: [
        portfolio.quality_score || 75,
        portfolio.value_score || 80,
        portfolio.growth_score || 70,
        portfolio.momentum_score || 65,
        portfolio.stability_score || 85,
      ],
    },
  ];

  // Key metrics
  const metrics = [
    { label: 'Total Value', value: portfolio.total_value || 0, format: 'currency' as const },
    { label: 'Total Stocks', value: portfolio.total_stocks || stocks.length, format: 'number' as const },
    { label: 'YTD Return', value: portfolio.ytd_return || 0, format: 'percentage' as const, change: portfolio.ytd_return },
    { label: 'Annual Return', value: portfolio.annual_return || 0, format: 'percentage' as const, change: portfolio.annual_return },
    { label: 'Sharpe Ratio', value: portfolio.sharpe_ratio || 0, format: 'number' as const },
    { label: 'Max Drawdown', value: portfolio.max_drawdown || 0, format: 'percentage' as const },
    { label: 'Volatility', value: portfolio.volatility || 0, format: 'percentage' as const },
    { label: 'Beta', value: portfolio.beta || 1.0, format: 'number' as const },
  ];

  return (
    <div className="space-y-6">
      {/* Portfolio Summary */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">{portfolioName}</h1>
        <p className="text-blue-100">{portfolio.description || 'Portfolio analysis and performance tracking'}</p>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-blue-200">Total Value</p>
            <p className="text-2xl font-bold">${(portfolio.total_value || 0).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-blue-200">YTD Return</p>
            <p className="text-2xl font-bold">{(portfolio.ytd_return || 0).toFixed(2)}%</p>
          </div>
          <div>
            <p className="text-sm text-blue-200">Total Stocks</p>
            <p className="text-2xl font-bold">{portfolio.total_stocks || stocks.length}</p>
          </div>
          <div>
            <p className="text-sm text-blue-200">Last Updated</p>
            <p className="text-2xl font-bold">{new Date().toLocaleDateString()}</p>
          </div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PortfolioPerformanceChart data={performanceData} title={`${portfolioName} Performance`} />
        <SectorAllocationChart data={sectorData} title="Sector Allocation" />
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PortfolioRadarChart metrics={radarMetrics} data={radarData} title="Quality Metrics" />
        <MetricsTable metrics={metrics} title="Portfolio Metrics" />
      </div>

      {/* Stock Holdings Table */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Stock Holdings</h2>
        <StockTable data={stocks} />
      </div>
    </div>
  );
}
