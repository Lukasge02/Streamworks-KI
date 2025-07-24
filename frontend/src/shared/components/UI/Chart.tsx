/**
 * Chart Components - Recharts Integration
 * Enterprise-grade charts with interactive features and export capabilities
 */

import React, { useMemo, useState, useRef } from 'react';
import {
  ResponsiveContainer,
  LineChart as RechartsLineChart,
  AreaChart as RechartsAreaChart,
  BarChart as RechartsBarChart,
  PieChart as RechartsPieChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Line,
  Area,
  Bar,
  Pie,
  Cell,
  ReferenceLine,
  Brush,
  ComposedChart,
  Scatter,
} from 'recharts';
import { Download, Maximize2, Minimize2, RefreshCw, Palette } from 'lucide-react';
import { Button } from './Button';
import { useUiStore } from '../../../stores/uiStore';

export interface ChartData {
  [key: string]: any;
}

interface BaseChartProps {
  data: ChartData[];
  title?: string;
  subtitle?: string;
  width?: string | number;
  height?: string | number;
  colors?: string[];
  animated?: boolean;
  exportable?: boolean;
  showGrid?: boolean;
  showLegend?: boolean;
  showTooltip?: boolean;
  loading?: boolean;
  className?: string;
  onDataPointClick?: (data: any, index: number) => void;
}

interface LineChartProps extends BaseChartProps {
  xKey: string;
  yKeys: string[];
  strokeWidth?: number;
  curved?: boolean;
  showDots?: boolean;
  showArea?: boolean;
}

interface BarChartProps extends BaseChartProps {
  xKey: string;
  yKeys: string[];
  stackId?: string;
  barSize?: number;
  layout?: 'horizontal' | 'vertical';
}

interface PieChartProps extends BaseChartProps {
  dataKey: string;
  nameKey: string;
  valueKey: string;
  showLabels?: boolean;
  innerRadius?: number;
  outerRadius?: number;
}

interface AreaChartProps extends BaseChartProps {
  xKey: string;
  yKeys: string[];
  stackId?: string;
  curved?: boolean;
}

