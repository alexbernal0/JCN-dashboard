# Tailwind CSS v3 Reference Guide for JCN Dashboard

## Official Documentation
- **Main Docs**: https://v3.tailwindcss.com/docs
- **Installation**: https://v3.tailwindcss.com/docs/installation
- **Configuration**: https://v3.tailwindcss.com/docs/configuration

---

## Project Setup

### Our Configuration
- **Version**: Tailwind CSS 3.4.x
- **PostCSS**: Configured with autoprefixer
- **Build Tool**: Vite
- **CSS File**: `frontend/src/index.css`

### Installation Commands
```bash
npm install -D tailwindcss@^3.4.0 postcss@^8.4.0 autoprefixer@^10.4.0
npx tailwindcss init -p
```

### CSS Import (index.css)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## Layout Utilities (Used in JCN Dashboard)

### Full-Screen Layouts
```jsx
// Landing page - full viewport coverage
<div className="fixed inset-0 w-full h-full">
  {/* Content */}
</div>

// Alternative with min-height
<div className="min-h-screen w-full">
  {/* Content */}
</div>
```

**Classes:**
- `fixed` - Fixed positioning
- `inset-0` - top/right/bottom/left all 0
- `w-full` - width: 100%
- `h-full` - height: 100%
- `min-h-screen` - min-height: 100vh

**Docs**: https://v3.tailwindcss.com/docs/position

### Flexbox (Navigation, Cards)
```jsx
// Horizontal navigation
<nav className="flex items-center justify-between px-6 py-4">
  {/* Nav items */}
</nav>

// Centered content
<div className="flex items-center justify-center h-screen">
  {/* Centered content */}
</div>

// Card grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Cards */}
</div>
```

**Common Flex Classes:**
- `flex` - display: flex
- `items-center` - align-items: center
- `justify-between` - justify-content: space-between
- `justify-center` - justify-content: center
- `gap-4` - gap: 1rem (16px)

**Docs**: https://v3.tailwindcss.com/docs/flex

### Grid Layouts
```jsx
// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Grid items */}
</div>
```

**Docs**: https://v3.tailwindcss.com/docs/grid-template-columns

---

## Responsive Design

### Breakpoints (Mobile-First)
- `sm:` - 640px and up
- `md:` - 768px and up
- `lg:` - 1024px and up
- `xl:` - 1280px and up
- `2xl:` - 1536px and up

### Examples Used in JCN
```jsx
// Responsive text sizing
<h1 className="text-4xl md:text-6xl lg:text-8xl">
  JCN.AI
</h1>

// Responsive padding
<div className="px-4 md:px-8 lg:px-12">
  {/* Content */}
</div>

// Responsive grid columns
<div className="grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* Cards */}
</div>
```

**Docs**: https://v3.tailwindcss.com/docs/responsive-design

---

## Colors & Dark Mode

### Our Custom Color Variables
```css
/* Light mode (Happy Hues Palette #6) */
:root {
  --color-background: #fffffe;
  --color-surface: #d1d1e9;
  --color-border: #2b2c34;
  --color-primary: #2b2c34;
  --color-secondary: #6c6c7c;
  --color-accent: #6246ea;
  --color-success: #22c55e;
  --color-error: #e45858;
  --color-highlight: #e45858;
}

/* Dark mode */
.dark {
  --color-background: #0a0a0a;
  --color-surface: #141414;
  --color-border: #262626;
  --color-primary: #ffffff;
  --color-secondary: #a3a3a3;
  --color-accent: #3b82f6;
  --color-success: #22c55e;
  --color-error: #ef4444;
  --color-highlight: #3b82f6;
}
```

### Using Custom Colors
```jsx
// Background colors
<div className="bg-background">  {/* Uses CSS variable */}
<div className="bg-surface">
<div className="bg-[#00d4ff]">  {/* Arbitrary value */}

// Text colors
<p className="text-primary">
<p className="text-secondary">
<p className="text-accent">
```

### Dark Mode Classes
```jsx
// Dark mode variant
<div className="bg-white dark:bg-gray-900">
  <p className="text-gray-900 dark:text-white">
    Content
  </p>
</div>
```

**Docs**: https://v3.tailwindcss.com/docs/dark-mode

---

## Typography

### Font Families
```jsx
// Inter font (our default)
<h1 className="font-sans">  {/* Uses Inter */}

// Monospace
<code className="font-mono">
```

