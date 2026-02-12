import { useQuery, useQueryClient } from '@tanstack/react-query';

const API_BASE_URL = 'https://jcn-dashboard-production.up.railway.app/api/v1';

export interface StockHolding {
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

export interface PortfolioData {
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

const fetchPortfolio = async (portfolioId: string): Promise<PortfolioData> => {
  const response = await fetch(`${API_BASE_URL}/portfolios/${portfolioId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch portfolio: ${response.statusText}`);
  }
  return response.json();
};

export function usePortfolio(portfolioId: string) {
  return useQuery({
    queryKey: ['portfolio', portfolioId],
    queryFn: () => fetchPortfolio(portfolioId),
    staleTime: 1000 * 60 * 10, // Data stays fresh for 10 minutes
    cacheTime: 1000 * 60 * 30, // Keep in cache for 30 minutes
    refetchOnWindowFocus: false,
    retry: 2,
  });
}

// Hook to prefetch all portfolios
export function usePrefetchPortfolios() {
  const queryClient = useQueryClient();

  const prefetchAll = () => {
    const portfolios = ['persistent_value', 'olivia_growth', 'pure_alpha'];
    portfolios.forEach((portfolioId) => {
      queryClient.prefetchQuery({
        queryKey: ['portfolio', portfolioId],
        queryFn: () => fetchPortfolio(portfolioId),
        staleTime: 1000 * 60 * 10,
      });
    });
  };

  return { prefetchAll };
}