// Default color schemes
const colorSchemes = {
  default: ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'],
  streamworks: ['#FF6B35', '#F7931E', '#FFD23F', '#06FFA5', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
  monochrome: ['#1F2937', '#374151', '#4B5563', '#6B7280', '#9CA3AF', '#D1D5DB', '#E5E7EB', '#F3F4F6'],
  warm: ['#DC2626', '#EA580C', '#CA8A04', '#65A30D', '#059669', '#0891B2', '#7C3AED', '#C2410C'],
  cool: ['#1E40AF', '#0891B2', '#059669', '#65A30D', '#7C3AED', '#BE185D', '#BE123C', '#A21CAF'],
};

// Base Chart Container Component
function ChartContainer({
  title,
  subtitle,
  exportable = false,
  loading = false,
  className = '',
  children,
  chartRef,
}: {
  title?: string;
  subtitle?: string;
  exportable?: boolean;
  loading?: boolean;
  className?: string;
  children: React.ReactNode;
  chartRef?: React.RefObject<HTMLDivElement>;
}) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentColorScheme, setCurrentColorScheme] = useState<keyof typeof colorSchemes>('streamworks');

  const handleExport = async (format: 'png' | 'svg' | 'pdf') => {
    if (!chartRef?.current) return;

    try {
      if (format === 'png') {
        // Use dynamic import for html2canvas
        const { default: html2canvas } = await import('html2canvas');
        const canvas = await html2canvas(chartRef.current, {
          backgroundColor: '#ffffff',
          scale: 2,
        });
        
        const link = document.createElement('a');
        link.download = `chart-${Date.now()}.png`;
        link.href = canvas.toDataURL();
        link.click();
      } else if (format === 'pdf') {
        const [{ default: html2canvas }, { default: jsPDF }] = await Promise.all([
          import('html2canvas'),
          import('jspdf')
        ]);
        
        const canvas = await html2canvas(chartRef.current, {
          backgroundColor: '#ffffff',
          scale: 2,
        });
        
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF();
        const imgWidth = 210;
        const pageHeight = 295;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        let heightLeft = imgHeight;
        
        let position = 0;
        
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
        
        while (heightLeft >= 0) {
          position = heightLeft - imgHeight;
          pdf.addPage();
          pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
          heightLeft -= pageHeight;
        }
        
        pdf.save(`chart-${Date.now()}.pdf`);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <div className={`bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      {(title || subtitle || exportable) && (
        <div className="flex items-center justify-between p-4 border-b border-neutral-200 dark:border-neutral-700">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                {subtitle}
              </p>
            )}
          </div>
          
          {exportable && (
            <div className="flex items-center space-x-2">
              <select
                value={currentColorScheme}
                onChange={(e) => setCurrentColorScheme(e.target.value as keyof typeof colorSchemes)}
                className="text-sm border border-neutral-300 dark:border-neutral-600 rounded px-2 py-1 bg-white dark:bg-neutral-800"
              >
                <option value="streamworks">StreamWorks</option>
                <option value="default">Standard</option>
                <option value="monochrome">Monochrom</option>
                <option value="warm">Warm</option>
                <option value="cool">Cool</option>
              </select>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport('png')}
                title="Als PNG exportieren"
                className="h-8 w-8 p-0"
              >
                <Download size={14} />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsFullscreen(!isFullscreen)}
                title={isFullscreen ? 'Vollbild verlassen' : 'Vollbild'}
                className="h-8 w-8 p-0"
              >
                {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
              </Button>
            </div>
          )}
        </div>
      )}
      
      {/* Chart Content */}
      <div 
        ref={chartRef}
        className={`relative ${isFullscreen ? 'fixed inset-0 z-50 bg-white dark:bg-neutral-900' : ''}`}
      >
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="flex items-center space-x-2 text-neutral-500">
              <RefreshCw size={20} className="animate-spin" />
              <span>Chart wird geladen...</span>
            </div>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
}

// Custom Tooltip Component
function CustomTooltip({ active, payload, label, formatter }: any) {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-lg p-3">
      <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100 mb-2">
        {label}
      </p>
      {payload.map((entry: any, index: number) => (
        <div key={index} className="flex items-center space-x-2 text-sm">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-neutral-600 dark:text-neutral-400">
            {entry.name}:
          </span>
          <span className="font-medium text-neutral-900 dark:text-neutral-100">
            {formatter ? formatter(entry.value, entry.name) : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}

// Line Chart Component
export function LineChart({
  data,
  xKey,
  yKeys,
  title,
  subtitle,
  width = '100%',
  height = 300,
  colors = colorSchemes.streamworks,
  animated = true,
  exportable = false,
  showGrid = true,
  showLegend = true,
  showTooltip = true,
  showDots = true,
  showArea = false,
  curved = true,
  strokeWidth = 2,
  loading = false,
  className = '',
  onDataPointClick,
}: LineChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const { isDark } = useUiStore();

  const chartColors = useMemo(() => {
    return yKeys.map((_, index) => colors[index % colors.length]);
  }, [yKeys, colors]);

  return (
    <ChartContainer
      title={title}
      subtitle={subtitle}
      exportable={exportable}
      loading={loading}
      className={className}
      chartRef={chartRef}
    >
      <div className="p-4">
        <ResponsiveContainer width={width} height={height}>
          <RechartsLineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            {showGrid && (
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={isDark ? '#374151' : '#E5E7EB'}
                opacity={0.5}
              />
            )}
            <XAxis 
              dataKey={xKey}
              stroke={isDark ? '#9CA3AF' : '#6B7280'}
              fontSize={12}
            />
            <YAxis 
              stroke={isDark ? '#9CA3AF' : '#6B7280'}
              fontSize={12}
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            
            {yKeys.map((key, index) => (
              <Line
                key={key}
                type={curved ? 'monotone' : 'linear'}
                dataKey={key}
                stroke={chartColors[index]}
                strokeWidth={strokeWidth}
                dot={showDots ? { fill: chartColors[index], r: 4 } : false}
                activeDot={{ r: 6, stroke: chartColors[index], strokeWidth: 2 }}
                animationDuration={animated ? 1000 : 0}
                onClick={onDataPointClick}
              />
            ))}
            
            {showArea && yKeys.map((key, index) => (
              <Area
                key={`area-${key}`}
                type={curved ? 'monotone' : 'linear'}
                dataKey={key}
                stroke={chartColors[index]}
                fill={chartColors[index]}
                fillOpacity={0.1}
              />
            ))}
          </RechartsLineChart>
        </ResponsiveContainer>
      </div>
    </ChartContainer>
  );
}

// Bar Chart Component
export function BarChart({
  data,
  xKey,
  yKeys,
  title,
  subtitle,
  width = '100%',
  height = 300,
  colors = colorSchemes.streamworks,
  animated = true,
  exportable = false,
  showGrid = true,
  showLegend = true,
  showTooltip = true,
  stackId,
  barSize = 20,
  layout = 'vertical',
  loading = false,
  className = '',
  onDataPointClick,
}: BarChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const { isDark } = useUiStore();

  const chartColors = useMemo(() => {
    return yKeys.map((_, index) => colors[index % colors.length]);
  }, [yKeys, colors]);

  return (
    <ChartContainer
      title={title}
      subtitle={subtitle}
      exportable={exportable}
      loading={loading}
      className={className}
      chartRef={chartRef}
    >
      <div className="p-4">
        <ResponsiveContainer width={width} height={height}>
          <RechartsBarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            {showGrid && (
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={isDark ? '#374151' : '#E5E7EB'}
                opacity={0.5}
              />
            )}
            <XAxis 
              dataKey={xKey}
              stroke={isDark ? '#9CA3AF' : '#6B7280'}
              fontSize={12}
            />
            <YAxis 
              stroke={isDark ? '#9CA3AF' : '#6B7280'}
              fontSize={12}
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            
            {yKeys.map((key, index) => (
              <Bar
                key={key}
                dataKey={key}
                fill={chartColors[index]}
                stackId={stackId}
                maxBarSize={barSize}
                animationDuration={animated ? 1000 : 0}
                onClick={onDataPointClick}
                radius={[2, 2, 0, 0]}
              />
            ))}
          </RechartsBarChart>
        </ResponsiveContainer>
      </div>
    </ChartContainer>
  );
}

// Area Chart Component
export function AreaChart({
  data,
  xKey,
  yKeys,
  title,
  subtitle,
  width = '100%',
  height = 300,
  colors = colorSchemes.streamworks,
  animated = true,
  exportable = false,
  showGrid = true,
  showLegend = true,
  showTooltip = true,
  stackId,
  curved = true,
  loading = false,
  className = '',
  onDataPointClick,
}: AreaChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const { isDark } = useUiStore();

  const chartColors = useMemo(() => {
    return yKeys.map((_, index) => colors[index % colors.length]);
  }, [yKeys, colors]);

  return (
    <ChartContainer
      title={title}
      subtitle={subtitle}
      exportable={exportable}
      loading={loading}
      className={className}
      chartRef={chartRef}
    >
      <div className="p-4">
        <ResponsiveContainer width={width} height={height}>
          <RechartsAreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            {showGrid && (
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={isDark ? '#374151' : '#E5E7EB'}
                opacity={0.5}
              />
            )}
            <XAxis 
              dataKey={xKey}
              stroke={isDark ? '#9CA3AF' : '#6B7280'}
              fontSize={12}
            />
            <YAxis 
              stroke={isDark ? '#9CA3AF' : '#6B7280'}
              fontSize={12}
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            
            {yKeys.map((key, index) => (
              <Area
                key={key}
                type={curved ? 'monotone' : 'linear'}
                dataKey={key}
                stackId={stackId}
                stroke={chartColors[index]}
                fill={chartColors[index]}
                fillOpacity={0.6}
                animationDuration={animated ? 1000 : 0}
                onClick={onDataPointClick}
              />
            ))}
          </RechartsAreaChart>
        </ResponsiveContainer>
      </div>
    </ChartContainer>
  );
}

// Pie Chart Component
export function PieChart({
  data,
  dataKey,
  nameKey,
  valueKey,
  title,
  subtitle,
  width = '100%',
  height = 300,
  colors = colorSchemes.streamworks,
  animated = true,
  exportable = false,
  showLegend = true,
  showTooltip = true,
  showLabels = true,
  innerRadius = 0,
  outerRadius = 80,
  loading = false,
  className = '',
  onDataPointClick,
}: PieChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  const chartColors = useMemo(() => {
    return data.map((_, index) => colors[index % colors.length]);
  }, [data, colors]);

  const renderCustomLabel = ({
    cx, cy, midAngle, innerRadius, outerRadius, percent
  }: any) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <ChartContainer
      title={title}
      subtitle={subtitle}
      exportable={exportable}
      loading={loading}
      className={className}
      chartRef={chartRef}
    >
      <div className="p-4">
        <ResponsiveContainer width={width} height={height}>
          <RechartsPieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={showLabels ? renderCustomLabel : false}
              outerRadius={outerRadius}
              innerRadius={innerRadius}
              fill="#8884d8"
              dataKey={dataKey}
              animationDuration={animated ? 1000 : 0}
              onClick={onDataPointClick}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={chartColors[index]} />
              ))}
            </Pie>
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
          </RechartsPieChart>
        </ResponsiveContainer>
      </div>
    </ChartContainer>
  );
}

// Export utility functions
export { colorSchemes };

// Custom hook for chart utilities
export function useChart() {
  const formatters = {
    currency: (value: number) => `€${value.toLocaleString('de-DE', { minimumFractionDigits: 2 })}`,
    percentage: (value: number) => `${value.toFixed(1)}%`,
    number: (value: number) => value.toLocaleString('de-DE'),
    compact: (value: number) => {
      if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
      if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
      return value.toString();
    },
  };

  const generateMockData = (count: number, keys: string[]) => {
    return Array.from({ length: count }, (_, i) => {
      const item: any = { name: `Item ${i + 1}`, date: `2024-${String(i % 12 + 1).padStart(2, '0')}-01` };
      keys.forEach(key => {
        item[key] = Math.floor(Math.random() * 100) + 10;
      });
      return item;
    });
  };

  return { formatters, generateMockData };
}