### Font Sizes
```jsx
<p className="text-xs">     {/* 12px */}
<p className="text-sm">     {/* 14px */}
<p className="text-base">   {/* 16px */}
<p className="text-lg">     {/* 18px */}
<p className="text-xl">     {/* 20px */}
<p className="text-2xl">    {/* 24px */}
<p className="text-4xl">    {/* 36px */}
<p className="text-6xl">    {/* 60px */}
<p className="text-8xl">    {/* 96px */}
```

### Font Weights
```jsx
<p className="font-normal">   {/* 400 */}
<p className="font-medium">   {/* 500 */}
<p className="font-semibold"> {/* 600 */}
<p className="font-bold">     {/* 700 */}
```

**Docs**: https://v3.tailwindcss.com/docs/font-family

---

## Spacing (Padding & Margin)

### Scale (1 unit = 0.25rem = 4px)
- `p-1` = 4px
- `p-2` = 8px
- `p-4` = 16px
- `p-6` = 24px
- `p-8` = 32px
- `p-12` = 48px
- `p-16` = 64px

### Examples
```jsx
// Padding
<div className="p-4">        {/* All sides */}
<div className="px-6 py-4">  {/* Horizontal & vertical */}
<div className="pt-8 pb-4">  {/* Top & bottom */}

// Margin
<div className="m-4">        {/* All sides */}
<div className="mx-auto">    {/* Horizontal centering */}
<div className="mt-8 mb-4">  {/* Top & bottom */}
```

**Docs**: https://v3.tailwindcss.com/docs/padding

---

## Borders & Shadows

### Borders
```jsx
<div className="border">              {/* 1px solid */}
<div className="border-2">            {/* 2px solid */}
<div className="border-border">       {/* Uses CSS variable */}
<div className="border-t border-b">   {/* Top & bottom only */}
<div className="rounded-lg">          {/* Border radius */}
<div className="rounded-full">        {/* Fully rounded */}
```

### Shadows
```jsx
<div className="shadow-sm">    {/* Small shadow */}
<div className="shadow">       {/* Default shadow */}
<div className="shadow-lg">    {/* Large shadow */}
<div className="shadow-xl">    {/* Extra large */}
```

**Docs**: https://v3.tailwindcss.com/docs/border-width

---

## Transitions & Animations

### Transitions
```jsx
// Smooth transitions
<button className="transition-all duration-300">
  Hover me
</button>

<div className="transition-colors duration-200 hover:bg-blue-500">
  Color transition
</div>
```

### Hover Effects (Used in JCN)
```jsx
// Landing page hover
<h1 className="hover:text-[#00d4ff] hover:drop-shadow-[0_0_30px_rgba(0,212,255,0.8)]">
  JCN.AI
</h1>

// Button hover
<button className="hover:bg-accent hover:scale-105 transition-all">
  Click me
</button>
```

**Docs**: https://v3.tailwindcss.com/docs/transition-property

---

## Background Images

### Using Background Images
```jsx
// Inline style (for dynamic images)
<div
  style={{
    backgroundImage: 'url(/landing-bg.jpg)',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
  }}
>
  {/* Content */}
</div>

// Tailwind classes
<div className="bg-cover bg-center bg-no-repeat" style={{ backgroundImage: 'url(/image.jpg)' }}>
  {/* Content */}
</div>
```

**Docs**: https://v3.tailwindcss.com/docs/background-size

---

## Common Patterns in JCN Dashboard

### 1. Full-Screen Landing Page
```jsx
<div
  className="fixed inset-0 w-full h-full overflow-hidden cursor-pointer"
  style={{
    backgroundImage: 'url(/landing-bg.jpg)',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
  }}
>
  <div className="absolute inset-0 flex items-center justify-center">
    <h1 className="text-6xl md:text-8xl lg:text-9xl font-bold">
      JCN.AI
    </h1>
  </div>
</div>
```

### 2. Navigation Bar
```jsx
<nav className="flex items-center justify-between px-6 py-4 bg-surface border-b border-border">
  <div className="text-xl font-bold text-primary">JCN.AI</div>
  <div className="flex gap-6">
    <a href="/dashboard" className="text-secondary hover:text-accent transition-colors">
      Dashboard
    </a>
  </div>
</nav>
```

