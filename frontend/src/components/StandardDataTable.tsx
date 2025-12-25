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
    loading = false
}: StandardDataTableProps<T>) {
    const [searchQuery, setSearchQuery] = useState("")
    const [activeFilters, setActiveFilters] = useState<Record<string, string[]>>({})
    const [currentPage, setCurrentPage] = useState(1)
    const [pageSize] = useState(10)

    const [importOpen, setImportOpen] = useState(false)
    const [importFile, setImportFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const [syncing, setSyncing] = useState(false)
    const [cancelling, setCancelling] = useState(false)

    // Filter Logic
    const filteredData = data.filter(item => {
        // 1. Text Search
        if (searchKey && searchQuery) {
            const val = item[searchKey]
            if (typeof val === 'string' && !val.toLowerCase().includes(searchQuery.toLowerCase())) {
                return false
            }
        }

        // 2. Faceted Filters
        for (const [key, selectedValues] of Object.entries(activeFilters)) {
            if (selectedValues.length > 0) {
                const itemValue = item[key]
                // Assumes itemValue is string or convertible to string
                const strVal = String(itemValue || "")
                if (!selectedValues.includes(strVal)) {
                    return false
                }
            }
        }

        return true
    })

    // Pagination Logic
    const totalPages = Math.ceil(filteredData.length / pageSize)
    const paginatedData = filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize)

    // Handlers
    const handleFilterChange = (key: string, value: string) => {
        setActiveFilters(prev => {
            const current = prev[key] || []
            const updated = current.includes(value)
                ? current.filter(v => v !== value)
                : [...current, value]
            return { ...prev, [key]: updated }
        })
        setCurrentPage(1)
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
                    <CardTitle className="text-xl">{title}</CardTitle>
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
                </div>
            </CardHeader>
            <CardContent className="p-6">
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6">
                    <div className="flex bg-background items-center w-full max-w-sm border rounded-md px-3">
                        <Search className="h-4 w-4 text-muted-foreground mr-2" />
                        <input
                            placeholder="Search..."
                            value={searchQuery}
                            onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
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
                                        {activeFilters[filter.key]?.length > 0 && (
                                            <span className="ml-2 rounded-sm bg-primary px-1 font-normal text-primary-foreground text-[10px]">
                                                {activeFilters[filter.key].length}
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
                                            checked={activeFilters[filter.key]?.includes(option.value)}
                                            onCheckedChange={() => handleFilterChange(filter.key, option.value)}
                                        >
                                            {option.label}
                                        </DropdownMenuCheckboxItem>
                                    ))}
                                    {activeFilters[filter.key]?.length > 0 && (
                                        <>
                                            <DropdownMenuSeparator />
                                            <DropdownMenuItem
                                                onSelect={() => handleFilterChange(filter.key, "")} // Logic to clear needs improvement, actually simple set empty
                                                onClick={() => setActiveFilters(prev => ({ ...prev, [filter.key]: [] }))}
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
                            ) : paginatedData.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={columns.length + 1} className="h-32 text-center text-muted-foreground">
                                        No results found.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                paginatedData.map((item, rowIdx) => (
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
                        Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, filteredData.length)} of {filteredData.length} records
                    </div>
                    <div className="space-x-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                        >
                            <ChevronLeft className="h-4 w-4" /> Previous
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages || totalPages === 0}
                        >
                            Next <ChevronRight className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
