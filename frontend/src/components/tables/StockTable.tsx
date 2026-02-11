import { useMemo, useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  ColumnDef,
  SortingState,
} from '@tanstack/react-table';
import { ArrowUpDown, ArrowUp, ArrowDown, Search } from 'lucide-react';

export interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  sector: string;
}

interface StockTableProps {
  data: Stock[];
}

export function StockTable({ data }: StockTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState('');

  const columns = useMemo<ColumnDef<Stock>[]>(
    () => [
      {
        accessorKey: 'symbol',
        header: ({ column }) => {
          return (
            <button
              className="flex items-center gap-2 font-semibold hover:text-blue-600"
              onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            >
              Symbol
              {column.getIsSorted() === 'asc' ? (
                <ArrowUp className="h-4 w-4" />
              ) : column.getIsSorted() === 'desc' ? (
                <ArrowDown className="h-4 w-4" />
              ) : (
                <ArrowUpDown className="h-4 w-4 opacity-50" />
              )}
            </button>
          );
        },
        cell: ({ row }) => (
          <div className="font-semibold text-blue-600">{row.getValue('symbol')}</div>
        ),
      },
      {
        accessorKey: 'name',
        header: 'Company Name',
        cell: ({ row }) => (
          <div className="max-w-xs truncate">{row.getValue('name')}</div>
        ),
      },
      {
        accessorKey: 'price',
        header: ({ column }) => {
          return (
            <button
              className="flex items-center gap-2 font-semibold hover:text-blue-600"
              onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            >
              Price
              {column.getIsSorted() === 'asc' ? (
                <ArrowUp className="h-4 w-4" />
              ) : column.getIsSorted() === 'desc' ? (
                <ArrowDown className="h-4 w-4" />
              ) : (
                <ArrowUpDown className="h-4 w-4 opacity-50" />
              )}
            </button>
          );
        },
        cell: ({ row }) => (
          <div className="font-medium">${row.getValue<number>('price').toFixed(2)}</div>
        ),
      },
      {
        accessorKey: 'change',
        header: ({ column }) => {
          return (
            <button
              className="flex items-center gap-2 font-semibold hover:text-blue-600"
              onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            >
              Change
              {column.getIsSorted() === 'asc' ? (
                <ArrowUp className="h-4 w-4" />
              ) : column.getIsSorted() === 'desc' ? (
                <ArrowDown className="h-4 w-4" />
              ) : (
                <ArrowUpDown className="h-4 w-4 opacity-50" />
              )}
            </button>
          );
        },
        cell: ({ row }) => {
          const change = row.getValue<number>('change');
          const changePercent = row.original.changePercent;
          const isPositive = change >= 0;
          
          return (
            <div className={`font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? '+' : ''}{change.toFixed(2)} ({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)
            </div>
          );
        },
      },
      {
        accessorKey: 'volume',
        header: 'Volume',
        cell: ({ row }) => {
          const volume = row.getValue<number>('volume');
          return (
            <div className="text-gray-600">
              {volume >= 1000000 
                ? `${(volume / 1000000).toFixed(2)}M` 
                : `${(volume / 1000).toFixed(2)}K`}
            </div>
          );
        },
      },
      {
        accessorKey: 'marketCap',
        header: ({ column }) => {
          return (
            <button
              className="flex items-center gap-2 font-semibold hover:text-blue-600"
              onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            >
              Market Cap
              {column.getIsSorted() === 'asc' ? (
                <ArrowUp className="h-4 w-4" />
              ) : column.getIsSorted() === 'desc' ? (
                <ArrowDown className="h-4 w-4" />
              ) : (
                <ArrowUpDown className="h-4 w-4 opacity-50" />
              )}
            </button>
          );
        },
        cell: ({ row }) => {
          const marketCap = row.getValue<number>('marketCap');
          return (
            <div className="text-gray-600">
              ${marketCap >= 1000000000 
                ? `${(marketCap / 1000000000).toFixed(2)}B` 
                : `${(marketCap / 1000000).toFixed(2)}M`}
            </div>
          );
        },
      },
      {
        accessorKey: 'sector',
        header: 'Sector',
        cell: ({ row }) => (
          <div className="text-sm text-gray-600">{row.getValue('sector')}</div>
        ),
      },
    ],
    []
  );

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  });

  return (
    <div className="bg-white rounded-lg border">
      {/* Search Bar */}
      <div className="p-4 border-b">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search stocks..."
            value={globalFilter ?? ''}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="hover:bg-gray-50 transition-colors">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-6 py-4 border-t flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{' '}
          {Math.min(
            (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
            table.getFilteredRowModel().rows.length
          )}{' '}
          of {table.getFilteredRowModel().rows.length} results
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
