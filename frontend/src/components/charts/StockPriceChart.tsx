import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface CandlestickData {
  date: string;
  open: number;
  close: number;
  low: number;
  high: number;
  volume: number;
}

interface StockPriceChartProps {
  data: CandlestickData[];
  symbol: string;
  height?: number;
}

export function StockPriceChart({ 
  data, 
  symbol,
  height = 500 
}: StockPriceChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    // Initialize chart
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const dates = data.map(d => d.date);
    const ohlc = data.map(d => [d.open, d.close, d.low, d.high]);
    const volumes = data.map(d => d.volume);

    const option: echarts.EChartsOption = {
      title: {
        text: `${symbol} Stock Price`,
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
          const candleData = params[0];
          const volumeData = params[1];
          
          return `<div style="font-weight: bold; margin-bottom: 8px;">${candleData.axisValue}</div>
                  <div style="margin-bottom: 4px;">
                    <div>Open: <strong>$${candleData.data[1]}</strong></div>
                    <div>Close: <strong>$${candleData.data[2]}</strong></div>
                    <div>Low: <strong>$${candleData.data[3]}</strong></div>
                    <div>High: <strong>$${candleData.data[4]}</strong></div>
                  </div>
                  <div>Volume: <strong>${volumeData.data.toLocaleString()}</strong></div>`;
        },
      },
      grid: [
        {
          left: '3%',
          right: '4%',
          top: 60,
          height: '60%',
          containLabel: true,
        },
        {
          left: '3%',
          right: '4%',
          top: '75%',
          height: '15%',
          containLabel: true,
        },
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          gridIndex: 0,
          axisLabel: {
            show: false,
          },
        },
        {
          type: 'category',
          data: dates,
          gridIndex: 1,
          axisLabel: {
            rotate: 45,
          },
        },
      ],
      yAxis: [
        {
          scale: true,
          gridIndex: 0,
          axisLabel: {
            formatter: '${value}',
          },
        },
        {
          scale: true,
          gridIndex: 1,
          axisLabel: {
            formatter: (value: number) => {
              if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M';
              if (value >= 1000) return (value / 1000).toFixed(1) + 'K';
              return value.toString();
            },
          },
        },
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 0,
          end: 100,
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          bottom: 10,
          start: 0,
          end: 100,
        },
      ],
      series: [
        {
          name: 'Price',
          type: 'candlestick',
          data: ohlc,
          xAxisIndex: 0,
          yAxisIndex: 0,
          itemStyle: {
            color: '#10b981', // green for up
            color0: '#ef4444', // red for down
            borderColor: '#10b981',
            borderColor0: '#ef4444',
          },
        },
        {
          name: 'Volume',
          type: 'bar',
          data: volumes,
          xAxisIndex: 1,
          yAxisIndex: 1,
          itemStyle: {
            color: 'rgba(59, 130, 246, 0.5)',
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
  }, [data, symbol]);

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
