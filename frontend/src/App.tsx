import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from './components/layout/MainLayout';
import Landing from './pages/Landing';
import { Home } from './pages/Home';
import { PortfolioDetail } from './pages/PortfolioDetail';
import { StockAnalysis } from './pages/StockAnalysis';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          
          <Route path="/dashboard" element={
            <MainLayout title="Home">
              <Home />
            </MainLayout>
          } />
          
          <Route path="/portfolio/persistent_value" element={
            <MainLayout title="Persistent Value" subtitle="Value investing portfolio">
              <PortfolioDetail portfolioId="persistent_value" portfolioName="Persistent Value" />
            </MainLayout>
          } />
          
          <Route path="/portfolio/olivia_growth" element={
            <MainLayout title="Olivia Growth" subtitle="Growth investing portfolio">
              <PortfolioDetail portfolioId="olivia_growth" portfolioName="Olivia Growth" />
            </MainLayout>
          } />
          
          <Route path="/stocks" element={
            <MainLayout title="Stock Analysis" subtitle="Search and analyze stocks">
              <StockAnalysis />
            </MainLayout>
          } />
          
          <Route path="/risk" element={
            <MainLayout title="Risk Management" subtitle="Portfolio risk analysis">
              <div className="text-center py-12">
                <h2 className="text-2xl font-bold text-gray-900">Risk Management</h2>
                <p className="text-gray-600 mt-2">Coming soon...</p>
              </div>
            </MainLayout>
          } />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
