"use client"

import { useState, useEffect } from "react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface Product {
    sku_id: string
    product_name: string
    group_id: string
    base_unit_id: string
    min_stock_level: number
    updated_at: string
    category: string // Legacy
    unit: string // Legacy
}

export default function ProductsPage() {
    const [data, setData] = useState<Product[]>([])
    const [loading, setLoading] = useState(true)
    const [units, setUnits] = useState<any[]>([])
    const [groups, setGroups] = useState<any[]>([])

    // Add Dialog State
    const [addOpen, setAddOpen] = useState(false)
    const [formData, setFormData] = useState<any>({})

    const fetchData = async () => {
        setLoading(true)
        try {
            const [pRes, uRes, gRes] = await Promise.all([
                fetch(`${API_BASE_URL}/api/data/products?limit=2000`), // Fetch more for client search
                fetch(`${API_BASE_URL}/api/data/units`),
                fetch(`${API_BASE_URL}/api/data/groups`)
            ])

            if (uRes.ok) setUnits(await uRes.json())
            if (gRes.ok) setGroups(await gRes.json())

            if (pRes.ok) {
                const json = await pRes.json()
                const rawData = json.data || []
                // Enhance data for filtering
                const groupsMap = new Map((await gRes.json()).map((g: any) => [g.group_id, g.group_name]))
                const unitsMap = new Map((await uRes.json()).map((u: any) => [u.unit_id, u.unit_name]))

                const enriched = rawData.map((p: any) => ({
                    ...p,
                    group_name: groupsMap.get(p.group_id) || p.category || '',
                    unit_name: unitsMap.get(p.base_unit_id) || p.unit || ''
                }))

                setData(enriched)
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    useEffect(() => {
        fetchData()
    }, [])

    const handleSync = async () => {
        const res = await fetch(`${API_BASE_URL}/api/data/sync/products`, { method: "POST" })
        if (res.ok) {
            alert("Sync Started for Products. This may take a while.")
        } else {
            alert("Sync Failed")
        }
    }

    const handleCancelSync = async () => {
        const res = await fetch(`${API_BASE_URL}/api/data/sync/cancel`, { method: "POST" })
        if (res.ok) alert("Cancellation Requested.")
    }

    const handleImport = async (file: File) => {
        const fd = new FormData()
        fd.append("file", file)
        const res = await fetch(`${API_BASE_URL}/api/data/import/upload?type=products`, {
            method: "POST",
            body: fd
        })
        if (res.ok) {
            alert("Upload Successful")
            fetchData()
        } else {
            const err = await res.json()
            alert(`Upload Failed: ${err.detail}`)
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
            header: "Sync Status",
            accessorKey: "updated_at",
            cell: (item) => item.updated_at ? 'Synced' : 'Pending'
        }
    ]

    return (
        <>
            <StandardDataTable
                title="Products Directory"
                description="Master list of all products."
                data={data}
                columns={columns}
                searchKey="product_name"
                filters={[
                    {
                        key: "group_name", // We need to ensure we filter by the text value or ensure logic maps group_id
                        title: "Category",
                        options: groups.map(g => ({ label: g.group_name, value: g.group_name })) // Simple string matching first
                    },
                    {
                        key: "unit_name", // Simpler to Filter if we prep data
                        title: "Unit",
                        options: units.map(u => ({ label: u.unit_name, value: u.unit_name }))
                    }
                ]}
                loading={loading}
                onSync={handleSync}
                onCancelSync={handleCancelSync}
                onImport={handleImport}
                onAdd={() => setAddOpen(true)}
            />

            <Dialog open={addOpen} onOpenChange={setAddOpen}>
                <DialogContent className="max-w-lg">
                    <DialogHeader>
                        <DialogTitle>Add New Product</DialogTitle>
                        <DialogDescription>Manually add a product to the system.</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <Input placeholder="SKU (Unique)" onChange={e => setFormData({ ...formData, sku_id: e.target.value })} />
                        <Input placeholder="Product Name" onChange={e => setFormData({ ...formData, product_name: e.target.value })} />

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Category</Label>
                                <Select onValueChange={v => setFormData({ ...formData, category: v })}>
                                    <SelectTrigger><SelectValue placeholder="Select Group" /></SelectTrigger>
                                    <SelectContent>
                                        {groups.map(g => <SelectItem key={g.group_id} value={g.group_name}>{g.group_name}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label>Unit</Label>
                                <Select onValueChange={v => setFormData({ ...formData, unit: v })}>
                                    <SelectTrigger><SelectValue placeholder="Select Unit" /></SelectTrigger>
                                    <SelectContent>
                                        {units.map(u => <SelectItem key={u.unit_id} value={u.unit_name}>{u.unit_name}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label>Min Stock Level</Label>
                            <Input type="number" placeholder="0" onChange={e => setFormData({ ...formData, min_stock_level: parseFloat(e.target.value) })} />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button onClick={handleAddSubmit}>Save Product</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </>
    )
}
