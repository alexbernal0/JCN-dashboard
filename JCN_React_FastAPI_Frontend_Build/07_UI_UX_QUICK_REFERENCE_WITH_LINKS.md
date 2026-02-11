# JCN Dashboard - UI/UX Quick Reference Guide

**Last Updated**: February 11, 2026  
**Purpose**: Quick reference for requesting UI changes, customizations, and design improvements  
**GitHub Repository**: https://github.com/alexbernal0/JCN-dashboard/tree/feature/fastapi-react

---

## 📂 Component File Links

### Layout Components
- **Header**: [`frontend/src/components/layout/Header.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/layout/Header.tsx)
- **Sidebar**: [`frontend/src/components/layout/Sidebar.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/layout/Sidebar.tsx)
- **MainLayout**: [`frontend/src/components/layout/MainLayout.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/layout/MainLayout.tsx)
- **Loading**: [`frontend/src/components/layout/Loading.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/layout/Loading.tsx)
- **ErrorMessage**: [`frontend/src/components/layout/ErrorMessage.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/layout/ErrorMessage.tsx)

### Chart Components
- **Portfolio Performance Chart**: [`frontend/src/components/charts/PortfolioPerformanceChart.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/charts/PortfolioPerformanceChart.tsx)
- **Sector Allocation Chart**: [`frontend/src/components/charts/SectorAllocationChart.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/charts/SectorAllocationChart.tsx)
- **Stock Price Chart**: [`frontend/src/components/charts/StockPriceChart.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/charts/StockPriceChart.tsx)
- **Portfolio Radar Chart**: [`frontend/src/components/charts/PortfolioRadarChart.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/charts/PortfolioRadarChart.tsx)

### Table Components
- **Stock Table**: [`frontend/src/components/tables/StockTable.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/tables/StockTable.tsx)
- **Metrics Table**: [`frontend/src/components/tables/MetricsTable.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/components/tables/MetricsTable.tsx)

### Page Components
- **Home**: [`frontend/src/pages/Home.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/pages/Home.tsx)
- **Portfolio Detail**: [`frontend/src/pages/PortfolioDetail.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/pages/PortfolioDetail.tsx)
- **Stock Analysis**: [`frontend/src/pages/StockAnalysis.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/pages/StockAnalysis.tsx)

