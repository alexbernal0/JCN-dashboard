import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface RadarMetric {
  name: string;
  max: number;
}

interface RadarData {
  name: string;
  value: number[];
}

interface PortfolioRadarChartProps {
  metrics: RadarMetric[];
  data: RadarData[];
  title?: string;
  height?: number;
}

export function PortfolioRadarChart({ 
  metrics,
  data, 
  title = 'Portfolio Quality Metrics',
  height = 400 
}: PortfolioRadarChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    // Initialize chart
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const option: echarts.EChartsOption = {
      title: {
        text: title,
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'bold',
        },
      },
      tooltip: {
        trigger: 'item',
      },
      legend: {
        data: data.map(d => d.name),
        bottom: 10,
      },
      radar: {
        indicator: metrics,
        shape: 'polygon',
        splitNumber: 5,
        axisName: {
          color: '#374151',
          fontSize: 12,
        },
        splitLine: {
          lineStyle: {
            color: '#e5e7eb',
          },
        },
        splitArea: {
          show: true,
          areaStyle: {
            color: ['rgba(59, 130, 246, 0.05)', 'rgba(59, 130, 246, 0.1)'],
          },
        },
      },
      series: [
        {
          name: 'Quality Metrics',
          type: 'radar',
          data: data.map((item, index) => ({
            name: item.name,
            value: item.value,
            lineStyle: {
              width: 2,
            },
            areaStyle: {
              opacity: 0.3,
            },
          })),
        },
      ],
      color: ['#3b82f6', '#8b5cf6', '#10b981'],
    };

    chartInstance.current.setOption(option);

    // Handle resize
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [data, metrics, title]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      chartInstance.current?.dispose();
    };
  }, []);

  return (
    <div className="bg-white rounded-lg border p-4">
      <div ref={chartRef} style={{ width: '100%', height: `${height}px` }} />
    </div>
  );
}
