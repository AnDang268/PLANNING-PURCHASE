"use client"

import { useState } from "react"
import {
    Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
    DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuCheckboxItem, DropdownMenuLabel, DropdownMenuSeparator
} from "@/components/ui/dropdown-menu"
import {
    Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger
} from "@/components/ui/dialog"
import {
    Card, CardContent, CardDescription, CardHeader, CardTitle
} from "@/components/ui/card"
import {
    Loader2, MoreHorizontal, Search, Download, Upload, RefreshCw, Trash2, Plus, FileSpreadsheet, ChevronLeft, ChevronRight, XCircle, Filter
} from "lucide-react"

export interface ColumnDef<T> {
    header: string
    accessorKey?: keyof T
    cell?: (item: T) => React.ReactNode
    className?: string
}

export interface DataTableFilterOption {
    label: string
    value: string
}

export interface DataTableFilter {
    key: string
    title: string
    options: DataTableFilterOption[]
}

interface StandardDataTableProps<T> {
    data: T[]
    columns: ColumnDef<T>[]
    title: string
    description?: string
    searchKey?: keyof T // Simple search on one column
    filters?: DataTableFilter[]

    // Actions
    onSync?: () => Promise<void>
    onCancelSync?: () => Promise<void>
    onImport?: (file: File) => Promise<void>
    onAdd?: () => void
    onEdit?: (item: T) => void
    onDelete?: (item: T) => Promise<void>
    onExport?: () => Promise<void>

    // Server-Side Props
    mode?: "client" | "server"
    totalCount?: number
    page?: number
    pageSize?: number
    onPaginationChange?: (page: number, pageSize: number) => void
    onSearchChange?: (query: string) => void
    onFilterChange?: (key: string, values: string[]) => void

    // State
    loading?: boolean
}

