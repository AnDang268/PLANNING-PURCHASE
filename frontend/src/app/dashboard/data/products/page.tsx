"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Check, ChevronsUpDown } from "lucide-react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { downloadCSV } from "@/lib/exportUtils"
import { cn } from "@/lib/utils"

interface Product {
    sku_id: string
    product_name: string
    group_id: string
    base_unit_id: string
    min_stock_level: number
    updated_at: string
    category: string // Legacy
    unit: string // Legacy
    distribution_profile_id?: string
}


export default function ProductsPage() {
    const router = useRouter()
    const [data, setData] = useState<Product[]>([])
    const [loading, setLoading] = useState(true)
    const [units, setUnits] = useState<any[]>([])
    const [groups, setGroups] = useState<any[]>([])
    const [profiles, setProfiles] = useState<any[]>([])

    // Add Dialog State
    const [addOpen, setAddOpen] = useState(false)
    const [formData, setFormData] = useState<any>({})

    const [totalCount, setTotalCount] = useState(0)
    const [page, setPage] = useState(1)
    const [search, setSearch] = useState("")

    // Filters
    const [groupFilter, setGroupFilter] = useState("ALL")
    const [openGroup, setOpenGroup] = useState(false)
    const [unitFilter, setUnitFilter] = useState<string | null>(null)

    // Master Data Load
    useEffect(() => {
        const fetchMasterData = async () => {
            try {
                const [uRes, gRes, pRes] = await Promise.all([
                    fetch(`${API_BASE_URL}/api/data/units`),
                    fetch(`${API_BASE_URL}/api/data/groups`),
                    fetch(`${API_BASE_URL}/api/data/profiles`)
                ])
                if (uRes.ok) setUnits(await uRes.json())
                if (gRes.ok) setGroups(await gRes.json())
                if (pRes.ok) setProfiles(await pRes.json())
            } catch (e) {
                console.error("Failed to load master data", e)
            }
        }
        fetchMasterData()
    }, [])

    const fetchData = async () => {
        setLoading(true)
        try {
            // Build Query params
            const limit = 20
            const skip = (page - 1) * limit

            const params = new URLSearchParams()
            params.append('skip', skip.toString())
            params.append('limit', limit.toString())
            if (search) params.append('search', search)
            if (groupFilter && groupFilter !== 'ALL') params.append('group_id', groupFilter)
            if (unitFilter) params.append('unit', unitFilter)

            const url = `${API_BASE_URL}/api/data/products?${params.toString()}`

            const pRes = await fetch(url)

            if (pRes.ok) {
                const json = await pRes.json()
                const rawData = json.data || []
                setTotalCount(json.total || 0)

                // Enhance data for display (names instead of IDs)
                // Use local state if available, otherwise fetch locally (for robustness)
                let localUnits = units
                let localGroups = groups

                if (localUnits.length === 0) {
                    const uRes = await fetch(`${API_BASE_URL}/api/data/units`)
                    if (uRes.ok) localUnits = await uRes.json()
                }
                if (localGroups.length === 0) {
                    const gRes = await fetch(`${API_BASE_URL}/api/data/groups`)
                    if (gRes.ok) localGroups = await gRes.json()
                }

                const groupsMap = new Map(localGroups.map((g: any) => [g.group_id, g.group_name]))
                const unitsMap = new Map(localUnits.map((u: any) => [u.unit_id, u.unit_name]))

                const enriched = rawData.map((p: any) => ({
                    ...p,
                    group_name: groupsMap.get(p.group_id) || p.category || '',
                    unit_name: unitsMap.get(p.base_unit_id) || p.unit || ''
                }))

                setData(enriched)
            }
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }



    useEffect(() => {
        fetchData()
    }, [page, search, groupFilter, unitFilter])

    const handleSync = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/sync/products`, { method: "POST" })
            if (res.ok) {
                alert("Sync Started Successfully")
                // Wait a bit then refresh
                setTimeout(() => {
                    fetchData()
                    setLoading(false)
                }, 2000)
            } else {
                alert("Sync Failed")
                setLoading(false)
            }
        } catch (e) {
            setLoading(false)
            alert("Network Error during Sync")
        }
    }

    const handleCancelSync = async () => {
        const res = await fetch(`${API_BASE_URL}/api/data/sync/cancel`, { method: "POST" })
        if (res.ok) alert("Cancellation Requested.")
    }

    const handleImport = async (file: File) => {
        setLoading(true)
        try {
            const fd = new FormData()
            fd.append("file", file)
            const res = await fetch(`${API_BASE_URL}/api/data/import/upload?type=products`, {
                method: "POST",
                body: fd
            })
            if (res.ok) {
                const json = await res.json()
                alert(`Upload Successful: ${json.message}`)
                fetchData()
            } else {
                const err = await res.json()
                alert(`Upload Failed: ${err.detail}`)
            }
        } catch (e) {
            alert("Network Error during Import")
        } finally {
            setLoading(false)
        }
    }

    const handleAddSubmit = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/products`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            })
            if (res.ok) {
                alert("Product Created")
                setAddOpen(false)
                setFormData({})
                fetchData()
            } else {
                const err = await res.json()
                alert(`Error: ${err.detail}`)
            }
        } catch (e) { alert("Network Error") }
    }

    const handleExport = async () => {
        try {
            // 1. Fetch ALL data (High limit)
            const res = await fetch(`${API_BASE_URL}/api/data/products?skip=0&limit=10000`)
            if (!res.ok) throw new Error("Failed to fetch data")
            const json = await res.json()
            const allData = json.data || []

            // 2. Prepare Maps
            let localUnits = units
            let localGroups = groups
            if (localUnits.length === 0) localUnits = await (await fetch(`${API_BASE_URL}/api/data/units`)).json()
            if (localGroups.length === 0) localGroups = await (await fetch(`${API_BASE_URL}/api/data/groups`)).json()

            const groupsMap = new Map(localGroups.map((g: any) => [g.group_id, g.group_name]))
            const unitsMap = new Map(localUnits.map((u: any) => [u.unit_id, u.unit_name]))

            // 3. Generate CSV Content
            const headers = ["sku_id", "product_name", "category", "unit", "min_stock_level", "updated_at"]
            const csvContent = [
                headers.join(","),
                ...allData.map((item: any) => [
                    `"${item.sku_id}"`,
                    `"${item.product_name}"`,
                    `"${groupsMap.get(item.group_id) || item.category || ''}"`,
                    `"${unitsMap.get(item.base_unit_id) || item.unit || ''}"`,
                    item.min_stock_level,
                    item.updated_at || ''
                ].join(","))
            ].join("\n")

            // 4. Download using Utility
            downloadCSV(csvContent, "products_export_all")

        } catch (e) {
            console.error(e)
            alert("Export failed!")
        }
    }

    const columns: ColumnDef<Product>[] = [
        { header: "SKU", accessorKey: "sku_id", className: "font-medium" },
        { header: "Product Name", accessorKey: "product_name" },
        {
            header: "Category/Group",
            accessorKey: "group_id",
            cell: (item) => {
                const g = groups.find(x => x.group_id === item.group_id)
                return g ? g.group_name : (item.category || '-')
            }
        },
        {
            header: "Unit",
            accessorKey: "base_unit_id",
            cell: (item) => {
                const u = units.find(x => x.unit_id === item.base_unit_id)
                return u ? u.unit_name : (item.unit || '-')
            }
        },
        { header: "Min Stock", accessorKey: "min_stock_level", className: "text-right" },
        {
            header: "Profile",
            accessorKey: "distribution_profile_id",
            cell: (item) => <div className="badge badge-outline text-xs">{item.distribution_profile_id || 'STD'}</div>
        },
        {
            header: "Sync Status",
            accessorKey: "updated_at",
            cell: (item) => item.updated_at ? 'Synced' : 'Pending'
        }
    ]

    return (
        <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" onClick={() => router.back()}>
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back
                </Button>
            </div>

            {/* Filters Section Top */}
            <div className="flex items-center gap-2 mb-2">
                <Popover open={openGroup} onOpenChange={setOpenGroup}>
                    <PopoverTrigger asChild>
                        <Button
                            variant="outline"
                            role="combobox"
                            aria-expanded={openGroup}
                            className="w-[250px] justify-between"
                        >
                            {groupFilter && groupFilter !== 'ALL'
                                ? groups.find((g) => g.group_id === groupFilter)?.group_name
                                : "Filter by Group..."}
                            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-[250px] p-0 z-[100]">
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
                                            value={group.group_name}
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

                {/* Unit Filter (Optional simplifed select) */}
                <Select value={unitFilter || "ALL"} onValueChange={(v) => { setUnitFilter(v === "ALL" ? null : v); setPage(1); }}>
                    <SelectTrigger className="w-[150px]">
                        <SelectValue placeholder="All Units" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="ALL">All Units</SelectItem>
                        {units.map(u => (
                            <SelectItem key={u.unit_id} value={u.unit_name}>
                                {u.unit_name}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <StandardDataTable
                title="Products Directory"
                description="Master list of all products."
                data={data}
                columns={columns}
                searchKey="product_name"
                loading={loading}

                // Server Side Props
                mode="server"
                totalCount={totalCount}
                page={page}
                pageSize={20}
                onPaginationChange={(p) => setPage(p)}
                onSearchChange={(q) => setSearch(q)}

                // NO FILTER CHANGE HANDLER HERE for Group/Unit as we handle it above
                // onFilterChange={(key, vals) => { ... }}

                filters={[]} // Clear default filters

                onSync={handleSync}
                onCancelSync={handleCancelSync}
                onImport={handleImport}
                onAdd={() => {
                    setFormData({})
                    setAddOpen(true)
                }}
                onEdit={(item: any) => {
                    setFormData({
                        sku_id: item.sku_id,
                        product_name: item.product_name,
                        category: item.group_name,
                        unit: item.unit_name,
                        min_stock_level: item.min_stock_level,
                        distribution_profile_id: item.distribution_profile_id
                    })
                    setAddOpen(true)
                }}
                onDelete={async (item: any) => {
                    if (!confirm(`Delete ${item.sku_id}?`)) return
                    await fetch(`${API_BASE_URL}/api/data/products/${item.sku_id}`, { method: "DELETE" })
                    fetchData()
                }}
            />

            <Dialog open={addOpen} onOpenChange={setAddOpen}>
                <DialogContent className="max-w-lg">
                    <DialogHeader>
                        <DialogTitle>{formData.sku_id && data.find(p => p.sku_id === formData.sku_id) ? "Edit Product" : "Add New Product"}</DialogTitle>
                        <DialogDescription>Manually add or edit a product.</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <Input
                            placeholder="SKU (Unique)"
                            value={formData.sku_id || ''}
                            disabled={!!(formData.sku_id && data.find(p => p.sku_id === formData.sku_id))}
                            onChange={e => setFormData({ ...formData, sku_id: e.target.value })}
                        />
                        <Input
                            placeholder="Product Name"
                            value={formData.product_name || ''}
                            onChange={e => setFormData({ ...formData, product_name: e.target.value })}
                        />

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Category</Label>
                                <Select value={formData.category} onValueChange={v => setFormData({ ...formData, category: v })}>
                                    <SelectTrigger><SelectValue placeholder="Select Group" /></SelectTrigger>
                                    <SelectContent>
                                        {groups.map(g => <SelectItem key={g.group_id} value={g.group_name}>{g.group_name}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label>Unit</Label>
                                <Select value={formData.unit} onValueChange={v => setFormData({ ...formData, unit: v })}>
                                    <SelectTrigger><SelectValue placeholder="Select Unit" /></SelectTrigger>
                                    <SelectContent>
                                        {units.map(u => <SelectItem key={u.unit_id} value={u.unit_name}>{u.unit_name}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label>Min Stock Level</Label>
                            <Input
                                type="number"
                                placeholder="0"
                                value={formData.min_stock_level || ''}
                                onChange={e => setFormData({ ...formData, min_stock_level: parseFloat(e.target.value) })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Demand Profile (Planning)</Label>
                            <Select value={formData.distribution_profile_id} onValueChange={v => setFormData({ ...formData, distribution_profile_id: v })}>
                                <SelectTrigger><SelectValue placeholder="Select Profile (e.g. B2C)" /></SelectTrigger>
                                <SelectContent>
                                    {profiles.map(p => (
                                        <SelectItem key={p.profile_id} value={p.profile_id}>
                                            <span className="font-medium">{p.profile_id}</span> - {p.profile_name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button onClick={async () => {
                            const isEdit = !!(formData.sku_id && data.find(p => p.sku_id === formData.sku_id))
                            const url = isEdit ? `${API_BASE_URL}/api/data/products/${formData.sku_id}` : `${API_BASE_URL}/api/data/products`
                            const method = isEdit ? "PUT" : "POST"

                            const res = await fetch(url, {
                                method,
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify(formData)
                            })
                            if (res.ok) {
                                setAddOpen(false)
                                setFormData({})
                                fetchData()
                            } else {
                                const err = await res.json()
                                alert(`Error: ${err.detail}`)
                            }
                        }}>{formData.sku_id && data.find(p => p.sku_id === formData.sku_id) ? "Save Changes" : "Create Product"}</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
