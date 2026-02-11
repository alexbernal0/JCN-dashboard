import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search } from 'lucide-react';
import { StockPriceChart } from '../components/charts/StockPriceChart';
import { MetricsTable } from '../components/tables/MetricsTable';
import { Loading } from '../components/layout/Loading';
import { ErrorMessage } from '../components/layout/ErrorMessage';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK !== 'false'; // Default to mock data

export function StockAnalysis() {
  const [symbol, setSymbol] = useState('');
  const [searchSymbol, setSearchSymbol] = useState('');

  // Fetch stock data
  const { data: stock, isLoading, error, refetch } = useQuery({
    queryKey: ['stock', searchSymbol],
    queryFn: async () => {
      if (!searchSymbol) return null;
      const endpoint = USE_MOCK_DATA
        ? `${API_BASE_URL}/api/v1/mock/stocks/${searchSymbol}`
        : `${API_BASE_URL}/api/v1/stocks/${searchSymbol}`;
      const response = await axios.get(endpoint);
      return response.data;
    },
    enabled: !!searchSymbol,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (symbol.trim()) {
      setSearchSymbol(symbol.trim().toUpperCase());
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Section */}
      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Search Stock</h2>
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Enter stock symbol (e.g., AAPL, MSFT, GOOGL)"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Search
          </button>
        </form>
      </div>

      {/* Results Section */}
      {isLoading && <Loading message={`Loading ${searchSymbol} data...`} />}

      {error && (
        <ErrorMessage
          title="Failed to load stock data"
          message={error instanceof Error ? error.message : 'An error occurred'}
          onRetry={() => refetch()}
        />
      )}

      {stock && (
        <>
          {/* Stock Info Card */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg p-6 text-white">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">{stock.symbol}</h1>
                <p className="text-blue-100 text-lg">{stock.name}</p>
              </div>
              <div className="text-right">
                <p className="text-4xl font-bold">${stock.current_price?.toFixed(2)}</p>
                <p className={`text-lg font-medium ${
                  stock.change >= 0 ? 'text-green-300' : 'text-red-300'
                }`}>
                  {stock.change >= 0 ? '+' : ''}{stock.change?.toFixed(2)} ({stock.change_percent >= 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}%)
                </p>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-blue-200">Market Cap</p>
                <p className="text-xl font-bold">
                  ${stock.market_cap >= 1000000000 
                    ? `${(stock.market_cap / 1000000000).toFixed(2)}B` 
                    : `${(stock.market_cap / 1000000).toFixed(2)}M`}
                </p>
              </div>
              <div>
                <p className="text-sm text-blue-200">Volume</p>
                <p className="text-xl font-bold">
                  {stock.volume >= 1000000 
                    ? `${(stock.volume / 1000000).toFixed(2)}M` 
                    : `${(stock.volume / 1000).toFixed(2)}K`}
                </p>
              </div>
              <div>
                <p className="text-sm text-blue-200">P/E Ratio</p>
                <p className="text-xl font-bold">{stock.pe_ratio?.toFixed(2) || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-blue-200">Sector</p>
                <p className="text-xl font-bold">{stock.sector || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Price Chart */}
          {stock.price_history && stock.price_history.length > 0 && (
            <StockPriceChart data={stock.price_history} symbol={stock.symbol} height={500} />
          )}

          {/* Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MetricsTable
              title="Valuation Metrics"
              metrics={[
                { label: 'P/E Ratio', value: stock.pe_ratio || 0, format: 'number' },
                { label: 'P/B Ratio', value: stock.pb_ratio || 0, format: 'number' },
                { label: 'EPS', value: stock.eps || 0, format: 'currency' },
                { label: 'Dividend Yield', value: stock.dividend_yield || 0, format: 'percentage' },
              ]}
            />
            <MetricsTable
              title="Performance Metrics"
              metrics={[
                { label: '52 Week High', value: stock.week_52_high || 0, format: 'currency' },
                { label: '52 Week Low', value: stock.week_52_low || 0, format: 'currency' },
                { label: 'YTD Return', value: stock.ytd_return || 0, format: 'percentage', change: stock.ytd_return },
                { label: 'Beta', value: stock.beta || 0, format: 'number' },
              ]}
            />
          </div>

          {/* Company Info */}
          {stock.description && (
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-3">About {stock.name}</h3>
              <p className="text-gray-600 leading-relaxed">{stock.description}</p>
            </div>
          )}
        </>
      )}

      {/* Empty State */}
      {!searchSymbol && !isLoading && (
        <div className="text-center py-12">
          <Search className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Search for a stock</h3>
          <p className="text-gray-600">Enter a stock symbol above to view detailed analysis and charts</p>
        </div>
      )}
    </div>
  );
}
