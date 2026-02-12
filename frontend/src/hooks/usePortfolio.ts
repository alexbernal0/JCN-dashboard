import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect } from 'react';

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
  fundamentals?: any;
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

const loadStaticSnapshot = async (portfolioId: string): Promise<PortfolioData> => {
  const response = await fetch(`/data/${portfolioId}.json`);
  if (!response.ok) {
    throw new Error(`Failed to load static snapshot for ${portfolioId}`);
  }
  return response.json();
};

const fetchPortfolioFromAPI = async (portfolioId: string): Promise<PortfolioData> => {
  const response = await fetch(`${API_BASE_URL}/portfolios/${portfolioId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch portfolio: ${response.statusText}`);
  }
  return response.json();
};

export function usePortfolio(portfolioId: string) {
  const [staticData, setStaticData] = useState<PortfolioData | null>(null);
  const [isLoadingStatic, setIsLoadingStatic] = useState(true);

  useEffect(() => {
    loadStaticSnapshot(portfolioId)
      .then((data) => {
        setStaticData(data);
        setIsLoadingStatic(false);
      })
      .catch((error) => {
        console.error('Failed to load static snapshot:', error);
        setIsLoadingStatic(false);
      });
  }, [portfolioId]);

  const { data: apiData, isLoading: isLoadingAPI, isError, error, refetch } = useQuery({
    queryKey: ['portfolio', portfolioId],
    queryFn: () => fetchPortfolioFromAPI(portfolioId),
    staleTime: 1000 * 60 * 10,
    cacheTime: 1000 * 60 * 30,
    refetchOnWindowFocus: false,
    retry: 2,
    enabled: !isLoadingStatic,
  });

  const data = apiData || staticData;
  const isLoading = isLoadingStatic && !staticData && isLoadingAPI && !apiData;

  return {
    data,
    isLoading,
    isError,
    error,
    refetch,
    isUsingSnapshot: !apiData && !!staticData,
  };
}

export function usePrefetchPortfolios() {
  const queryClient = useQueryClient();

  const prefetchAll = () => {
    const portfolios = ['persistent_value', 'olivia_growth', 'pure_alpha'];
    portfolios.forEach((portfolioId) => {
      queryClient.prefetchQuery({
        queryKey: ['portfolio', portfolioId],
        queryFn: () => fetchPortfolioFromAPI(portfolioId),
        staleTime: 1000 * 60 * 10,
      });
    });
  };

  return { prefetchAll };
}
