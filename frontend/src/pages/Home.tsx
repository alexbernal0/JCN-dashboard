import { Link } from 'react-router-dom';
import { TrendingUp, Sprout, Zap, BarChart3, Globe, Shield } from 'lucide-react';

export function Home() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">JCN Financial & Tax Advisory Group, LLC</h1>
        <h2 className="text-2xl text-secondary">Investment Dashboard</h2>
      </div>

      <div className="border-t border-border my-8" />

      {/* Welcome Section */}
      <div className="mb-12">
        <h2 className="text-3xl font-bold mb-4">Welcome to Your Investment Dashboard</h2>
        <p className="text-secondary text-lg">
          Select a portfolio or analysis tool from the sidebar to get started.
        </p>
      </div>

      {/* Available Portfolios */}
      <div className="mb-12">
        <h3 className="text-2xl font-semibold mb-6">Available Portfolios:</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link to="/portfolio/persistent-value" className="group">
            <div className="bg-surface rounded-lg p-6 hover:ring-2 hover:ring-accent transition-all">
              <div className="flex items-center gap-3 mb-3">
                <TrendingUp className="w-6 h-6 text-accent" />
                <h4 className="text-lg font-semibold group-hover:text-accent transition-colors">
                  Persistent Value
                </h4>
              </div>
              <p className="text-secondary text-sm">
                Value-focused investment strategy with long-term growth potential
              </p>
            </div>
          </Link>

          <Link to="/portfolio/olivia-growth" className="group">
            <div className="bg-surface rounded-lg p-6 hover:ring-2 hover:ring-accent transition-all">
              <div className="flex items-center gap-3 mb-3">
                <Sprout className="w-6 h-6 text-accent" />
                <h4 className="text-lg font-semibold group-hover:text-accent transition-colors">
                  Olivia Growth
                </h4>
              </div>
              <p className="text-secondary text-sm">
                Growth-focused investment strategy
              </p>
            </div>
          </Link>

          <Link to="/portfolio/pure-alpha" className="group">
            <div className="bg-surface rounded-lg p-6 hover:ring-2 hover:ring-accent transition-all">
              <div className="flex items-center gap-3 mb-3">
                <Zap className="w-6 h-6 text-accent" />
                <h4 className="text-lg font-semibold group-hover:text-accent transition-colors">
                  Pure Alpha
                </h4>
              </div>
              <p className="text-secondary text-sm">
                Alpha-generating investment strategy
              </p>
            </div>
          </Link>
        </div>
      </div>

      {/* Analysis Tools */}
      <div className="mb-12">
        <h3 className="text-2xl font-semibold mb-6">Analysis Tools:</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link to="/stock-analysis" className="group">
            <div className="bg-surface rounded-lg p-6 hover:ring-2 hover:ring-accent transition-all">
              <div className="flex items-center gap-3 mb-3">
                <BarChart3 className="w-6 h-6 text-accent" />
                <h4 className="text-lg font-semibold group-hover:text-accent transition-colors">
                  Stock Analysis
                </h4>
              </div>
              <p className="text-secondary text-sm">
                Individual stock research and analysis
              </p>
            </div>
          </Link>

          <Link to="/market-analysis" className="group">
            <div className="bg-surface rounded-lg p-6 hover:ring-2 hover:ring-accent transition-all">
              <div className="flex items-center gap-3 mb-3">
                <Globe className="w-6 h-6 text-accent" />
                <h4 className="text-lg font-semibold group-hover:text-accent transition-colors">
                  Market Analysis
                </h4>
              </div>
              <p className="text-secondary text-sm">
                Broad market trends and sector analysis
              </p>
            </div>
          </Link>

          <Link to="/risk-management" className="group">
            <div className="bg-surface rounded-lg p-6 hover:ring-2 hover:ring-accent transition-all">
              <div className="flex items-center gap-3 mb-3">
                <Shield className="w-6 h-6 text-accent" />
                <h4 className="text-lg font-semibold group-hover:text-accent transition-colors">
                  Risk Management
                </h4>
              </div>
              <p className="text-secondary text-sm">
                Portfolio risk assessment and management
              </p>
            </div>
          </Link>
        </div>
      </div>

      <div className="border-t border-border my-8" />

      {/* Quick Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="bg-accent/10 border border-accent/20 rounded-lg p-6">
          <h4 className="font-semibold mb-2">Real-time Data</h4>
          <p className="text-sm text-secondary">
            All portfolio data is updated in real-time using market feeds
          </p>
        </div>

        <div className="bg-accent/10 border border-accent/20 rounded-lg p-6">
          <h4 className="font-semibold mb-2">Comprehensive Analysis</h4>
          <p className="text-sm text-secondary">
            Detailed performance metrics and risk assessments
          </p>
        </div>

        <div className="bg-accent/10 border border-accent/20 rounded-lg p-6">
          <h4 className="font-semibold mb-2">Multi-Portfolio</h4>
          <p className="text-sm text-secondary">
            Track multiple investment strategies simultaneously
          </p>
        </div>
      </div>

      <div className="border-t border-border my-8" />

      {/* Footer */}
      <div className="text-center text-sm text-secondary">
        JCN Financial & Tax Advisory Group, LLC - Built with React
      </div>
    </div>
  );
}
