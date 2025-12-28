"use client"

import { useState, useEffect } from "react"
import { API_BASE_URL } from "@/config"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableFooter } from "@/components/ui/table"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Loader2, Search, ArrowLeft, ArrowRight, RefreshCw, Upload, FileDown, Edit, Trash2 } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { format } from "date-fns"

// Force Refresh
interface InventoryItem {
    snapshot_date: string
    warehouse_id: string
    warehouse_name: string
    sku_id: string
    product_name: string
    group_id: string
    group_name: string
    quantity_on_hand: number
    quantity_original?: number
    quantity_update?: number
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

interface DateRange {
    from: Date | undefined
    to: Date | undefined
}

export default function InventoryPage() {
    const [data, setData] = useState<InventoryItem[]>([])
    const [loading, setLoading] = useState(true)
    const [page, setPage] = useState(1)
    const [total, setTotal] = useState(0)
    const [aggregates, setAggregates] = useState({ total_on_hand: 0, total_on_order: 0, total_allocated: 0 })
    const { toast } = useToast()

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

            const res = await fetch(`${API_BASE_URL}/api/data/inventory?${params.toString()}`)
            if (res.ok) {
                const json = await res.json()
                setData(json.data)
                setTotal(json.total)
                if (json.aggregates) setAggregates(json.aggregates)
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

    const handleDownloadTemplate = () => window.open(`${API_BASE_URL}/api/data/template/inventory_manual`, '_blank')

    const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return
        const formData = new FormData()
        formData.append("file", file)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/inventory/import`, { method: "POST", body: formData })
            const json = await res.json()
            if (res.ok) {
                toast({ title: "Success", description: json.message })
                fetchData()
            } else {
                toast({ title: "Import Failed", description: json.detail || "Unknown error", variant: "destructive" })
            }
        } catch (err) {
            toast({ title: "Error", description: "Import Error", variant: "destructive" })
        } finally {
            e.target.value = ""
        }
    }

    const handleSync = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/crm/sync-inventory`, { method: 'POST' })
            if (res.ok) {
                toast({ title: "Sync Started", description: "Inventory sync running..." })
                setTimeout(fetchData, 2000)
            } else {
                toast({ title: "Sync Failed", variant: "destructive" })
            }
        } catch (e) {
            toast({ title: "Sync Error", variant: "destructive" })
        } finally {
            setLoading(false)
        }
    }

    const [editingItem, setEditingItem] = useState<InventoryItem | null>(null)
    const handleUpdateSuccess = () => {
        setEditingItem(null)
        fetchData()
        toast({ title: "Updated", description: "Inventory updated successfully" })
    }

    return (
        <div className="container py-8 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Opening Stock</h2>
                    <p className="text-muted-foreground">
                        Manage manual Opening Stock checkpoints. Overrides calculated planning values.
                    </p>
                    <div className="mt-2 text-sm font-medium text-blue-600">
                        Total On Hand: {aggregates?.total_on_hand?.toLocaleString() || 0}
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <Button onClick={handleDownloadTemplate} variant="outline" size="sm">
                        <FileDown className="mr-2 h-4 w-4" /> Template
                    </Button>
                    <div className="flex items-center space-x-2">
                        <Input id="inv-import" type="file" className="hidden" accept=".xlsx,.xls,.csv" onChange={handleImport} />
                        <Button variant="outline" size="sm" onClick={() => document.getElementById('inv-import')?.click()}>
                            <Upload className="mr-2 h-4 w-4" /> Import
                        </Button>
                    </div>
                    <Button onClick={handleSync} variant="secondary" size="sm">
                        <RefreshCw className="mr-2 h-4 w-4" /> Sync
                    </Button>
                </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
                <div className="w-full sm:w-[250px] relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="Search product..." value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSearch()} className="pl-8" />
                </div>
                <Select value={groupFilter} onValueChange={setGroupFilter}>
                    <SelectTrigger className="w-[180px]"><SelectValue placeholder="Product Group" /></SelectTrigger>
                    <SelectContent>
                        <SelectItem value="ALL">All Groups</SelectItem>
                        {groups.map(g => <SelectItem key={g.group_id} value={g.group_id}>{g.group_name}</SelectItem>)}
                    </SelectContent>
                </Select>
                <Select value={warehouseFilter} onValueChange={setWarehouseFilter}>
                    <SelectTrigger className="w-[180px]"><SelectValue placeholder="Warehouse" /></SelectTrigger>
                    <SelectContent>
                        <SelectItem value="ALL">All Warehouses</SelectItem>
                        {warehouses.map(w => <SelectItem key={w.warehouse_id} value={w.warehouse_id}>{w.warehouse_name}</SelectItem>)}
                    </SelectContent>
                </Select>
                <div className="flex-1"></div>
                <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">Month:</span>
                    <Input type="month" className="w-[180px]" onChange={(e) => {
                        if (e.target.value) {
                            const d = new Date(e.target.value)
                            setDateRange({ from: new Date(d.getFullYear(), d.getMonth(), 1), to: new Date(d.getFullYear(), d.getMonth() + 1, 0) })
                        } else setDateRange({ from: undefined, to: undefined })
                    }}
                    />
                </div>
            </div>

            <Card>
                <CardHeader className="pb-4"><CardTitle>Inventory Checkpoints</CardTitle></CardHeader>
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
                                <TableHead>Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow><TableCell colSpan={9} className="text-center py-8"><Loader2 className="animate-spin mx-auto" /></TableCell></TableRow>
                            ) : data.length === 0 ? (
                                <TableRow><TableCell colSpan={9} className="text-center py-4">No data</TableCell></TableRow>
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
                                        <TableCell className="text-right">
                                            {(item.quantity_update !== undefined && item.quantity_update !== null && item.quantity_update > 0) ? (
                                                <div className="flex flex-col items-end">
                                                    <span className="font-bold text-blue-600" title="Actual Update">{item.quantity_update.toLocaleString()}</span>
                                                    <span className="text-xs text-muted-foreground line-through" title="Opening Book">{item.quantity_original?.toLocaleString()}</span>
                                                </div>
                                            ) : (
                                                <span className="font-bold">{item.quantity_on_hand.toLocaleString()}</span>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-right text-muted-foreground">{item.quantity_on_order.toLocaleString()}</TableCell>
                                        <TableCell className="text-right text-muted-foreground">{item.quantity_allocated?.toLocaleString() || 0}</TableCell>
                                        <TableCell>{item.unit}</TableCell>
                                        <TableCell>
                                            <div className="flex gap-1 justify-end">
                                                <Button variant="ghost" size="icon" onClick={() => setEditingItem(item)} title="Edit">
                                                    <Edit className="h-4 w-4 text-blue-500" />
                                                </Button>
                                                <Button variant="ghost" size="icon" className="hover:bg-red-100" onClick={async () => {
                                                    if (!confirm("Are you sure you want to delete this record?")) return;
                                                    try {
                                                        const res = await fetch(`${API_BASE_URL}/api/data/inventory/delete?sku_id=${item.sku_id}&warehouse_id=${item.warehouse_id}&snapshot_date=${item.snapshot_date}`, { method: 'DELETE' });
                                                        if (res.ok) {
                                                            toast({ title: "Deleted", description: "Record deleted" });
                                                            fetchData();
                                                        } else {
                                                            alert("Failed to delete");
                                                        }
                                                    } catch (e) {
                                                        console.error(e);
                                                        alert("Error deleting");
                                                    }
                                                }} title="Delete">
                                                    <Trash2 className="h-4 w-4 text-red-500" />
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                        <TableFooter>
                            <TableRow>
                                <TableCell colSpan={4} className="font-bold">Total Page</TableCell>
                                <TableCell className="text-right font-bold">
                                    {data.reduce((sum, item) => sum + (item.quantity_update && item.quantity_update > 0 ? item.quantity_update : item.quantity_on_hand), 0).toLocaleString()}
                                </TableCell>
                                <TableCell className="text-right font-bold">
                                    {data.reduce((sum, item) => sum + item.quantity_on_order, 0).toLocaleString()}
                                </TableCell>
                                <TableCell className="text-right font-bold">
                                    {data.reduce((sum, item) => sum + (item.quantity_allocated || 0), 0).toLocaleString()}
                                </TableCell>
                                <TableCell colSpan={2} />
                            </TableRow>
                        </TableFooter>
                    </Table>
                    <div className="flex items-center justify-end space-x-2 py-4">
                        <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1 || loading}><ArrowLeft className="h-4 w-4" /></Button>
                        <div className="text-sm">Page {page} of {Math.ceil(total / 20)}</div>
                        <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / 20) || loading}><ArrowRight className="h-4 w-4" /></Button>
                    </div>
                </CardContent>
            </Card>

            {editingItem && (
                <EditInventoryDialog
                    item={editingItem}
                    groups={groups}
                    warehouses={warehouses}
                    open={!!editingItem}
                    onOpenChange={(open) => !open && setEditingItem(null)}
                    onSuccess={handleUpdateSuccess}
                />
            )}
        </div>
    )
}

