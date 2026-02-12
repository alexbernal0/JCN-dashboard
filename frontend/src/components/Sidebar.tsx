import { Link, useLocation } from 'react-router-dom';
import { Moon, Sun, LayoutDashboard, TrendingUp, Sprout, Zap, BarChart3, Globe, Shield, Info, RefreshCw } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useQueryClient } from '@tanstack/react-query';

export function Sidebar() {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const queryClient = useQueryClient();

  const handleRefreshData = () => {
    // Invalidate all portfolio queries to force refetch
    queryClient.invalidateQueries({ queryKey: ['portfolio'] });
    // Show a brief toast notification (optional)
    console.log('Refreshing all portfolio data...');
  };

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  ];

  const portfolioItems = [
    { path: '/portfolio/persistent-value', icon: TrendingUp, label: 'Persistent Value' },
    { path: '/portfolio/olivia-growth', icon: Sprout, label: 'Olivia Growth' },
    { path: '/portfolio/pure-alpha', icon: Zap, label: 'Pure Alpha' },
  ];

  const analysisItems = [
    { path: '/stock-analysis', icon: BarChart3, label: 'Stock Analysis' },
    { path: '/market-analysis', icon: Globe, label: 'Market Analysis' },
    { path: '/risk-management', icon: Shield, label: 'Risk Management' },
  ];

  const otherItems = [
    { path: '/about', icon: Info, label: 'About' },
  ];

  return (
    <aside className="w-60 h-screen bg-background border-r border-border fixed left-0 top-0 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <Link to="/" className="text-2xl font-semibold tracking-wider text-accent hover:opacity-80 transition-opacity">
          JCN.AI
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {/* Main */}
        <div className="mb-6">
          {navItems.map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={`
                flex items-center gap-3 px-6 py-3 text-sm font-medium transition-all
                ${isActive(path)
                  ? 'bg-surface text-primary border-l-3 border-accent'
                  : 'text-secondary hover:text-primary hover:bg-surface/50'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span>{label}</span>
            </Link>
          ))}
        </div>

        {/* Portfolios */}
        <div className="mb-6">
          <div className="px-6 py-2 text-xs font-semibold uppercase tracking-wider text-secondary">
            Portfolios
          </div>
          {portfolioItems.map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={`
                flex items-center gap-3 px-6 py-3 text-sm font-medium transition-all
                ${isActive(path)
                  ? 'bg-surface text-primary border-l-3 border-accent'
                  : 'text-secondary hover:text-primary hover:bg-surface/50'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span>{label}</span>
            </Link>
          ))}
        </div>

        {/* Analysis */}
        <div className="mb-6">
          <div className="px-6 py-2 text-xs font-semibold uppercase tracking-wider text-secondary">
            Analysis
          </div>
          {analysisItems.map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={`
                flex items-center gap-3 px-6 py-3 text-sm font-medium transition-all
                ${isActive(path)
                  ? 'bg-surface text-primary border-l-3 border-accent'
                  : 'text-secondary hover:text-primary hover:bg-surface/50'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span>{label}</span>
            </Link>
          ))}
        </div>

        {/* Other */}
        <div className="border-t border-border pt-4">
          {otherItems.map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={`
                flex items-center gap-3 px-6 py-3 text-sm font-medium transition-all
                ${isActive(path)
                  ? 'bg-surface text-primary border-l-3 border-accent'
                  : 'text-secondary hover:text-primary hover:bg-surface/50'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span>{label}</span>
            </Link>
          ))}
          
          {/* Refresh Data Button */}
          <button
            onClick={handleRefreshData}
            className="w-full flex items-center gap-3 px-6 py-3 text-sm font-medium transition-all text-secondary hover:text-primary hover:bg-surface/50"
          >
            <RefreshCw className="w-5 h-5" />
            <span>Refresh Data</span>
          </button>
        </div>
      </nav>

      {/* Theme Toggle */}
      <div className="p-4 border-t border-border">
        <button
          onClick={toggleTheme}
          className="w-full flex items-center justify-between px-4 py-3 rounded-lg bg-surface hover:bg-surface/80 transition-all text-sm font-medium"
        >
          <span className="text-secondary">{theme === 'dark' ? 'Dark Mode' : 'Light Mode'}</span>
          {theme === 'dark' ? (
            <Moon className="w-5 h-5 text-accent" />
          ) : (
            <Sun className="w-5 h-5 text-accent" />
          )}
        </button>
      </div>
    </aside>
  );
}