### 3. Card Grid
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
  <div className="bg-surface rounded-lg p-6 border border-border shadow-lg hover:shadow-xl transition-shadow">
    <h3 className="text-xl font-semibold text-primary mb-2">Card Title</h3>
    <p className="text-secondary">Card content</p>
  </div>
</div>
```

### 4. Data Table
```jsx
<div className="overflow-x-auto">
  <table className="w-full border-collapse">
    <thead className="bg-surface">
      <tr>
        <th className="px-4 py-2 text-left text-primary border-b border-border">
          Header
        </th>
      </tr>
    </thead>
    <tbody>
      <tr className="hover:bg-surface transition-colors">
        <td className="px-4 py-2 border-b border-border">
          Data
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## Arbitrary Values

When you need values not in the default scale:

```jsx
// Arbitrary colors
<div className="bg-[#00d4ff]">

// Arbitrary spacing
<div className="p-[13px]">

// Arbitrary shadows
<div className="drop-shadow-[0_0_30px_rgba(0,212,255,0.8)]">

// Arbitrary widths
<div className="w-[450px]">
```

**Docs**: https://v3.tailwindcss.com/docs/adding-custom-styles#using-arbitrary-values

---

## Utility-First Best Practices

### ✅ DO:
- Use utility classes for most styling
- Combine utilities for complex designs
- Use responsive prefixes for mobile-first design
- Extract repeated patterns into components
- Use CSS variables for theme colors

### ❌ DON'T:
- Write custom CSS unless absolutely necessary
- Use inline styles when Tailwind utilities exist
- Hardcode colors (use CSS variables)
- Ignore responsive design
- Over-nest components

---

## Quick Reference Links

### Layout
- [Container](https://v3.tailwindcss.com/docs/container)
- [Display](https://v3.tailwindcss.com/docs/display)
- [Position](https://v3.tailwindcss.com/docs/position)
- [Flexbox](https://v3.tailwindcss.com/docs/flex)
- [Grid](https://v3.tailwindcss.com/docs/grid-template-columns)

### Typography
- [Font Family](https://v3.tailwindcss.com/docs/font-family)
- [Font Size](https://v3.tailwindcss.com/docs/font-size)
- [Font Weight](https://v3.tailwindcss.com/docs/font-weight)
- [Text Color](https://v3.tailwindcss.com/docs/text-color)

### Backgrounds
- [Background Color](https://v3.tailwindcss.com/docs/background-color)
- [Background Size](https://v3.tailwindcss.com/docs/background-size)
- [Background Position](https://v3.tailwindcss.com/docs/background-position)

### Effects
- [Box Shadow](https://v3.tailwindcss.com/docs/box-shadow)
- [Opacity](https://v3.tailwindcss.com/docs/opacity)
- [Transitions](https://v3.tailwindcss.com/docs/transition-property)

### Interactivity
- [Hover](https://v3.tailwindcss.com/docs/hover-focus-and-other-states#hover)
- [Focus](https://v3.tailwindcss.com/docs/hover-focus-and-other-states#focus)
- [Active](https://v3.tailwindcss.com/docs/hover-focus-and-other-states#active)
- [Dark Mode](https://v3.tailwindcss.com/docs/dark-mode)

---

## Troubleshooting

### Styles Not Applying?
1. Check if Tailwind is properly installed
2. Verify `@tailwind` directives in CSS
3. Check `tailwind.config.js` content paths
4. Clear build cache and restart dev server

### Dark Mode Not Working?
1. Ensure `.dark` class is on parent element
2. Check CSS variables are defined for both modes
3. Use `dark:` prefix on utilities

### Responsive Not Working?
1. Remember mobile-first (base styles apply to all sizes)
2. Use breakpoint prefixes: `md:`, `lg:`, etc.
3. Test in browser dev tools with responsive mode

---

## Project-Specific Notes

### Color System
We use CSS variables for theming, defined in `index.css`. Always use semantic color names (`bg-background`, `text-primary`) instead of hardcoded values for consistency across light/dark modes.

### Font
Inter font is loaded from Google Fonts in `index.html` and set as default via `font-sans` class.

### Build Process
Vite handles Tailwind compilation. PostCSS config is in `postcss.config.js`.

### Performance
Tailwind automatically purges unused styles in production builds, keeping CSS bundle size minimal.
