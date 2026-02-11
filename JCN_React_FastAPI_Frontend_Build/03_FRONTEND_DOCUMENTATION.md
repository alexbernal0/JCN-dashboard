# Frontend Documentation - React + TypeScript

**Last Updated:** February 11, 2026  
**Status:** 🔄 In Progress (Scaffold Complete, Components Pending)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Component Breakdown](#component-breakdown)
5. [State Management](#state-management)
6. [Data Fetching](#data-fetching)
7. [Charts & Visualizations](#charts--visualizations)
8. [Remaining Work](#remaining-work)

---

## Architecture Overview

### Design Principles

1. **Component-Based** - Reusable, composable UI components
2. **Type-Safe** - TypeScript for all code
3. **Performance-First** - Code splitting, lazy loading, memoization
4. **Responsive** - Mobile-first design
5. **Accessible** - WCAG 2.1 AA compliance

### Technology Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | React | 19.0.0 | UI library |
| **Language** | TypeScript | 5.6.3 | Type safety |
| **Build Tool** | Vite | 6.0.5 | Fast dev server + bundling |
| **Data Fetching** | TanStack Query | 5.x | Server state management |
| **Charts** | Apache ECharts | 5.x | Data visualizations |
| **Tables** | TanStack Table | 8.x | Advanced data tables |
| **UI Components** | shadcn/ui | Latest | Pre-built components |
| **Styling** | Tailwind CSS | 4.x | Utility-first CSS |
| **Icons** | Lucide React | Latest | Icon library |
| **HTTP Client** | Axios | 1.x | API requests |

---

## Project Structure

```
frontend/src/
├── main.tsx                    # Application entry point
├── App.tsx                     # Root component + routing
├── vite-env.d.ts              # Vite type definitions
│
├── components/                 # Reusable UI components
│   ├── ui/                    # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── charts/                # Chart components
│   │   ├── PortfolioPerformanceChart.tsx
│   │   ├── StockPriceChart.tsx
│   │   └── RadarChart.tsx
│   ├── tables/                # Table components
│   │   └── StockTable.tsx
│   └── layout/                # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
│
├── pages/                      # Page components
│   ├── Home.tsx
│   ├── PortfolioDetail.tsx
│   ├── StockAnalysis.tsx
│   └── About.tsx
│
├── hooks/                      # Custom React hooks
│   ├── usePortfolio.ts        # Portfolio data fetching
│   ├── useStock.ts            # Stock data fetching
│   └── useDebounce.ts         # Utility hooks
│
├── services/                   # API client
│   ├── api.ts                 # Axios instance + interceptors
│   ├── portfolioService.ts    # Portfolio API calls
│   └── stockService.ts        # Stock API calls
│
├── types/                      # TypeScript types
│   ├── portfolio.ts
│   ├── stock.ts
│   └── api.ts
│
├── lib/                        # Utilities
│   ├── utils.ts               # Helper functions
│   └── constants.ts           # App constants
│
└── styles/                     # Global styles
    └── globals.css            # Tailwind + custom CSS
```

---

## Component Breakdown

### 1. Layout Components

#### Header Component
```typescript
// components/layout/Header.tsx
interface HeaderProps {
  title: string;
  subtitle?: string;
}

export function Header({ title, subtitle }: HeaderProps) {
  return (
    <header className="border-b">
      <div className="container py-6">
        <h1 className="text-3xl font-bold">{title}</h1>
        {subtitle && <p className="text-muted-foreground">{subtitle}</p>}
      </div>
    </header>
  );
}
```

#### Sidebar Component
```typescript
// components/layout/Sidebar.tsx
const navigation = [
  { name: 'Home', href: '/', icon: HomeIcon },
  { name: 'Persistent Value', href: '/portfolio/persistent_value', icon: TrendingUpIcon },
  { name: 'Olivia Growth', href: '/portfolio/olivia_growth', icon: RocketIcon },
  // ...
];

export function Sidebar() {
  return (
    <aside className="w-64 border-r">
      <nav className="space-y-1 p-4">
        {navigation.map((item) => (
          <Link key={item.name} to={item.href} className="...">
            <item.icon className="mr-3 h-5 w-5" />
            {item.name}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
```

---

### 2. Chart Components

#### Portfolio Performance Chart (ECharts)
```typescript
// components/charts/PortfolioPerformanceChart.tsx
import ReactECharts from 'echarts-for-react';

interface PortfolioPerformanceChartProps {
  data: {
    dates: string[];
    values: number[];
    benchmark: number[];
  };
}

export function PortfolioPerformanceChart({ data }: PortfolioPerformanceChartProps) {
  const option = {
    title: { text: 'Portfolio Performance' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['Portfolio', 'Benchmark'] },
    xAxis: {
      type: 'category',
      data: data.dates,
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '{value}%' },
    },
    series: [
      {
        name: 'Portfolio',
        type: 'line',
        data: data.values,
        smooth: true,
        lineStyle: { width: 3 },
        itemStyle: { color: '#3b82f6' },
      },
      {
        name: 'Benchmark',
        type: 'line',
        data: data.benchmark,
        smooth: true,
        lineStyle: { width: 2, type: 'dashed' },
        itemStyle: { color: '#94a3b8' },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '400px' }} />;
}
```

#### Stock Price Chart (Candlestick)
```typescript
// components/charts/StockPriceChart.tsx
export function StockPriceChart({ data }: StockPriceChartProps) {
  const option = {
    title: { text: 'Stock Price' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: data.dates,
    },
    yAxis: {
      type: 'value',
      scale: true,
    },
    series: [
      {
        type: 'candlestick',
        data: data.ohlc, // [open, close, low, high]
        itemStyle: {
          color: '#ef4444',  // Up candle
          color0: '#22c55e', // Down candle
          borderColor: '#ef4444',
          borderColor0: '#22c55e',
        },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '500px' }} />;
}
```

---

### 3. Table Components

#### Stock Table (TanStack Table)
```typescript
// components/tables/StockTable.tsx
import { useReactTable, getCoreRowModel, getSortedRowModel } from '@tanstack/react-table';

const columns = [
  {
    accessorKey: 'symbol',
    header: 'Symbol',
  },
  {
    accessorKey: 'name',
    header: 'Name',
  },
  {
    accessorKey: 'current_price',
    header: 'Price',
    cell: ({ getValue }) => formatCurrency(getValue()),
  },
  {
    accessorKey: 'change_percent',
    header: 'Change',
    cell: ({ getValue }) => (
      <span className={getValue() > 0 ? 'text-green-600' : 'text-red-600'}>
        {getValue()}%
      </span>
    ),
  },
  // ... more columns
];

export function StockTable({ data }: StockTableProps) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.column.columnDef.header}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.map((row) => (
            <TableRow key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
```

---

## State Management

### TanStack Query for Server State

**Why TanStack Query?**
- ✅ Automatic caching
- ✅ Background refetching
- ✅ Optimistic updates
- ✅ Request deduplication
- ✅ Pagination & infinite scroll support

**Setup:**

```typescript
// main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);
```

**Usage:**

```typescript
// hooks/usePortfolio.ts
import { useQuery } from '@tanstack/react-query';
import { portfolioService } from '../services/portfolioService';

export function usePortfolio(portfolioId: string) {
  return useQuery({
    queryKey: ['portfolio', portfolioId],
    queryFn: () => portfolioService.getPortfolioSummary(portfolioId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// In component:
function PortfolioDetail({ portfolioId }: Props) {
  const { data, isLoading, error } = usePortfolio(portfolioId);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return <PortfolioView data={data} />;
}
```

---

## Data Fetching

### API Client Setup

```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Handle errors globally
    if (error.response?.status === 401) {
      // Redirect to login
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Service Layer

```typescript
// services/portfolioService.ts
import api from './api';
import type { PortfolioSummary } from '../types/portfolio';

export const portfolioService = {
  async getPortfolioSummary(portfolioId: string): Promise<PortfolioSummary> {
    return api.get(`/api/v1/portfolios/${portfolioId}`);
  },

  async listPortfolios() {
    return api.get('/api/v1/portfolios');
  },
};
```

---

## Charts & Visualizations

### ECharts Integration

**Installation:**
```bash
pnpm add echarts echarts-for-react
```

**Available Chart Types for JCN Dashboard:**

1. **Line Chart** - Portfolio performance over time
2. **Candlestick Chart** - Stock price OHLC data
3. **Bar Chart** - Sector allocation
4. **Pie Chart** - Portfolio composition
5. **Radar Chart** - Portfolio quality metrics
6. **Scatter Plot** - Risk vs return analysis
7. **Heatmap** - Correlation matrix

**Performance Tips:**
- Use `notMerge: true` for dynamic updates
- Implement `shouldComponentUpdate` for large datasets
- Use `lazyUpdate: true` for better performance
- Enable `dataZoom` for large time series

---

## Remaining Work

### Phase 1: Core Components (4-5 hours)

- [ ] **Layout Components** (1 hour)
  - [ ] Header with navigation
  - [ ] Sidebar with portfolio links
  - [ ] Footer with credits

- [ ] **Chart Components** (2 hours)
  - [ ] Portfolio performance line chart
  - [ ] Stock price candlestick chart
  - [ ] Sector allocation pie chart
  - [ ] Portfolio radar chart

- [ ] **Table Components** (1 hour)
  - [ ] Stock table with sorting/filtering
  - [ ] Performance metrics table

- [ ] **Page Components** (1 hour)
  - [ ] Home page
  - [ ] Portfolio detail page
  - [ ] Stock analysis page

### Phase 2: Integration & Polish (2-3 hours)

- [ ] **API Integration** (1 hour)
  - [ ] Connect all components to backend
  - [ ] Add loading states
  - [ ] Add error handling

- [ ] **Responsive Design** (1 hour)
  - [ ] Mobile layout
  - [ ] Tablet layout
  - [ ] Desktop layout

- [ ] **Performance** (1 hour)
  - [ ] Code splitting
  - [ ] Lazy loading
  - [ ] Image optimization

### Phase 3: Testing & Documentation (1 hour)

- [ ] **Testing**
  - [ ] Component tests
  - [ ] Integration tests

- [ ] **Documentation**
  - [ ] Component documentation
  - [ ] Usage examples

---

## Next Steps

1. Implement layout components
2. Implement chart components with ECharts
3. Implement table components with TanStack Table
4. Connect to backend API
5. Add responsive design
6. Test and deploy

---

**Status:** 🔄 Scaffold complete, components in progress
