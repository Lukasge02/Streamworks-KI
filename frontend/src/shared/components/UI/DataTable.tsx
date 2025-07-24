/**
 * Advanced DataTable Component
 * Enterprise-grade table with sorting, filtering, pagination, and virtual scrolling
 */

import React, { useMemo, useState, useRef, useEffect } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
  type VisibilityState,
  type RowSelectionState,
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import { 
  ChevronUp, 
  ChevronDown, 
  ChevronsUpDown,
  Search,
  Filter,
  Download,
  Eye,
  EyeOff,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  MoreHorizontal,
  Check,
  X,
} from 'lucide-react';
import { Button } from './Button';
import { Input } from './Input';
import { motion, AnimatePresence } from 'framer-motion';

export interface Column<T = any> {
  id: string;
  header: string;
  accessorKey?: keyof T;
  accessorFn?: (row: T) => any;
  cell?: (info: { getValue: () => any; row: { original: T } }) => React.ReactNode;
  sortable?: boolean;
  filterable?: boolean;
  width?: number | string;
  minWidth?: number;
  maxWidth?: number;
  align?: 'left' | 'center' | 'right';
  meta?: {
    filterVariant?: 'text' | 'select' | 'range' | 'date';
    filterOptions?: Array<{ label: string; value: any }>;
  };
}

interface DataTableProps<T = any> {
  data: T[];
  columns: Column<T>[];
  sortable?: boolean;
  filterable?: boolean;
  selectable?: boolean | 'single' | 'multiple';
  exportable?: boolean;
  pagination?: boolean;
  pageSize?: number;
  pageSizeOptions?: number[];
  virtualScrolling?: boolean;
  height?: string;
  loading?: boolean;
  emptyMessage?: string;
  className?: string;
  onRowSelect?: (selectedRows: T[]) => void;
  onRowClick?: (row: T) => void;
  onExport?: (data: T[], format: 'csv' | 'json' | 'excel') => void;
  expandableRows?: boolean;
  renderExpandedRow?: (row: T) => React.ReactNode;
}

