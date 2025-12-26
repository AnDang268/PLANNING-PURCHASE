"use client"

import { useState, useEffect } from "react"
import { API_BASE_URL } from "@/config"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableFooter } from "@/components/ui/table"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Loader2, Search, ArrowLeft, ArrowRight, Check, ChevronsUpDown, Filter, Download, Upload, FileDown, RefreshCw } from "lucide-react"
import { cn } from "@/lib/utils"
import { useToast } from "@/components/ui/use-toast"

interface InventoryItem {
    snapshot_date: string
    warehouse_id: string
    warehouse_name: string
    sku_id: string
    product_name: string
    group_name: string
    quantity_on_hand: number
    quantity_on_order: number
    quantity_allocated: number
    unit: string
    notes: string
}

interface Warehouse {
    warehouse_id: string
    warehouse_name: string
}

interface ProductGroup {
    group_id: string
    group_name: string
}

import { format } from "date-fns"
import { PeriodFilter, DateRange } from "@/components/PeriodFilter"

export default function InventoryPage() {
    const [data, setData] = useState<InventoryItem[]>([])
    const [loading, setLoading] = useState(true)
    const [page, setPage] = useState(1)
    const [total, setTotal] = useState(0)
    const [aggregates, setAggregates] = useState({ total_on_hand: 0, total_on_order: 0, total_allocated: 0 })
    const { toast } = useToast()

    // Filters
    // Default to this year
    const currentYear = new Date().getFullYear()
    const [dateRange, setDateRange] = useState<DateRange>({
        from: new Date(currentYear, 0, 1),
        to: new Date(currentYear, 11, 31)
    })

    const [search, setSearch] = useState("")
    const [warehouseFilter, setWarehouseFilter] = useState("ALL")
    const [groupFilter, setGroupFilter] = useState("ALL")

    // Filter Options
    const [warehouses, setWarehouses] = useState<Warehouse[]>([])
    const [groups, setGroups] = useState<ProductGroup[]>([])
    const [openGroup, setOpenGroup] = useState(false)

    // Load Filters
    useEffect(() => {
        const fetchFilters = async () => {
            try {
                const [resWh, resGr] = await Promise.all([
                    fetch(`${API_BASE_URL}/api/data/warehouses`),
                    fetch(`${API_BASE_URL}/api/data/groups`)
                ])
                if (resWh.ok) setWarehouses(await resWh.json())
                if (resGr.ok) setGroups(await resGr.json())
            } catch (e) {
                console.error("Failed to load filters", e)
            }
        }
        fetchFilters()
    }, [])

    const fetchData = async () => {
        setLoading(true)
        try {
            const limit = 20
            const skip = (page - 1) * limit

            const params = new URLSearchParams()
            params.append('skip', skip.toString())
            params.append('limit', limit.toString())

            if (dateRange.from) params.append('start_date', format(dateRange.from, 'yyyy-MM-dd'))
            if (dateRange.to) params.append('end_date', format(dateRange.to, 'yyyy-MM-dd'))

            if (search) params.append('search', search)
            if (warehouseFilter && warehouseFilter !== 'ALL') params.append('warehouse_id', warehouseFilter)
            if (groupFilter && groupFilter !== 'ALL') params.append('group_id', groupFilter)

            const url = `${API_BASE_URL}/api/data/inventory?${params.toString()}`

            const res = await fetch(url)
            if (res.ok) {
                const json = await res.json()
                setData(json.data)
                setTotal(json.total)
                if (json.aggregates) setAggregates(json.aggregates)
            } else {
                console.error("Fetch returned", res.status)
            }
        } catch (e) {
            console.error("Fetch Error", e)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [page, dateRange, warehouseFilter, groupFilter])

    const handleSearch = () => {
        setPage(1)
        fetchData()
    }

    const handleDownloadTemplate = () => {
        window.open(`${API_BASE_URL}/api/data/template/inventory_manual`, '_blank')
    }

    const handleExport = () => {
        // Build export URL with current filters
        // TODO: Implement proper export
    }

    const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        const formData = new FormData()
        formData.append("file", file)

        try {
            const res = await fetch(`${API_BASE_URL}/api/data/inventory/import`, {
                method: "POST",
                body: formData,
            })
            const json = await res.json()
            if (res.ok) {
                toast({ title: "Success", description: json.message, variant: "default" })
                fetchData()
            } else {
                toast({ title: "Import Failed", description: json.detail || "Unknown error", variant: "destructive" })
                if (json.errors) {
                    console.error("Import Errors:", json.errors)
                }
            }
        } catch (err) {
            console.error(err)
            toast({ title: "Error", description: "Import Error", variant: "destructive" })
        } finally {
            // Reset input
            e.target.value = ""
        }
    }

    const handleSync = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/crm/sync-inventory`, { method: 'POST' })
            if (res.ok) {
                toast({ title: "Sync Started", description: "Inventory sync running in background..." })
                setTimeout(fetchData, 2000)
            } else {
                toast({ title: "Sync Failed", variant: "destructive" })
            }
        } catch (e) {
            console.error(e)
            toast({ title: "Sync Error", variant: "destructive" })
        } finally {
            setLoading(false)
        }
    }

    const totalPages = Math.ceil(total / 20)

    return (
        <div className="container py-8 space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-text-heading">Inventory Snapshots</h1>
                <p className="text-muted-foreground">View daily inventory levels synced from MISA CRM.</p>
            </div>

            <Card>
                <CardHeader className="pb-4">
                    <CardTitle>Snapshot Data</CardTitle>
                    <div className="flex flex-col gap-4 mt-4">
                        {/* Actions Row */}
                        <div className="flex gap-2 justify-end">
                            <Button variant="outline" size="sm" onClick={handleSync}>
                                <RefreshCw className="mr-2 h-4 w-4" /> Sync from Misa
                            </Button>
                            <Button variant="outline" size="sm" onClick={handleDownloadTemplate}>
                                <FileDown className="mr-2 h-4 w-4" /> Template
                            </Button>
                            <div className="relative">
                                <Button variant="default" size="sm" className="relative">
                                    <Upload className="mr-2 h-4 w-4" /> Import Excel
                                    <input
                                        type="file"
                                        accept=".csv,.xlsx"
                                        className="absolute inset-0 opacity-0 cursor-pointer"
                                        onChange={handleImport}
                                    />
                                </Button>
                            </div>
                        </div>

                        <div className="flex flex-col md:flex-row gap-4 justify-between">
                            <div className="flex flex-wrap gap-2 items-center flex-1">
                                {/* Period Filter */}
                                <PeriodFilter onFilterChange={(r) => { setDateRange(r); setPage(1); }} />

                                {/* Warehouse Filter */}
                                <Select value={warehouseFilter} onValueChange={(v) => { setWarehouseFilter(v); setPage(1); }}>
                                    <SelectTrigger className="w-[180px]">
                                        <SelectValue placeholder="All Warehouses" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="ALL">All Warehouses</SelectItem>
                                        {warehouses.map(wh => (
                                            <SelectItem key={wh.warehouse_id} value={wh.warehouse_id}>
                                                {wh.warehouse_name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>

                                {/* Group Filter (Searchable) */}
                                <Popover open={openGroup} onOpenChange={setOpenGroup}>
                                    <PopoverTrigger asChild>
                                        <Button
                                            variant="outline"
                                            role="combobox"
                                            aria-expanded={openGroup}
                                            className="w-[200px] justify-between"
                                        >
                                            {groupFilter && groupFilter !== 'ALL'
                                                ? groups.find((g) => g.group_id === groupFilter)?.group_name
                                                : "All Product Groups"}
                                            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                        </Button>
                                    </PopoverTrigger>
                                    <PopoverContent className="w-[200px] p-0">
                                        <Command>
                                            <CommandInput placeholder="Search group..." />
                                            <CommandList>
                                                <CommandEmpty>No group found.</CommandEmpty>
                                                <CommandGroup>
                                                    <CommandItem
                                                        value="ALL"
                                                        onSelect={() => {
                                                            setGroupFilter("ALL")
                                                            setOpenGroup(false)
                                                            setPage(1)
                                                        }}
                                                    >
                                                        <Check className={cn("mr-2 h-4 w-4", groupFilter === "ALL" ? "opacity-100" : "opacity-0")} />
                                                        All Product Groups
                                                    </CommandItem>
                                                    {groups.map((group) => (
                                                        <CommandItem
                                                            key={group.group_id}
                                                            value={group.group_name} // Search by name
                                                            onSelect={() => {
                                                                setGroupFilter(group.group_id)
                                                                setOpenGroup(false)
                                                                setPage(1)
                                                            }}
                                                        >
                                                            <Check
                                                                className={cn(
                                                                    "mr-2 h-4 w-4",
                                                                    groupFilter === group.group_id ? "opacity-100" : "opacity-0"
                                                                )}
                                                            />
                                                            {group.group_name}
                                                        </CommandItem>
                                                    ))}
                                                </CommandGroup>
                                            </CommandList>
                                        </Command>
                                    </PopoverContent>
                                </Popover>
                            </div>

                            {/* Search SKU */}
                            <div className="flex items-center space-x-2">
                                <Input
                                    placeholder="Search SKU / Name..."
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                    className="h-10 w-[250px]"
                                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                />
                                <Button onClick={handleSearch}>
                                    <Search className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Date</TableHead>
                                <TableHead>Product</TableHead>
                                <TableHead>Group</TableHead>
                                <TableHead>Warehouse</TableHead>
                                <TableHead className="text-right">Qty On Hand</TableHead>
                                <TableHead className="text-right">Qty On Order</TableHead>
                                <TableHead className="text-right">Allocated</TableHead>
                                <TableHead>Unit</TableHead>
                                <TableHead>Notes</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={7} className="h-24 text-center">
                                        <div className="flex justify-center items-center gap-2 text-muted-foreground">
                                            <Loader2 className="h-4 w-4 animate-spin" /> Loading...
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ) : data.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                                        No data found.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                data.map((item, idx) => {
                                    // Hacky: Try to find group name for display if possible, or just skip
                                    // Ideally backend returns group_name. For now let's just show details we have
                                    return (
                                        <TableRow key={idx}>
                                            <TableCell>{item.snapshot_date}</TableCell>
                                            <TableCell>
                                                <div className="font-medium">{item.product_name || "Unknown"}</div>
                                                <div className="text-xs text-muted-foreground">{item.sku_id}</div>
                                            </TableCell>
                                            <TableCell>
                                                <div className="text-sm">{item.group_name || "-"}</div>
                                            </TableCell>
                                            <TableCell>
                                                <div className="text-sm">{item.warehouse_name || item.warehouse_id}</div>
                                            </TableCell>
                                            <TableCell className="text-right font-medium">{item.quantity_on_hand.toLocaleString()}</TableCell>
                                            <TableCell className="text-right text-muted-foreground">{item.quantity_on_order.toLocaleString()}</TableCell>
                                            <TableCell className="text-right text-muted-foreground">{item.quantity_allocated?.toLocaleString() || 0}</TableCell>
                                            <TableCell>{item.unit}</TableCell>
                                            <TableCell className="text-xs text-muted-foreground">{item.notes}</TableCell>
                                        </TableRow>
                                    )
                                })
                            )}
                        </TableBody>
                        <TableFooter>
                            <TableRow className="bg-muted font-medium">
                                <TableCell colSpan={4}>Total</TableCell>
                                <TableCell className="text-right">{aggregates.total_on_hand.toLocaleString()}</TableCell>
                                <TableCell className="text-right text-muted-foreground">{aggregates.total_on_order.toLocaleString()}</TableCell>
                                <TableCell className="text-right text-muted-foreground">{aggregates.total_allocated.toLocaleString()}</TableCell>
                                <TableCell colSpan={2}></TableCell>
                            </TableRow>
                        </TableFooter>
                    </Table>

                    <div className="flex items-center justify-end space-x-2 py-4">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page === 1 || loading}
                        >
                            <ArrowLeft className="h-4 w-4 mr-2" /> Previous
                        </Button>
                        <div className="text-sm text-muted-foreground">
                            Page {page} of {totalPages || 1}
                        </div>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            disabled={page === totalPages || loading}
                        >
                            Next <ArrowRight className="h-4 w-4 ml-2" />
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