### Configuration Files
- **App Router**: [`frontend/src/App.tsx`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/App.tsx)
- **Global Styles**: [`frontend/src/index.css`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/src/index.css)
- **Tailwind Config**: [`frontend/tailwind.config.js`](https://github.com/alexbernal0/JCN-dashboard/blob/feature/fastapi-react/frontend/tailwind.config.js)

---

# JCN Dashboard - UI/UX Quick Reference Guide

**Last Updated**: February 11, 2026  
**Purpose**: Quick reference for requesting UI changes, customizations, and design improvements

---

## Table of Contents

1. [Available Components](#available-components)
2. [Color Schemes & Themes](#color-schemes--themes)
3. [Typography & Fonts](#typography--fonts)
4. [Layout Patterns](#layout-patterns)
5. [Chart Customization](#chart-customization)
6. [Table Customization](#table-customization)
7. [Animation & Transitions](#animation--transitions)
8. [Responsive Design](#responsive-design)
9. [Icon Library](#icon-library)
10. [Common UI Change Requests](#common-ui-change-requests)
11. [Design Inspiration Links](#design-inspiration-links)

---

## Available Components

### Layout Components

#### 1. Header Component
**Location**: `frontend/src/components/layout/Header.tsx`

**Features**:
- Responsive navigation
- Mobile hamburger menu
- Logo/branding area
- Navigation links

**How to Request Changes**:
```
"Change the header background to dark blue"
"Add a search bar to the header"
"Make the header sticky on scroll"
"Change the logo to [upload image]"
"Add user profile dropdown to header"
```

---

#### 2. Sidebar Component
**Location**: `frontend/src/components/layout/Sidebar.tsx`

**Features**:
- Navigation menu
- Active state highlighting
- Quick stats display
- Collapsible sections

**How to Request Changes**:
```
"Make the sidebar collapsible"
"Change sidebar background to gradient"
"Add icons to sidebar menu items"
"Reorder the navigation items"
"Add a footer section to sidebar"
```

---

#### 3. MainLayout Component
**Location**: `frontend/src/components/layout/MainLayout.tsx`

**Features**:
- Page wrapper
- Consistent spacing
- Responsive grid

**How to Request Changes**:
```
"Add more padding around content"
"Change the max-width of content area"
"Add a breadcrumb navigation"
"Include a page title section"
```

---

### Chart Components

#### 1. Portfolio Performance Chart
**Location**: `frontend/src/components/charts/PortfolioPerformanceChart.tsx`

**Type**: Line + Area Chart  
**Library**: Apache ECharts  
**Features**: Benchmark comparison, tooltips, zoom controls

**How to Request Changes**:
```
"Change line color to green"
"Add more data points (daily instead of weekly)"
"Show percentage change instead of absolute values"
"Add a moving average line"
"Change chart height to 500px"
"Add a legend at the bottom"
"Make the area fill more transparent"
```

**Color Options**:
- `#3b82f6` (blue) - Current portfolio line
- `#ef4444` (red) - Benchmark line
- `#10b981` (green) - Positive performance
- `#f59e0b` (amber) - Warning/neutral

---

#### 2. Sector Allocation Chart
**Location**: `frontend/src/components/charts/SectorAllocationChart.tsx`

**Type**: Doughnut Pie Chart  
**Library**: Apache ECharts  
**Features**: Interactive legend, tooltips, percentage display

**How to Request Changes**:
```
"Change to a full pie chart (not doughnut)"
"Use different colors for sectors"
"Show values instead of percentages"
"Add a data table below the chart"
"Make the chart bigger/smaller"
"Change the color scheme to [specify colors]"
```

**Current Color Palette**:
- Technology: `#3b82f6` (blue)
- Healthcare: `#10b981` (green)
- Finance: `#f59e0b` (amber)
- Consumer: `#8b5cf6` (purple)
- Energy: `#ef4444` (red)

---

#### 3. Stock Price Chart
**Location**: `frontend/src/components/charts/StockPriceChart.tsx`

**Type**: Candlestick + Volume Chart  
**Library**: Apache ECharts  
**Features**: Zoom controls, volume bars, tooltips

**How to Request Changes**:
```
"Change candlestick colors (green/red to blue/orange)"
"Add moving average lines (50-day, 200-day)"
"Show MACD indicator below"
"Add RSI indicator"
"Change time range (1 month, 3 months, 1 year)"
"Make volume bars more prominent"
"Add Bollinger Bands"
```

**Candlestick Colors**:
- Up (bullish): `#10b981` (green)
- Down (bearish): `#ef4444` (red)

---

#### 4. Portfolio Radar Chart
**Location**: `frontend/src/components/charts/PortfolioRadarChart.tsx`

**Type**: Radar/Spider Chart  
**Library**: Apache ECharts  
**Features**: Multi-dimensional metrics, tooltips

**How to Request Changes**:
```
"Add more metrics (liquidity, momentum)"
"Change the shape to circular"
"Use different colors for each metric"
"Add comparison with benchmark"
"Make the chart bigger"
"Change axis labels"
```

**Current Metrics**:
- Quality Score
- Value Score
- Growth Score
- Momentum Score
- Stability Score

---

### Table Components

#### 1. Stock Table
**Location**: `frontend/src/components/tables/StockTable.tsx`

**Type**: Data Table  
**Library**: TanStack Table  
**Features**: Sorting, filtering, pagination, search

**How to Request Changes**:
```
"Add more columns (52-week high, dividend yield)"
"Change the default sort order"
"Add row highlighting on hover"
"Change pagination size (show 20 rows instead of 10)"
"Add export to CSV button"
"Make the table scrollable horizontally"
"Add color coding for positive/negative changes"
"Add sparkline charts in cells"
```

**Available Columns**:
- Symbol
- Name
- Price
- Change
- Change %
- Volume
- Market Cap
- Sector

---

#### 2. Metrics Table
**Location**: `frontend/src/components/tables/MetricsTable.tsx`

**Type**: Key-Value Table  
**Features**: Change indicators, color coding

**How to Request Changes**:
```
"Add more metrics rows"
"Change the layout to cards instead of table"
"Add trend indicators (up/down arrows)"
"Change color scheme for positive/negative"
"Add tooltips explaining each metric"
"Make it a horizontal layout"
```

---

### UI Elements

#### Loading States
**Location**: `frontend/src/components/layout/Loading.tsx`

**Types Available**:
- Spinner
- Card Skeleton
- Table Skeleton

**How to Request Changes**:
```
"Change spinner color to brand color"
"Add a loading message"
"Use a different animation (pulse, bounce)"
"Add a progress bar"
"Change skeleton colors"
```

---

#### Error Messages
**Location**: `frontend/src/components/layout/ErrorMessage.tsx`

**Features**: Error display, retry button

**How to Request Changes**:
```
"Change error message styling"
"Add an icon to error messages"
"Make errors dismissible"
"Add different error types (warning, info, success)"
"Change button colors"
```

---

## Color Schemes & Themes

### Current Color Palette

**Primary Colors**:
```css
Blue:    #3b82f6  /* Primary actions, links */
Green:   #10b981  /* Success, positive changes */
Red:     #ef4444  /* Errors, negative changes */
Amber:   #f59e0b  /* Warnings, neutral */
Purple:  #8b5cf6  /* Accent */
```

**Neutral Colors**:
```css
Gray-50:  #f9fafb  /* Backgrounds */
Gray-100: #f3f4f6  /* Light backgrounds */
Gray-200: #e5e7eb  /* Borders */
Gray-300: #d1d5db  /* Dividers */
Gray-400: #9ca3af  /* Disabled */
Gray-500: #6b7280  /* Secondary text */
Gray-600: #4b5563  /* Body text */
Gray-700: #374151  /* Headings */
Gray-800: #1f2937  /* Dark text */
Gray-900: #111827  /* Very dark text */
```

---

### How to Request Color Changes

**Example Requests**:
```
"Change the primary color from blue to purple"
"Use a darker shade of green for positive changes"
"Change all red colors to orange"
"Add a gradient background to cards"
"Use a dark theme instead of light"
"Change the sidebar background to a gradient from #1e3a8a to #3b82f6"
```

---

### Pre-defined Color Schemes

#### 1. **Professional Blue** (Current)
- Primary: Blue (#3b82f6)
- Success: Green (#10b981)
- Danger: Red (#ef4444)
- **Use Case**: Financial, corporate

#### 2. **Modern Purple**
- Primary: Purple (#8b5cf6)
- Success: Teal (#14b8a6)
- Danger: Pink (#ec4899)
- **Use Case**: Tech, creative

#### 3. **Classic Green**
- Primary: Green (#10b981)
- Success: Emerald (#059669)
- Danger: Red (#dc2626)
- **Use Case**: Finance, investment

#### 4. **Bold Orange**
- Primary: Orange (#f97316)
- Success: Green (#22c55e)
- Danger: Red (#ef4444)
- **Use Case**: Energetic, startup

#### 5. **Dark Mode**
- Background: Dark (#111827)
- Text: Light (#f9fafb)
- Primary: Blue (#60a5fa)
- **Use Case**: Reduced eye strain

**How to Request**:
```
"Switch to Modern Purple color scheme"
"Use Dark Mode theme"
"Apply Classic Green colors"
```

---

## Typography & Fonts

### Current Font Stack

**Sans-serif** (Default):
```css
font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 
             "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

---

### How to Change Fonts

#### Option 1: Google Fonts
**Popular Choices**:
- **Inter** - Modern, clean (great for dashboards)
- **Roboto** - Friendly, readable
- **Poppins** - Geometric, modern
- **Montserrat** - Bold, impactful
- **Open Sans** - Classic, versatile
- **Lato** - Warm, professional
- **Raleway** - Elegant, sophisticated

**How to Request**:
```
"Change font to Inter from Google Fonts"
"Use Poppins for headings and Inter for body text"
"Apply Montserrat font throughout"
```

**Google Fonts Link**: https://fonts.google.com

---

#### Option 2: Font Weights & Sizes

**Current Sizes**:
```css
text-xs:   0.75rem   (12px)
text-sm:   0.875rem  (14px)
text-base: 1rem      (16px)
text-lg:   1.125rem  (18px)
text-xl:   1.25rem   (20px)
text-2xl:  1.5rem    (24px)
text-3xl:  1.875rem  (30px)
text-4xl:  2.25rem   (36px)
```

**How to Request**:
```
"Make all headings bigger"
"Increase body text size from 16px to 18px"
"Use bolder font weights for headings"
"Make the sidebar text smaller"
```

---

## Layout Patterns

### Current Layout: Sidebar + Content

```
┌─────────────────────────────────────┐
│           Header                    │
├──────────┬──────────────────────────┤
│          │                          │
│ Sidebar  │      Main Content        │
│          │                          │
│          │                          │
└──────────┴──────────────────────────┘
```

---

### Alternative Layouts

#### 1. **Top Navigation**
```
┌─────────────────────────────────────┐
│     Header with Navigation          │
├─────────────────────────────────────┤
│                                     │
│         Main Content                │
│                                     │
└─────────────────────────────────────┘
```

**How to Request**:
```
"Move navigation to top header instead of sidebar"
"Use a horizontal navigation bar"
```

---

#### 2. **Dashboard Grid**
```
┌─────────────────────────────────────┐
│           Header                    │
├─────────────┬───────────────────────┤
│             │                       │
│   Stats     │    Main Chart         │
│   Cards     │                       │
│             ├───────────────────────┤
│             │    Secondary Chart    │
└─────────────┴───────────────────────┘
```

**How to Request**:
```
"Add a stats card section at the top"
"Create a dashboard grid layout"
"Show KPIs in cards above charts"
```

---

#### 3. **Tabs Layout**
```
┌─────────────────────────────────────┐
│           Header                    │
├─────────────────────────────────────┤
│  Tab1  │  Tab2  │  Tab3  │  Tab4   │
├─────────────────────────────────────┤
│                                     │
│         Tab Content                 │
│                                     │
└─────────────────────────────────────┘
```

**How to Request**:
```
"Organize portfolio sections into tabs"
"Add tabs for different time periods"
"Use tabs instead of separate pages"
```

---

### Spacing & Padding

**Current Spacing Scale** (Tailwind):
```css
p-0:  0px
p-1:  0.25rem  (4px)
p-2:  0.5rem   (8px)
p-4:  1rem     (16px)
p-6:  1.5rem   (24px)
p-8:  2rem     (32px)
p-12: 3rem     (48px)
```

**How to Request**:
```
"Add more spacing between sections"
"Reduce padding in cards"
"Make the layout more compact"
"Add breathing room around charts"
```

---

## Chart Customization

### ECharts Configuration Options

#### Colors
```javascript
color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
```

**How to Request**:
```
"Use a gradient color scheme for charts"
"Change chart colors to match brand"
"Use monochromatic colors (shades of blue)"
```

---

#### Grid & Axis
```javascript
grid: {
  left: '3%',
  right: '4%',
  bottom: '3%',
  top: '10%',
  containLabel: true
}
```

**How to Request**:
```
"Add more padding around chart"
"Show grid lines on chart"
"Hide axis labels"
"Change axis label colors"
```

---

#### Tooltips
```javascript
tooltip: {
  trigger: 'axis',
  backgroundColor: 'rgba(0,0,0,0.8)',
  textStyle: { color: '#fff' }
}
```

**How to Request**:
```
"Change tooltip background color"
"Show more information in tooltips"
"Format tooltip values as currency"
"Add custom tooltip styling"
```

---

#### Legend
```javascript
legend: {
  data: ['Portfolio', 'Benchmark'],
  bottom: 0
}
```

**How to Request**:
```
"Move legend to top"
"Hide legend"
"Change legend text color"
"Add icons to legend"
```

---

### Chart Type Alternatives

**Current**: Line, Area, Pie, Candlestick, Radar

**Available Alternatives**:
- **Bar Chart** - For comparisons
- **Scatter Plot** - For correlations
- **Heatmap** - For multi-dimensional data
- **Gauge Chart** - For single metrics
- **Funnel Chart** - For conversion flows
- **Treemap** - For hierarchical data
- **Sankey Diagram** - For flow visualization

**How to Request**:
```
"Change sector allocation to a treemap"
"Add a bar chart comparing portfolios"
"Show correlation as a scatter plot"
"Add a gauge chart for portfolio health score"
```

**ECharts Examples**: https://echarts.apache.org/examples/en/index.html

---

## Table Customization

### TanStack Table Features

#### Sorting
**Current**: Click column header to sort

**How to Request**:
```
"Add multi-column sorting"
"Change default sort order"
"Add sort indicators (arrows)"
"Disable sorting on certain columns"
```

---

#### Filtering
**Current**: Global search box

**How to Request**:
```
"Add column-specific filters"
"Add dropdown filters for sectors"
"Add range filters for price"
"Add date range picker"
```

---

#### Pagination
**Current**: 10 rows per page

**How to Request**:
```
"Show 25 rows per page"
"Add 'show all' option"
"Change pagination style"
"Add infinite scroll instead of pagination"
```

---

#### Cell Formatting

**How to Request**:
```
"Format prices as currency ($1,234.56)"
"Add color coding (green for positive, red for negative)"
"Add trend arrows in cells"
"Add sparkline charts in cells"
"Make certain columns bold"
"Add icons to cells"
```

---

#### Row Actions

**How to Request**:
```
"Add 'View Details' button to each row"
"Add row selection checkboxes"
"Add row hover effects"
"Add row expansion for more details"
"Add context menu on right-click"
```

---

### Table Alternatives

**Current**: Standard data table

**Alternatives**:
- **Card Grid** - For mobile-friendly display
- **List View** - For simpler display
- **Kanban Board** - For workflow visualization
- **Timeline View** - For chronological data

**How to Request**:
```
"Show stocks as cards instead of table"
"Use a list view on mobile"
"Add a timeline view for transactions"
```

---

## Animation & Transitions

### Current Animations

**Hover Effects**:
- Button hover: Scale + color change
- Card hover: Shadow increase
- Link hover: Color change

**Page Transitions**:
- Fade in on load
- Smooth scroll

---

### How to Request Animation Changes

```
"Add slide-in animation for sidebar"
"Make charts animate on load"
"Add bounce effect to buttons"
"Smooth scroll to top when navigating"
"Add loading skeleton animations"
"Fade in cards on scroll"
"Add ripple effect on button click"
```

---

### Animation Libraries

**Framer Motion** (Recommended):
```
"Add Framer Motion animations"
"Animate cards sliding in from left"
"Add page transition animations"
```

**Framer Motion Docs**: https://www.framer.com/motion/

---

## Responsive Design

### Current Breakpoints (Tailwind)

```css
sm:  640px   /* Small devices */
md:  768px   /* Tablets */
lg:  1024px  /* Laptops */
xl:  1280px  /* Desktops */
2xl: 1536px  /* Large desktops */
```

---

### Mobile Optimizations

**Current**:
- Hamburger menu on mobile
- Stacked layout on small screens
- Responsive tables (horizontal scroll)

**How to Request**:
```
"Hide sidebar on mobile by default"
"Show simplified charts on mobile"
"Change table to cards on mobile"
"Add bottom navigation on mobile"
"Make charts full-width on mobile"
```

---

## Icon Library

### Lucide React Icons

**Currently Used**:
- `Home` - Home page
- `TrendingUp` - Portfolio performance
- `PieChart` - Sector allocation
- `BarChart3` - Stock analysis
- `Settings` - Settings
- `Search` - Search functionality
- `Menu` - Mobile menu
- `X` - Close buttons
- `ChevronDown` - Dropdowns
- `AlertCircle` - Errors
- `Loader2` - Loading

**Browse All Icons**: https://lucide.dev/icons/

---

### How to Request Icon Changes

```
"Change home icon to a different style"
"Add icons to navigation menu"
"Use filled icons instead of outlined"
"Add custom icons for sectors"
"Change the loading spinner icon"
```

---

## Common UI Change Requests

### 1. Color & Theme Changes

```
✅ "Change primary color to purple"
✅ "Use a dark theme"
✅ "Apply a gradient background to the header"
✅ "Change card backgrounds to white"
✅ "Use softer colors throughout"
```

---

### 2. Layout Changes

```
✅ "Make the sidebar collapsible"
✅ "Move navigation to top"
✅ "Add a dashboard grid on home page"
✅ "Increase content width"
✅ "Add more spacing between sections"
```

---

### 3. Chart Changes

```
✅ "Change line chart colors"
✅ "Add moving average to stock chart"
✅ "Show percentage instead of absolute values"
✅ "Make charts bigger"
✅ "Add more data points"
✅ "Change pie chart to bar chart"
```

---

### 4. Table Changes

```
✅ "Add more columns to stock table"
✅ "Change default sort order"
✅ "Show 25 rows instead of 10"
✅ "Add color coding for positive/negative"
✅ "Add export to CSV button"
✅ "Show table as cards on mobile"
```

---

### 5. Typography Changes

```
✅ "Change font to Inter"
✅ "Make headings bigger"
✅ "Increase body text size"
✅ "Use bolder font weights"
✅ "Change font color to darker gray"
```

---

### 6. Component Changes

```
✅ "Add a search bar to header"
✅ "Show user profile in header"
✅ "Add quick stats cards to home page"
✅ "Add a footer"
✅ "Show notifications"
```

---

### 7. Animation Changes

```
✅ "Add fade-in animation on load"
✅ "Animate charts on scroll"
✅ "Add hover effects to cards"
✅ "Smooth scroll to sections"
✅ "Add loading animations"
```

---

### 8. Responsive Changes

```
✅ "Optimize for mobile"
✅ "Hide sidebar on tablets"
✅ "Stack charts vertically on mobile"
✅ "Add bottom navigation on mobile"
✅ "Make tables scrollable on mobile"
```

---

## Design Inspiration Links

### 1. **Dashboard UI Inspiration**

**Dribbble - Dashboard Designs**:
- https://dribbble.com/search/dashboard
- Browse thousands of dashboard designs
- Filter by color, style, industry

**Behance - Dashboard Projects**:
- https://www.behance.net/search/projects?search=dashboard
- Professional dashboard designs
- Case studies and process

**Awwwards - Dashboard Sites**:
- https://www.awwwards.com/websites/dashboard/
- Award-winning dashboard designs
- Interactive examples

---

### 2. **Financial Dashboard Examples**

**Robinhood**:
- https://robinhood.com
- Clean, minimal design
- Mobile-first approach

**Coinbase**:
- https://www.coinbase.com
- Professional, trustworthy
- Data-heavy charts

**Personal Capital**:
- https://www.personalcapital.com
- Comprehensive financial dashboard
- Great data visualization

**Mint**:
- https://mint.intuit.com
- User-friendly interface
- Clear data presentation

---

### 3. **Chart & Data Visualization**

**Observable**:
- https://observablehq.com/@d3/gallery
- D3.js examples
- Interactive visualizations

**Chart.js Examples**:
- https://www.chartjs.org/docs/latest/samples/
- Simple chart examples
- Various chart types

**ECharts Gallery**:
- https://echarts.apache.org/examples/en/index.html
- Extensive chart examples
- Interactive demos

**Plotly Examples**:
- https://plotly.com/javascript/
- Advanced visualizations
- 3D charts

---

### 4. **Color Scheme Generators**

**Coolors**:
- https://coolors.co
- Generate color palettes
- Export to various formats

**Adobe Color**:
- https://color.adobe.com
- Create color schemes
- Explore trending palettes

**Tailwind Color Palette**:
- https://tailwindcss.com/docs/customizing-colors
- Pre-defined color scales
- Accessible colors

**ColorHunt**:
- https://colorhunt.co
- Curated color palettes
- Trending colors

---

### 5. **UI Component Libraries**

**shadcn/ui**:
- https://ui.shadcn.com
- Beautiful components
- Built with Tailwind

**Headless UI**:
- https://headlessui.com
- Unstyled components
- Fully accessible

**Radix UI**:
- https://www.radix-ui.com
- Primitive components
- Highly customizable

**Ant Design**:
- https://ant.design
- Enterprise UI components
- Comprehensive library

---

### 6. **Icon Libraries**

**Lucide Icons** (Current):
- https://lucide.dev
- Clean, consistent icons
- Open source

**Heroicons**:
- https://heroicons.com
- Beautiful hand-crafted icons
- By Tailwind team

**Feather Icons**:
- https://feathericons.com
- Simply beautiful icons
- Open source

**Font Awesome**:
- https://fontawesome.com
- Extensive icon library
- Pro and free versions

---

### 7. **Typography Resources**

**Google Fonts**:
- https://fonts.google.com
- Free web fonts
- Easy integration

**Font Pair**:
- https://www.fontpair.co
- Font pairing suggestions
- Google Fonts combinations

**Typewolf**:
- https://www.typewolf.com
- Typography inspiration
- Font recommendations

---

### 8. **Design Systems**

**Material Design**:
- https://material.io/design
- Google's design system
- Comprehensive guidelines

**Apple Human Interface Guidelines**:
- https://developer.apple.com/design/human-interface-guidelines/
- Apple's design principles
- iOS/macOS patterns

**Microsoft Fluent Design**:
- https://www.microsoft.com/design/fluent/
- Microsoft's design system
- Windows patterns

---

### 9. **Animation Libraries**

**Framer Motion**:
- https://www.framer.com/motion/
- React animation library
- Easy to use

**GSAP**:
- https://greensock.com/gsap/
- Professional animation
- High performance

**Anime.js**:
- https://animejs.com
- Lightweight animation
- Simple API

---

### 10. **Accessibility Resources**

**WebAIM**:
- https://webaim.org
- Accessibility guidelines
- Testing tools

**A11y Project**:
- https://www.a11yproject.com
- Accessibility checklist
- Best practices

**WAVE**:
- https://wave.webaim.org
- Accessibility testing
- Browser extension

---

## How to Use This Guide

### Step 1: Identify What You Want to Change

Browse the sections above to find:
- Component you want to modify
- Design element you want to change
- Inspiration for new features

---

### Step 2: Use Example Requests

Copy and modify the example requests:
```
"Change [component] to [desired state]"
"Add [feature] to [location]"
"Use [style/color/font] for [element]"
```

---

### Step 3: Provide Visual References (Optional)

Include links to:
- Design inspiration (Dribbble, Behance)
- Similar dashboards
- Color palettes
- Specific examples

---

### Step 4: Be Specific

**Good Requests**:
✅ "Change the primary color from blue (#3b82f6) to purple (#8b5cf6)"
✅ "Add a 50-day moving average line to the stock price chart in orange"
✅ "Make the sidebar collapsible with an animated slide-out effect"

**Vague Requests**:
❌ "Make it look better"
❌ "Change the colors"
❌ "Add more features"

---

## Quick Request Templates

### Color Change
```
"Change the [element] color from [current color] to [new color]"
Example: "Change the primary button color from blue to purple"
```

### Layout Change
```
"Move [component] from [current location] to [new location]"
Example: "Move navigation from sidebar to top header"
```

### Component Addition
```
"Add a [component type] showing [data] to [location]"
Example: "Add a stats card showing total portfolio value to the home page"
```

### Chart Modification
```
"Change the [chart name] to show [data] using [chart type] with [color/style]"
Example: "Change the sector allocation to show values using a bar chart with gradient colors"
```

### Typography Change
```
"Change [text element] to use [font name] at [size] with [weight]"
Example: "Change headings to use Poppins at 24px with bold weight"
```

---

## Conclusion

This guide provides a comprehensive reference for customizing the JCN Dashboard UI/UX. Use the examples, links, and templates to:

- ✅ Request specific design changes
- ✅ Explore design inspiration
- ✅ Understand available options
- ✅ Communicate effectively about UI/UX

**Remember**: The more specific your request, the better the result!

---

**Need Help?**
- Review the component documentation in `03_FRONTEND_DOCUMENTATION.md`
- Check the design inspiration links above
- Provide visual references when possible
- Ask for clarification if needed

---

**Last Updated**: February 11, 2026
