interface Metric {
  label: string;
  value: string | number;
  change?: number;
  format?: 'currency' | 'percentage' | 'number' | 'text';
}

interface MetricsTableProps {
  metrics: Metric[];
  title?: string;
}

export function MetricsTable({ metrics, title = 'Key Metrics' }: MetricsTableProps) {
  const formatValue = (metric: Metric) => {
    const { value, format } = metric;
    
    if (format === 'currency') {
      return `$${typeof value === 'number' ? value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : value}`;
    }
    
    if (format === 'percentage') {
      return `${typeof value === 'number' ? value.toFixed(2) : value}%`;
    }
    
    if (format === 'number') {
      return typeof value === 'number' ? value.toLocaleString() : value;
    }
    
    return value;
  };

  return (
    <div className="bg-white rounded-lg border">
      <div className="px-6 py-4 border-b">
        <h3 className="text-lg font-bold text-gray-900">{title}</h3>
      </div>
      <div className="divide-y">
        {metrics.map((metric, index) => (
          <div key={index} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
            <div className="text-sm font-medium text-gray-600">{metric.label}</div>
            <div className="flex items-center gap-3">
              <div className="text-sm font-semibold text-gray-900">
                {formatValue(metric)}
              </div>
              {metric.change !== undefined && (
                <div className={`text-xs font-medium px-2 py-1 rounded ${
                  metric.change >= 0 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-red-100 text-red-700'
                }`}>
                  {metric.change >= 0 ? '+' : ''}{metric.change.toFixed(2)}%
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
