import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface SectorData {
  sector: string;
  value: number;
  percentage: number;
}

interface SectorAllocationChartProps {
  data: SectorData[];
  title?: string;
  height?: number;
}

export function SectorAllocationChart({ 
  data, 
  title = 'Sector Allocation',
  height = 400 
}: SectorAllocationChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    // Initialize chart
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const chartData = data.map(item => ({
      name: item.sector,
      value: item.value,
    }));

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
        formatter: (params: any) => {
          return `<div style="font-weight: bold; margin-bottom: 4px;">${params.name}</div>
                  <div>Value: <strong>$${params.value.toLocaleString()}</strong></div>
                  <div>Percentage: <strong>${params.percent}%</strong></div>`;
        },
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'middle',
        textStyle: {
          fontSize: 12,
        },
      },
      series: [
        {
          name: 'Sector Allocation',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '55%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2,
          },
          label: {
            show: true,
            formatter: '{b}: {d}%',
            fontSize: 11,
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold',
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
          data: chartData,
        },
      ],
      color: [
        '#3b82f6', // blue
        '#8b5cf6', // purple
        '#10b981', // green
        '#f59e0b', // amber
        '#ef4444', // red
        '#06b6d4', // cyan
        '#ec4899', // pink
        '#6366f1', // indigo
        '#14b8a6', // teal
        '#f97316', // orange
      ],
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
  }, [data, title]);

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