export function DataTable<T = any>({
  data,
  columns,
  sortable = true,
  filterable = true,
  selectable = false,
  exportable = false,
  pagination = true,
  pageSize = 10,
  pageSizeOptions = [10, 25, 50, 100],
  virtualScrolling = false,
  height = '400px',
  loading = false,
  emptyMessage = 'Keine Daten verfügbar',
  className = '',
  onRowSelect,
  onRowClick,
  onExport,
  expandableRows = false,
  renderExpandedRow,
}: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
  const [globalFilter, setGlobalFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});
  
  const tableContainerRef = useRef<HTMLDivElement>(null);

  // Convert our Column interface to TanStack table ColumnDef
  const tableColumns = useMemo<ColumnDef<T>[]>(() => {
    const cols: ColumnDef<T>[] = [];

    // Selection column
    if (selectable) {
      cols.push({
        id: 'select',
        header: ({ table }) => (
          selectable === 'multiple' ? (
            <input
              type="checkbox"
              checked={table.getIsAllRowsSelected()}
              onChange={table.getToggleAllRowsSelectedHandler()}
              className="w-4 h-4 text-primary-600 rounded border-neutral-300 focus:ring-primary-500"
            />
          ) : null
        ),
        cell: ({ row }) => (
          <input
            type={selectable === 'single' ? 'radio' : 'checkbox'}
            name={selectable === 'single' ? 'row-selection' : undefined}
            checked={row.getIsSelected()}
            onChange={row.getToggleSelectedHandler()}
            className="w-4 h-4 text-primary-600 rounded border-neutral-300 focus:ring-primary-500"
          />
        ),
        size: 40,
        enableSorting: false,
        enableHiding: false,
      });
    }

    // Expand column
    if (expandableRows) {
      cols.push({
        id: 'expand',
        header: '',
        cell: ({ row }) => (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              const rowId = row.id;
              setExpandedRows(prev => ({
                ...prev,
                [rowId]: !prev[rowId],
              }));
            }}
            className="w-8 h-8 p-0"
          >
            <ChevronDown 
              size={16} 
              className={`transition-transform ${expandedRows[row.id] ? 'rotate-180' : ''}`}
            />
          </Button>
        ),
        size: 40,
        enableSorting: false,
        enableHiding: false,
      });
    }

    // Data columns
    columns.forEach((col) => {
      cols.push({
        id: col.id,
        accessorKey: col.accessorKey as string,
        accessorFn: col.accessorFn,
        header: col.header,
        cell: col.cell ? (info) => col.cell!(info) : undefined,
        enableSorting: sortable && (col.sortable !== false),
        enableColumnFilter: filterable && (col.filterable !== false),
        size: typeof col.width === 'number' ? col.width : undefined,
        minSize: col.minWidth,
        maxSize: col.maxWidth,
        meta: {
          align: col.align || 'left',
          ...col.meta,
        },
      });
    });

    return cols;
  }, [columns, selectable, sortable, filterable, expandableRows, expandedRows]);

  const table = useReactTable({
    data,
    columns: tableColumns,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
      globalFilter,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: pagination ? getPaginationRowModel() : undefined,
    enableRowSelection: !!selectable,
    enableMultiRowSelection: selectable === 'multiple',
    initialState: {
      pagination: {
        pageSize,
      },
    },
  });

  const { rows } = table.getRowModel();

  // Virtual scrolling setup
  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 50,
    enabled: virtualScrolling,
  });

  // Handle row selection changes
  useEffect(() => {
    if (onRowSelect) {
      const selectedRows = table.getSelectedRowModel().rows.map(row => row.original);
      onRowSelect(selectedRows);
    }
  }, [rowSelection, onRowSelect, table]);

  // Export functionality
  const handleExport = (format: 'csv' | 'json' | 'excel') => {
    if (onExport) {
      const selectedRows = table.getSelectedRowModel().rows;
      const dataToExport = selectedRows.length > 0 
        ? selectedRows.map(row => row.original)
        : data;
      onExport(dataToExport, format);
    } else {
      // Default export implementation
      const selectedRows = table.getSelectedRowModel().rows;
      const dataToExport = selectedRows.length > 0 
        ? selectedRows.map(row => row.original)
        : data;
      
      if (format === 'json') {
        const blob = new Blob([JSON.stringify(dataToExport, null, 2)], {
          type: 'application/json',
        });
        downloadBlob(blob, 'data.json');
      } else if (format === 'csv') {
        const csv = convertToCSV(dataToExport);
        const blob = new Blob([csv], { type: 'text/csv' });
        downloadBlob(blob, 'data.csv');
      }
    }
  };

  // Helper function to convert data to CSV
  const convertToCSV = (data: T[]): string => {
    if (data.length === 0) return '';
    
    const headers = columns.map(col => col.header);
    const csvRows = [headers.join(',')];
    
    data.forEach(row => {
      const values = columns.map(col => {
        const value = col.accessorKey ? (row as any)[col.accessorKey] : '';
        return `"${String(value).replace(/"/g, '""')}"`;
      });
      csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className={`bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg overflow-hidden ${className}`}>
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b border-neutral-200 dark:border-neutral-700">
        <div className="flex items-center space-x-4">
          {/* Global Search */}
          {filterable && (
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400" />
              <Input
                placeholder="Suchen..."
                value={globalFilter}
                onChange={(e) => setGlobalFilter(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
          )}
          
          {/* Filter Toggle */}
          {filterable && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              leftIcon={<Filter size={16} />}
            >
              Filter {showFilters && <span className="ml-1">({columnFilters.length})</span>}
            </Button>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {/* Column Visibility */}
          <div className="relative">
            <Button
              variant="outline"
              size="sm"
              leftIcon={<Eye size={16} />}
              onClick={() => {
                // Toggle visibility menu (implement dropdown)
              }}
            >
              Spalten
            </Button>
          </div>

          {/* Export */}
          {exportable && (
            <div className="relative">
              <Button
                variant="outline"
                size="sm"
                leftIcon={<Download size={16} />}
                onClick={() => handleExport('csv')}
              >
                Export
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Column Filters */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800"
          >
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {table.getHeaderGroups()[0]?.headers.map((header) => {
                const canFilter = header.column.getCanFilter();
                if (!canFilter || ['select', 'expand'].includes(header.id)) return null;

                return (
                  <div key={header.id}>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                    </label>
                    <Input
                      placeholder={`Filter ${header.column.columnDef.header}...`}
                      value={(header.column.getFilterValue() as string) ?? ''}
                      onChange={(e) => header.column.setFilterValue(e.target.value)}
                      className="w-full"
                    />
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Table */}
      <div 
        ref={tableContainerRef}
        className="overflow-auto"
        style={{ height: virtualScrolling ? height : 'auto' }}
      >
        <table className="w-full">
          <thead className="bg-neutral-50 dark:bg-neutral-800 sticky top-0 z-10">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className={`
                      px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider
                      ${header.column.getCanSort() ? 'cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-700' : ''}
                      ${(header.column.columnDef.meta as any)?.align === 'center' ? 'text-center' : ''}
                      ${(header.column.columnDef.meta as any)?.align === 'right' ? 'text-right' : ''}
                    `}
                    style={{ width: header.getSize() }}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center space-x-1">
                      <span>
                        {flexRender(header.column.columnDef.header, header.getContext())}
                      </span>
                      {header.column.getCanSort() && (
                        <span className="flex-shrink-0">
                          {header.column.getIsSorted() === 'asc' ? (
                            <ChevronUp size={14} />
                          ) : header.column.getIsSorted() === 'desc' ? (
                            <ChevronDown size={14} />
                          ) : (
                            <ChevronsUpDown size={14} className="opacity-40" />
                          )}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          
          <tbody className="bg-white dark:bg-neutral-900 divide-y divide-neutral-200 dark:divide-neutral-700">
            {loading ? (
              <tr>
                <td colSpan={tableColumns.length} className="px-4 py-8 text-center">
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                    <span className="text-neutral-500">Lädt...</span>
                  </div>
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={tableColumns.length} className="px-4 py-8 text-center text-neutral-500">
                  {emptyMessage}
                </td>
              </tr>
            ) : virtualScrolling ? (
              virtualizer.getVirtualItems().map((virtualRow) => {
                const row = rows[virtualRow.index];
                return (
                  <React.Fragment key={row.id}>
                    <tr
                      className="hover:bg-neutral-50 dark:hover:bg-neutral-800 cursor-pointer"
                      onClick={() => onRowClick?.(row.original)}
                      style={{
                        height: `${virtualRow.size}px`,
                        transform: `translateY(${virtualRow.start}px)`,
                      }}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <td
                          key={cell.id}
                          className={`
                            px-4 py-3 text-sm text-neutral-900 dark:text-neutral-100
                            ${(cell.column.columnDef.meta as any)?.align === 'center' ? 'text-center' : ''}
                            ${(cell.column.columnDef.meta as any)?.align === 'right' ? 'text-right' : ''}
                          `}
                        >
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                      ))}
                    </tr>
                    
                    {/* Expanded Row */}
                    {expandableRows && expandedRows[row.id] && renderExpandedRow && (
                      <tr>
                        <td colSpan={tableColumns.length} className="px-4 py-4 bg-neutral-50 dark:bg-neutral-800">
                          {renderExpandedRow(row.original)}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            ) : (
              rows.map((row) => (
                <React.Fragment key={row.id}>
                  <tr
                    className="hover:bg-neutral-50 dark:hover:bg-neutral-800 cursor-pointer"
                    onClick={() => onRowClick?.(row.original)}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className={`
                          px-4 py-3 text-sm text-neutral-900 dark:text-neutral-100
                          ${(cell.column.columnDef.meta as any)?.align === 'center' ? 'text-center' : ''}
                          ${(cell.column.columnDef.meta as any)?.align === 'right' ? 'text-right' : ''}
                        `}
                      >
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                  
                  {/* Expanded Row */}
                  {expandableRows && expandedRows[row.id] && renderExpandedRow && (
                    <tr>
                      <td colSpan={tableColumns.length} className="px-4 py-4 bg-neutral-50 dark:bg-neutral-800">
                        {renderExpandedRow(row.original)}
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && !virtualScrolling && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-neutral-200 dark:border-neutral-700">
          <div className="flex items-center space-x-2 text-sm text-neutral-700 dark:text-neutral-300">
            <span>
              Zeige {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} bis{' '}
              {Math.min(
                (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
                table.getFilteredRowModel().rows.length
              )}{' '}
              von {table.getFilteredRowModel().rows.length} Einträgen
            </span>
            {table.getSelectedRowModel().rows.length > 0 && (
              <span className="text-primary-600">
                ({table.getSelectedRowModel().rows.length} ausgewählt)
              </span>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <select
              value={table.getState().pagination.pageSize}
              onChange={(e) => table.setPageSize(Number(e.target.value))}
              className="border border-neutral-300 dark:border-neutral-600 rounded px-2 py-1 text-sm bg-white dark:bg-neutral-800"
            >
              {pageSizeOptions.map((size) => (
                <option key={size} value={size}>
                  {size} pro Seite
                </option>
              ))}
            </select>

            <div className="flex items-center space-x-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.setPageIndex(0)}
                disabled={!table.getCanPreviousPage()}
                className="w-8 h-8 p-0"
              >
                <ChevronsLeft size={14} />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
                className="w-8 h-8 p-0"
              >
                <ChevronLeft size={14} />
              </Button>
              
              <span className="px-2 text-sm">
                {table.getState().pagination.pageIndex + 1} von {table.getPageCount()}
              </span>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
                className="w-8 h-8 p-0"
              >
                <ChevronRight size={14} />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                disabled={!table.getCanNextPage()}
                className="w-8 h-8 p-0"
              >
                <ChevronsRight size={14} />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}