export function StandardDataTable<T extends Record<string, any>>({
    data,
    columns,
    title,
    description,
    searchKey,
    filters = [],
    onSync,
    onCancelSync,
    onImport,
    onAdd,
    onEdit,
    onDelete,
    loading = false,
    mode = "client",
    totalCount = 0,
    page = 1,
    pageSize = 10,
    onPaginationChange,
    onSearchChange,
    onFilterChange,
    onExport
}: StandardDataTableProps<T>) {
    // Client-Side State
    const [clientSearchQuery, setClientSearchQuery] = useState("")
    const [clientActiveFilters, setClientActiveFilters] = useState<Record<string, string[]>>({})
    const [clientPage, setClientPage] = useState(1)
    const [clientPageSize] = useState(10) // Fixed for now

    const [importOpen, setImportOpen] = useState(false)
    const [importFile, setImportFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const [syncing, setSyncing] = useState(false)
    const [cancelling, setCancelling] = useState(false)

    // Derived Values based on Mode
    const isServer = mode === "server"
    const currentPage = isServer ? page : clientPage
    const currentTotal = isServer ? totalCount : data.length // For client, we calculate filtered length later

    // --- Client-Side Filtering Logic ---
    const filteredData = isServer ? data : data.filter(item => {
        // 1. Text Search
        if (clientSearchQuery) {
            const query = clientSearchQuery.toLowerCase()
            const matches = Object.values(item).some(val =>
                String(val).toLowerCase().includes(query)
            )
            if (!matches) return false
        }
        // 2. Faceted Filters
        for (const [key, selectedValues] of Object.entries(clientActiveFilters)) {
            if (selectedValues.length > 0) {
                const itemValue = item[key]
                const strVal = String(itemValue || "")
                if (!selectedValues.includes(strVal)) {
                    return false
                }
            }
        }
        return true
    })

    // Pagination Logic
    const finalTotalCount = isServer ? totalCount : filteredData.length
    const totalPages = Math.ceil(finalTotalCount / (isServer ? pageSize : clientPageSize))
    const displayData = isServer
        ? data
        : filteredData.slice((clientPage - 1) * clientPageSize, clientPage * clientPageSize)

    // Handlers
    const handleSearch = (val: string) => {
        if (isServer) {
            onSearchChange?.(val)
        } else {
            setClientSearchQuery(val)
            setClientPage(1)
        }
    }

    const handleFilter = (key: string, value: string) => {
        if (isServer) {
            // For Server Mode, we assume the parent manages the full state of filters
            // BUT, to keep this component dumb/smart hybrid, we need to know the current state.
            // Simplified: We notify the parent of the NEW list for this key.
            // WARNING: This component doesn't hold server filter state prop, so we might need to rely on parent to pass 'activeFilters' prop if we want fully controlled.
            // For now, let's implement a simple toggle logic assuming parent acts on it.
            // ACTUALLY: To support Faceted Filter UI properly in server mode, we need 'activeFilters' prop.
            // Let's defer complex server filtering and stick to Client-Side filtering for now? 
            // NO, the requirement IS Server-Side filtering.
            // Lets assume 'onFilterChange' takes (key, newValues).
            // But we don't know 'currentValues' if strict server mode.
            // FIX: We need 'activeFilters' prop if server mode.
            // For MVP: Let's use local state to track "desired" filters and send them up.
            setClientActiveFilters(prev => {
                const current = prev[key] || []
                const updated = current.includes(value)
                    ? current.filter(v => v !== value)
                    : [...current, value]

                if (isServer) onFilterChange?.(key, updated)
                return { ...prev, [key]: updated }
            })
            if (!isServer) setClientPage(1)
        } else {
            setClientActiveFilters(prev => {
                const current = prev[key] || []
                const updated = current.includes(value)
                    ? current.filter(v => v !== value)
                    : [...current, value]
                return { ...prev, [key]: updated }
            })
            setClientPage(1)
        }
    }

    const handlePageChange = (newPage: number) => {
        if (isServer) {
            onPaginationChange?.(newPage, pageSize)
        } else {
            setClientPage(newPage)
        }
    }

    const handleSync = async () => {
        if (!onSync) return
        setSyncing(true)
        try { await onSync() } finally { setSyncing(false) }
    }

    const handleCancelSync = async () => {
        if (!onCancelSync) return
        setCancelling(true)
        try { await onCancelSync() } finally { setCancelling(false) }
    }

    const handleImport = async () => {
        if (!onImport || !importFile) return
        setUploading(true)
        try {
            await onImport(importFile)
            setImportOpen(false)
            setImportFile(null)
        } finally { setUploading(false) }
    }

    return (
        <Card className="shadow-sm">
            <CardHeader className="border-b space-y-4 md:space-y-0 md:flex-row md:items-center md:justify-between p-6">
                <div>
                    <div className="flex items-center gap-3">
                        <CardTitle className="text-xl">{title}</CardTitle>
                        <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                            {finalTotalCount} records
                        </span>
                    </div>
                    {description && <CardDescription className="mt-1">{description}</CardDescription>}
                </div>
                <div className="flex flex-wrap items-center gap-2">
                    {onSync && (
                        <div className="flex gap-1 border-r border-border pr-2 mr-1">
                            <Button variant="outline" size="sm" onClick={handleSync} disabled={syncing}>
                                {syncing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                                Sync
                            </Button>
                            {onCancelSync && (
                                <Button variant="ghost" size="icon" onClick={handleCancelSync} disabled={cancelling} className="text-destructive hover:bg-destructive/10">
                                    <XCircle className="h-4 w-4" />
                                </Button>
                            )}
                        </div>
                    )}
                    {onImport && (
                        <Dialog open={importOpen} onOpenChange={setImportOpen}>
                            <DialogTrigger asChild>
                                <Button variant="outline" size="sm">
                                    <Upload className="mr-2 h-4 w-4" /> Import
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Import Data</DialogTitle>
                                    <DialogDescription>Supported formats: .xlsx, .csv</DialogDescription>
                                </DialogHeader>
                                <div className="grid gap-4 py-4">
                                    <Input
                                        type="file"
                                        accept=".csv,.xlsx,.xls"
                                        onChange={e => setImportFile(e.target.files?.[0] || null)}
                                    />
                                </div>
                                <DialogFooter>
                                    <Button onClick={handleImport} disabled={!importFile || uploading}>
                                        {uploading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                        Upload
                                    </Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    )}
                    {onAdd && (
                        <Button size="sm" onClick={onAdd}>
                            <Plus className="mr-2 h-4 w-4" /> Add New
                        </Button>
                    )}
                    {onExport && (
                        <Button variant="outline" size="sm" onClick={onExport}>
                            <Download className="mr-2 h-4 w-4" /> Export
                        </Button>
                    )}
                </div>
            </CardHeader>
            <CardContent className="p-6">
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6">
                    <div className="flex bg-background items-center w-full max-w-sm border rounded-md px-3">
                        <Search className="h-4 w-4 text-muted-foreground mr-2" />
                        <input
                            placeholder="Search..."
                            defaultValue={mode === 'client' ? clientSearchQuery : undefined}
                            onChange={(e) => handleSearch(e.target.value)}
                            className="flex h-9 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
                        />
                    </div>
                    {/* Filters */}
                    <div className="flex gap-2 flex-wrap">
                        {filters.map((filter) => (
                            <DropdownMenu key={filter.key}>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="outline" size="sm" className="border-dashed">
                                        <Filter className="mr-2 h-4 w-4" />
                                        {filter.title}
                                        {clientActiveFilters[filter.key]?.length > 0 && (
                                            <span className="ml-2 rounded-sm bg-primary px-1 font-normal text-primary-foreground text-[10px]">
                                                {clientActiveFilters[filter.key].length}
                                            </span>
                                        )}
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-[200px]">
                                    <DropdownMenuLabel>{filter.title}</DropdownMenuLabel>
                                    <DropdownMenuSeparator />
                                    {filter.options.map((option) => (
                                        <DropdownMenuCheckboxItem
                                            key={option.value}
                                            checked={clientActiveFilters[filter.key]?.includes(option.value)}
                                            onCheckedChange={() => handleFilter(filter.key, option.value)}
                                        >
                                            {option.label}
                                        </DropdownMenuCheckboxItem>
                                    ))}
                                    {clientActiveFilters[filter.key]?.length > 0 && (
                                        <>
                                            <DropdownMenuSeparator />
                                            <DropdownMenuItem
                                                onSelect={() => {
                                                    setClientActiveFilters(prev => ({ ...prev, [filter.key]: [] }))
                                                    if (isServer) onFilterChange?.(filter.key, [])
                                                }}
                                                className="justify-center text-center"
                                            >
                                                Clear filters
                                            </DropdownMenuItem>
                                        </>
                                    )}
                                </DropdownMenuContent>
                            </DropdownMenu>
                        ))}
                    </div>
                </div>

                <div className="rounded-md border">
                    <Table>
                        <TableHeader className="bg-muted/50">
                            <TableRow>
                                {columns.map((col, idx) => (
                                    <TableHead key={idx} className={col.className}>{col.header}</TableHead>
                                ))}
                                {(onEdit || onDelete) && <TableHead className="w-[50px]"></TableHead>}
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                Array.from({ length: 5 }).map((_, i) => (
                                    <TableRow key={i}>
                                        {columns.map((_, idx) => (
                                            <TableCell key={idx}><div className="h-4 bg-muted rounded animate-pulse w-full"></div></TableCell>
                                        ))}
                                        {(onEdit || onDelete) && <TableCell><div className="h-4 bg-muted rounded animate-pulse w-8"></div></TableCell>}
                                    </TableRow>
                                ))
                            ) : displayData.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={columns.length + 1} className="h-32 text-center text-muted-foreground">
                                        No results found.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                displayData.map((item, rowIdx) => (
                                    <TableRow key={rowIdx} className="hover:bg-muted/50">
                                        {columns.map((col, colIdx) => (
                                            <TableCell key={colIdx} className={col.className}>
                                                {col.cell ? col.cell(item) : (item[col.accessorKey as keyof T] as React.ReactNode)}
                                            </TableCell>
                                        ))}
                                        {(onEdit || onDelete) && (
                                            <TableCell>
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button variant="ghost" className="h-8 w-8 p-0">
                                                            <MoreHorizontal className="h-4 w-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        {onEdit && <DropdownMenuItem onClick={() => onEdit(item)}>Edit</DropdownMenuItem>}
                                                        {onDelete && (
                                                            <DropdownMenuItem onClick={() => onDelete(item)} className="text-red-600">
                                                                Delete
                                                            </DropdownMenuItem>
                                                        )}
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            </TableCell>
                                        )}
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </div>

                <div className="flex items-center justify-between py-4">
                    <div className="text-sm text-muted-foreground">
                        Showing {currentPage === 1 ? 1 : (currentPage - 1) * (isServer ? pageSize : clientPageSize) + 1} to {Math.min(currentPage * (isServer ? pageSize : clientPageSize), finalTotalCount)} of {finalTotalCount} records
                    </div>
                    <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1 text-sm mr-2">
                            <span>Page</span>
                            <Input
                                className="h-8 w-12 text-center p-0"
                                value={currentPage}
                                onChange={(e) => {
                                    const val = parseInt(e.target.value)
                                    if (!isNaN(val) && val >= 1 && val <= totalPages) {
                                        handlePageChange(val)
                                    }
                                }}
                            />
                            <span>of {totalPages}</span>
                        </div>
                        <Button
                            variant="outline"
                            size="sm"
                            className="h-8 px-2"
                            onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
                            disabled={currentPage === 1}
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            className="h-8 px-2"
                            onClick={() => handlePageChange(Math.min(totalPages, currentPage + 1))}
                            disabled={currentPage === totalPages || totalPages === 0}
                        >
                            <ChevronRight className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}

function FilterDropdown({
    filter,
    activeFilters,
    onFilterChange,
    onClear
}: {
    filter: DataTableFilter
    activeFilters: string[]
    onFilterChange: (value: string) => void
    onClear: () => void
}) {
    const [search, setSearch] = useState("")
    const filteredOptions = filter.options.filter(opt =>
        opt.label.toLowerCase().includes(search.toLowerCase())
    )

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="border-dashed">
                    <Filter className="mr-2 h-4 w-4" />
                    {filter.title}
                    {activeFilters.length > 0 && (
                        <span className="ml-2 rounded-sm bg-primary px-1 font-normal text-primary-foreground text-[10px]">
                            {activeFilters.length}
                        </span>
                    )}
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-[240px]">
                <DropdownMenuLabel>{filter.title}</DropdownMenuLabel>
                <div className="px-2 py-1.5 border-b border-border-subtle mb-1">
                    <div className="relative">
                        <Search className="absolute left-2 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                        <input
                            placeholder="Filter values..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="flex h-8 w-full rounded-md border border-input bg-transparent pl-8 pr-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                        />
                    </div>
                </div>

                <div className="max-h-[300px] overflow-y-auto pt-1">
                    {filteredOptions.length === 0 ? (
                        <div className="p-4 text-xs text-muted-foreground text-center">No matches found</div>
                    ) : (
                        filteredOptions.map((option) => (
                            <DropdownMenuCheckboxItem
                                key={option.value}
                                checked={activeFilters.includes(option.value)}
                                onCheckedChange={() => onFilterChange(option.value)}
                            >
                                {option.label}
                            </DropdownMenuCheckboxItem>
                        ))
                    )}
                </div>
                {activeFilters.length > 0 && (
                    <>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                            onSelect={onClear}
                            className="justify-center text-center text-destructive focus:text-destructive group cursor-pointer"
                        >
                            <span className="group-hover:underline">Clear filters</span>
                        </DropdownMenuItem>
                    </>
                )}
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
