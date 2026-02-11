import { Link, useLocation } from 'react-router-dom';
import { Home, TrendingUp, Rocket, Search, BarChart3 } from 'lucide-react';

const navigation = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Persistent Value', href: '/portfolio/persistent_value', icon: TrendingUp },
  { name: 'Olivia Growth', href: '/portfolio/olivia_growth', icon: Rocket },
  { name: 'Stock Analysis', href: '/stocks', icon: Search },
  { name: 'Risk Management', href: '/risk', icon: BarChart3 },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 border-r bg-gray-50 min-h-screen">
      <div className="p-4">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Navigation
        </h2>
        <nav className="space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${isActive 
                    ? 'bg-blue-600 text-white shadow-sm' 
                    : 'text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Portfolio Summary Section */}
        <div className="mt-8 pt-6 border-t">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Quick Stats
          </h2>
          <div className="space-y-3">
            <div className="bg-white rounded-lg p-3 border">
              <p className="text-xs text-gray-500">Total Portfolios</p>
              <p className="text-2xl font-bold text-gray-900">2</p>
            </div>
            <div className="bg-white rounded-lg p-3 border">
              <p className="text-xs text-gray-500">Total Stocks</p>
              <p className="text-2xl font-bold text-gray-900">~30</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