function EditInventoryDialog({ item, groups, warehouses, open, onOpenChange, onSuccess }: { item: InventoryItem, groups: ProductGroup[], warehouses: Warehouse[], open: boolean, onOpenChange: (open: boolean) => void, onSuccess: () => void }) {
    const [qty, setQty] = useState(item.quantity_on_hand)
    const [qtyUpdate, setQtyUpdate] = useState(item.quantity_update || 0) // New state
    const [selectedGroup, setSelectedGroup] = useState(item.group_id || 'ALL')
    const [selectedWarehouse, setSelectedWarehouse] = useState(item.warehouse_id)
    const [saving, setSaving] = useState(false)

    const handleSave = async () => {
        setSaving(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/inventory/update`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sku_id: item.sku_id,
                    warehouse_id: item.warehouse_id, // Original ID
                    new_warehouse_id: selectedWarehouse !== item.warehouse_id ? selectedWarehouse : null, // New ID if changed
                    snapshot_date: item.snapshot_date,
                    quantity_on_hand: qty,
                    quantity_update: qtyUpdate !== 0 ? qtyUpdate : null, // Pass new field
                    group_id: selectedGroup !== 'ALL' ? selectedGroup : null
                })
            })
            if (res.ok) {
                onSuccess()
                onOpenChange(false)
            } else {
                alert("Failed to update")
            }
        } catch (e) {
            console.error(e)
            alert("Error updating")
        } finally {
            setSaving(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>Adjust Inventory: {item.product_name}</DialogTitle>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">SKU</Label>
                        <div className="col-span-3 font-mono text-sm">{item.sku_id}</div>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">Warehouse</Label>
                        <div className="col-span-3">
                            <Select value={selectedWarehouse} onValueChange={setSelectedWarehouse}>
                                <SelectTrigger><SelectValue placeholder="Select Warehouse" /></SelectTrigger>
                                <SelectContent>
                                    {warehouses.map(w => (
                                        <SelectItem key={w.warehouse_id} value={w.warehouse_id}>{w.warehouse_name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">Date</Label> <span className="col-span-3">{item.snapshot_date}</span>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">Product Group</Label>
                        <div className="col-span-3">
                            <Select value={selectedGroup} onValueChange={setSelectedGroup}>
                                <SelectTrigger><SelectValue placeholder="Select Group" /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="ALL">Keep Original</SelectItem>
                                    {groups.map(g => <SelectItem key={g.group_id} value={g.group_id}>{g.group_name}</SelectItem>)}
                                </SelectContent>
                            </Select>
                        </div>
                        <Label>Opening Qty</Label>
                        <Input type="number" value={qty} onChange={(e) => setQty(parseFloat(e.target.value))} className="col-span-3" />
                        <Label className="text-blue-600 font-bold">Actual Qty</Label>
                        <div className="col-span-3 flex items-center gap-2">
                            <Input type="number" value={qtyUpdate} onChange={(e) => setQtyUpdate(parseFloat(e.target.value))} placeholder="0 if none" />
                            <span className="text-xs text-muted-foreground w-32">Overrides Opening if {'>'} 0</span>
                        </div>
                    </div>
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
                    <Button onClick={handleSave} disabled={saving}>{saving ? "Saving..." : "Save Changes"}</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
