import { Link } from 'react-router-dom';
import { TrendingUp, Rocket, Search, BarChart3 } from 'lucide-react';

export function Home() {
  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome to JCN Dashboard</h1>
        <p className="text-blue-100">
          Professional financial analysis and portfolio management
        </p>
      </div>

      {/* Portfolio Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Persistent Value Portfolio */}
        <Link 
          to="/portfolio/persistent_value"
          className="bg-white rounded-lg border p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Persistent Value</h2>
                <p className="text-sm text-gray-500">Value investing strategy</p>
              </div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Total Stocks</span>
              <span className="font-semibold text-gray-900">~15</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Strategy</span>
              <span className="font-semibold text-gray-900">Value + Quality</span>
            </div>
          </div>
        </Link>

        {/* Olivia Growth Portfolio */}
        <Link 
          to="/portfolio/olivia_growth"
          className="bg-white rounded-lg border p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Rocket className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Olivia Growth</h2>
                <p className="text-sm text-gray-500">Growth investing strategy</p>
              </div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Total Stocks</span>
              <span className="font-semibold text-gray-900">~15</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Strategy</span>
              <span className="font-semibold text-gray-900">Growth + Momentum</span>
            </div>
          </div>
        </Link>
      </div>

      {/* Tools Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link 
          to="/stocks"
          className="bg-white rounded-lg border p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Search className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-lg font-bold text-gray-900">Stock Analysis</h3>
          </div>
          <p className="text-sm text-gray-600">
            Search and analyze individual stocks with detailed metrics and charts
          </p>
        </Link>

        <Link 
          to="/risk"
          className="bg-white rounded-lg border p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-red-600" />
            </div>
            <h3 className="text-lg font-bold text-gray-900">Risk Management</h3>
          </div>
          <p className="text-sm text-gray-600">
            Portfolio risk analysis, correlation matrices, and stress testing
          </p>
        </Link>
      </div>

      {/* Quick Stats */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Stats</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Total Portfolios</p>
            <p className="text-2xl font-bold text-gray-900">2</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Stocks</p>
            <p className="text-2xl font-bold text-gray-900">~30</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Data Source</p>
            <p className="text-2xl font-bold text-gray-900">Yahoo Finance</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Update Frequency</p>
            <p className="text-2xl font-bold text-gray-900">Real-time</p>
          </div>
        </div>
      </div>
    </div>
  );
}
