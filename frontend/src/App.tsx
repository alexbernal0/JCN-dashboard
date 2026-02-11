import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardLayout } from './components/DashboardLayout';
import Landing from './pages/Landing';
import { Home } from './pages/Home';
import { PersistentValue } from './pages/PersistentValue';
import { OliviaGrowth } from './pages/OliviaGrowth';
import { PureAlpha } from './pages/PureAlpha';
import { StockAnalysis } from './pages/StockAnalysis';
import { MarketAnalysis } from './pages/MarketAnalysis';
import { RiskManagement } from './pages/RiskManagement';
import { About } from './pages/About';

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
          {/* Landing page (no sidebar) */}
          <Route path="/" element={<Landing />} />
          
          {/* Dashboard pages (with sidebar) */}
          <Route path="/dashboard" element={
            <DashboardLayout>
              <Home />
            </DashboardLayout>
          } />
          
          {/* Portfolio pages */}
          <Route path="/portfolio/persistent-value" element={
            <DashboardLayout>
              <PersistentValue />
            </DashboardLayout>
          } />
          
          <Route path="/portfolio/olivia-growth" element={
            <DashboardLayout>
              <OliviaGrowth />
            </DashboardLayout>
          } />
          
          <Route path="/portfolio/pure-alpha" element={
            <DashboardLayout>
              <PureAlpha />
            </DashboardLayout>
          } />
          
          {/* Analysis pages */}
          <Route path="/stock-analysis" element={
            <DashboardLayout>
              <StockAnalysis />
            </DashboardLayout>
          } />
          
          <Route path="/market-analysis" element={
            <DashboardLayout>
              <MarketAnalysis />
            </DashboardLayout>
          } />
          
          <Route path="/risk-management" element={
            <DashboardLayout>
              <RiskManagement />
            </DashboardLayout>
          } />
          
          {/* About page */}
          <Route path="/about" element={
            <DashboardLayout>
              <About />
            </DashboardLayout>
          } />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
