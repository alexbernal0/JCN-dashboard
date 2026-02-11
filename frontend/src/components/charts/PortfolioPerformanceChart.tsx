import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface PerformanceData {
  date: string;
  value: number;
  benchmark?: number;
}

interface PortfolioPerformanceChartProps {
  data: PerformanceData[];
  title?: string;
  height?: number;
}

export function PortfolioPerformanceChart({ 
  data, 
  title = 'Portfolio Performance',
  height = 400 
}: PortfolioPerformanceChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    // Initialize chart
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const dates = data.map(d => d.date);
    const values = data.map(d => d.value);
    const benchmarks = data.map(d => d.benchmark || 0);

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
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
        },
        formatter: (params: any) => {
          let result = `<div style="font-weight: bold; margin-bottom: 4px;">${params[0].axisValue}</div>`;
          params.forEach((param: any) => {
            const value = param.value.toFixed(2);
            const color = param.color;
            result += `<div style="display: flex; align-items: center; gap: 8px;">
              <span style="display: inline-block; width: 10px; height: 10px; background-color: ${color}; border-radius: 50%;"></span>
              <span>${param.seriesName}: <strong>$${value}</strong></span>
            </div>`;
          });
          return result;
        },
      },
      legend: {
        data: ['Portfolio', 'Benchmark'],
        top: 30,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: 80,
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLabel: {
          rotate: 45,
        },
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '${value}',
        },
      },
      series: [
        {
          name: 'Portfolio',
          type: 'line',
          data: values,
          smooth: true,
          lineStyle: {
            width: 3,
            color: '#3b82f6',
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
              { offset: 1, color: 'rgba(59, 130, 246, 0.05)' },
            ]),
          },
          itemStyle: {
            color: '#3b82f6',
          },
        },
        {
          name: 'Benchmark',
          type: 'line',
          data: benchmarks,
          smooth: true,
          lineStyle: {
            width: 2,
            color: '#94a3b8',
            type: 'dashed',
          },
          itemStyle: {
            color: '#94a3b8',
          },
        },
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
