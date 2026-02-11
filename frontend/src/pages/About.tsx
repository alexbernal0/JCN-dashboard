import { Building2, BarChart3, Shield, Zap } from 'lucide-react';

export function About() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">ℹ️ About</h1>
        <p className="text-secondary">Learn more about JCN Financial services and this dashboard</p>
      </div>

      {/* Company Info */}
      <div className="bg-surface border border-border rounded-lg p-8 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Building2 className="w-8 h-8 text-accent" />
          <h2 className="text-2xl font-semibold">JCN Financial & Tax Advisory Group, LLC</h2>
        </div>
        <p className="text-secondary text-lg leading-relaxed mb-4">
          Professional investment dashboard providing real-time portfolio tracking, analysis, and risk management tools.
        </p>
        <p className="text-secondary leading-relaxed">
          Our platform combines fundamental analysis from MotherDuck with real-time market data to provide comprehensive
          portfolio insights and investment decision support.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <BarChart3 className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Portfolio Tracking</h3>
          </div>
          <p className="text-secondary">
            Monitor multiple portfolios with real-time position tracking, performance metrics, and sector allocation analysis.
          </p>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <Shield className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Risk Management</h3>
          </div>
          <p className="text-secondary">
            Advanced risk assessment tools including volatility analysis, drawdown monitoring, and risk-adjusted returns.
          </p>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <Zap className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Real-Time Data</h3>
          </div>
          <p className="text-secondary">
            Live market data integration with automatic updates and caching for optimal performance.
          </p>
        </div>

        <div className="bg-surface border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <Building2 className="w-6 h-6 text-accent" />
            <h3 className="text-xl font-semibold">Fundamental Analysis</h3>
          </div>
          <p className="text-secondary">
            Deep fundamental metrics from MotherDuck including growth rates, margins, and quality scores.
          </p>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="bg-surface border border-border rounded-lg p-8">
        <h2 className="text-2xl font-semibold mb-4">Technology Stack</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <h4 className="font-semibold mb-2">Frontend</h4>
            <ul className="text-sm text-secondary space-y-1">
              <li>React 19</li>
              <li>TypeScript</li>
              <li>Tailwind CSS</li>
              <li>ECharts</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Backend</h4>
            <ul className="text-sm text-secondary space-y-1">
              <li>FastAPI</li>
              <li>Python</li>
              <li>Uvicorn</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Data</h4>
            <ul className="text-sm text-secondary space-y-1">
              <li>MotherDuck</li>
              <li>yfinance</li>
              <li>DuckDB</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Deployment</h4>
            <ul className="text-sm text-secondary space-y-1">
              <li>Railway</li>
              <li>GitHub</li>
              <li>CI/CD</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
