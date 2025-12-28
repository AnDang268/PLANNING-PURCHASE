"use client"

import { useState, useEffect } from "react"
import { API_BASE_URL } from "@/config"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableFooter } from "@/components/ui/table"
import { Loader2, Search, ArrowLeft, ArrowRight, RefreshCw } from "lucide-react"

import { format } from "date-fns"

interface InventoryItem {
    snapshot_date: string
    warehouse_name: string
    warehouse_id: string
    sku_id: string
    product_name: string
    group_name: string
    quantity_on_hand: number
    quantity_on_order: number
    quantity_allocated: number
    unit: string
}

interface Warehouse {
    warehouse_id: string
    warehouse_name: string
}

interface ProductGroup {
    group_id: string
    group_name: string
}

interface DateRange {
    from: Date | undefined
    to: Date | undefined
}

export default function SnapshotsPage() {
    const [data, setData] = useState<InventoryItem[]>([])
    const [loading, setLoading] = useState(true)
    const [total, setTotal] = useState(0)
    const [page, setPage] = useState(1)

    // Aggregates
    const [aggregates, setAggregates] = useState({ total_on_hand: 0 })

    // Filters
    const [dateRange, setDateRange] = useState<DateRange>({ from: undefined, to: undefined })
    const [search, setSearch] = useState("")
    const [warehouseFilter, setWarehouseFilter] = useState("ALL")
    const [groupFilter, setGroupFilter] = useState("ALL")

    // Filter Options
    const [warehouses, setWarehouses] = useState<Warehouse[]>([])
    const [groups, setGroups] = useState<ProductGroup[]>([])

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
            const limit = 50
            const skip = (page - 1) * limit
            const params = new URLSearchParams()
            params.append('skip', skip.toString())
            params.append('limit', limit.toString())

            if (dateRange.from) params.append('start_date', format(dateRange.from, 'yyyy-MM-dd'))
            if (dateRange.to) params.append('end_date', format(dateRange.to, 'yyyy-MM-dd'))

            if (search) params.append('search', search)
            if (warehouseFilter && warehouseFilter !== 'ALL') params.append('warehouse_id', warehouseFilter)
            if (groupFilter && groupFilter !== 'ALL') params.append('group_id', groupFilter)

            const res = await fetch(`${API_BASE_URL}/api/data/snapshots?${params.toString()}`)
            if (res.ok) {
                const json = await res.json()
                setData(json.data)
                setTotal(json.total || 0)
                if (json.aggregates) setAggregates(json.aggregates)
            }
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        setPage(1)
        fetchData()
    }, [warehouseFilter, groupFilter, dateRange])

    useEffect(() => {
        fetchData()
    }, [page])

    const handleSearch = () => {
        setPage(1)
        fetchData()
    }

    return (
        <div className="container py-8 space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Realtime Stock</h2>
                <p className="text-muted-foreground">
                    Read-only view of inventory synced from External Systems (e.g. MISA).
                </p>
                {/* Summary Metrics */}
                <div className="mt-4 flex flex-wrap gap-6">
                    <div className="border rounded-md px-4 py-2 bg-muted/50">
                        <span className="text-sm font-medium text-muted-foreground block">Total Records</span>
                        <span className="text-2xl font-bold">{total}</span>
                    </div>
                    <div className="border rounded-md px-4 py-2 bg-muted/50">
                        <span className="text-sm font-medium text-muted-foreground block">Total On Hand</span>
                        <span className="text-2xl font-bold text-blue-600">{aggregates.total_on_hand.toLocaleString()}</span>
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="w-full sm:w-[250px]">
                    <div className="relative">
                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search product..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            className="pl-8"
                        />
                    </div>
                </div>

                <Select value={groupFilter} onValueChange={setGroupFilter}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Product Group" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="ALL">All Groups</SelectItem>
                        {groups.map(g => (
                            <SelectItem key={g.group_id} value={g.group_id}>{g.group_name}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>

                <Select value={warehouseFilter} onValueChange={setWarehouseFilter}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Warehouse" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="ALL">All Warehouses</SelectItem>
                        {warehouses.map(w => (
                            <SelectItem key={w.warehouse_id} value={w.warehouse_id}>{w.warehouse_name}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>

                <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">Month:</span>
                    <Input
                        type="month"
                        className="w-[180px]"
                        onChange={(e) => {
                            if (e.target.value) {
                                const d = new Date(e.target.value)
                                // Standardize to Month Start/End
                                setDateRange({
                                    from: new Date(d.getFullYear(), d.getMonth(), 1),
                                    to: new Date(d.getFullYear(), d.getMonth() + 1, 0)
                                })
                            } else {
                                setDateRange({ from: undefined, to: undefined })
                            }
                        }}
                    />
                </div>

                <div className="flex-1"></div>
                <Button variant="outline" onClick={fetchData}>
                    <RefreshCw className="mr-2 h-4 w-4" /> Refresh
                </Button>
            </div>

            <Card>
                <CardHeader className="pb-4">
                    <CardTitle>Snapshot Data</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Date</TableHead>
                                <TableHead>Product</TableHead>
                                <TableHead>Group</TableHead>
                                <TableHead>Warehouse</TableHead>
                                <TableHead className="text-right">On Hand</TableHead>
                                <TableHead className="text-right">On Order</TableHead>
                                <TableHead className="text-right">Allocated</TableHead>
                                <TableHead>Unit</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={8} className="text-center py-8"><Loader2 className="animate-spin mx-auto" /></TableCell>
                                </TableRow>
                            ) : data.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={8} className="text-center py-4">No data found</TableCell>
                                </TableRow>
                            ) : (
                                data.map((item, idx) => (
                                    <TableRow key={idx}>
                                        <TableCell>{item.snapshot_date}</TableCell>
                                        <TableCell>
                                            <div className="font-medium">{item.product_name}</div>
                                            <div className="text-xs text-muted-foreground">{item.sku_id}</div>
                                        </TableCell>
                                        <TableCell>{item.group_name || "-"}</TableCell>
                                        <TableCell>{item.warehouse_name || item.warehouse_id}</TableCell>
                                        <TableCell className="text-right font-bold">{item.quantity_on_hand.toLocaleString()}</TableCell>
                                        <TableCell className="text-right text-muted-foreground">{item.quantity_on_order.toLocaleString()}</TableCell>
                                        <TableCell className="text-right text-muted-foreground">{item.quantity_allocated?.toLocaleString() || 0}</TableCell>
                                        <TableCell>{item.unit}</TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                        <TableFooter>
                            <TableRow>
                                <TableCell colSpan={4} className="font-bold">Total Page</TableCell>
                                <TableCell className="text-right font-bold">
                                    {data.reduce((sum, item) => sum + item.quantity_on_hand, 0).toLocaleString()}
                                </TableCell>
                                <TableCell className="text-right font-bold">
                                    {data.reduce((sum, item) => sum + item.quantity_on_order, 0).toLocaleString()}
                                </TableCell>
                                <TableCell className="text-right font-bold">
                                    {data.reduce((sum, item) => sum + (item.quantity_allocated || 0), 0).toLocaleString()}
                                </TableCell>
                                <TableCell />
                            </TableRow>
                        </TableFooter>
                    </Table>

                    {/* Pagination Context */}
                    <div className="flex items-center justify-end space-x-2 py-4">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage((p) => Math.max(1, p - 1))}
                            disabled={page === 1 || loading}
                        >
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                        <div className="text-sm">
                            Page {page} of {Math.ceil(total / 50)}
                        </div>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage((p) => p + 1)}
                            disabled={page >= Math.ceil(total / 50) || loading}
                        >
                            <ArrowRight className="h-4 w-4" />
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
