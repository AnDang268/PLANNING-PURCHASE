"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { downloadCSV } from "@/lib/exportUtils"

interface Warehouse {
    warehouse_id: string
    warehouse_name: string
    branch_id: string
    updated_at: string
}

export default function WarehousesPage() {
    const router = useRouter()
    const [data, setData] = useState<Warehouse[]>([])
    const [loading, setLoading] = useState(true)

    // CRUD
    const [open, setOpen] = useState(false)
    const [isEdit, setIsEdit] = useState(false)
    const [formData, setFormData] = useState<Partial<Warehouse>>({})

    const fetchData = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/warehouses`)
            if (res.ok) setData(await res.json())
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    useEffect(() => { fetchData() }, [])

    const handleSync = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/sync/warehouses`, { method: "POST" })
            if (res.ok) {
                alert("Sync Started")
                setTimeout(() => {
                    fetchData()
                    setLoading(false)
                }, 2000)
            } else {
                alert("Sync Failed")
                setLoading(false)
            }
        } catch (e) { setLoading(false) }
    }

    const handleExport = async () => {
        const headers = ["warehouse_id", "warehouse_name", "branch_id", "updated_at"]
        const csvContent = [
            headers.join(","),
            ...data.map(item => [
                `"${item.warehouse_id}"`,
                `"${item.warehouse_name}"`,
                `"${item.branch_id || ''}"`,
                `"${item.updated_at || ''}"`
            ].join(","))
        ].join("\n")
        downloadCSV(csvContent, "warehouses_export")
    }

    const handleSubmit = async () => {
        const method = isEdit ? "PUT" : "POST"
        const url = isEdit
            ? `${API_BASE_URL}/api/data/warehouses/${formData.warehouse_id}`
            : `${API_BASE_URL}/api/data/warehouses`

        try {
            const res = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            })
            if (res.ok) {
                setOpen(false)
                fetchData()
            } else {
                const err = await res.json()
                alert(`Error: ${err.detail}`)
            }
        } catch (e) { alert("Network Error") }
    }

    const handleDelete = async (item: Warehouse) => {
        if (!confirm(`Delete ${item.warehouse_name}?`)) return
        await fetch(`${API_BASE_URL}/api/data/warehouses/${item.warehouse_id}`, { method: "DELETE" })
        fetchData()
    }

    const handleImport = async (file: File) => {
        setLoading(true)
        try {
            const formData = new FormData()
            formData.append("file", file)
            const res = await fetch(`${API_BASE_URL}/api/data/import/upload?type=warehouses`, {
                method: "POST",
                body: formData
            })
            if (res.ok) {
                const json = await res.json()
                alert(`Import Successful: ${json.message}`)
                fetchData()
            } else {
                const err = await res.json()
                alert(`Import Failed: ${err.detail}`)
            }
        } catch (e) { alert("Network Error") }
        finally { setLoading(false) }
    }


    const columns: ColumnDef<Warehouse>[] = [
        { header: "Stock ID", accessorKey: "warehouse_id", className: "font-medium" },
        { header: "Warehouse Name", accessorKey: "warehouse_name" },
        { header: "Branch", accessorKey: "branch_id" },
        {
            header: "Last Updated",
            accessorKey: "updated_at",
            cell: (item) => item.updated_at ? new Date(item.updated_at).toLocaleDateString() : '-'
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
            <StandardDataTable
                title="Warehouses"
                description="Manage Stock locations."
                data={data}
                columns={columns}
                searchKey="warehouse_name"
                loading={loading}
                onSync={handleSync}
                onExport={handleExport}
                onImport={handleImport}
                onAdd={() => {
                    setFormData({})
                    setIsEdit(false)
                    setOpen(true)
                }}
                onEdit={(item) => {
                    setFormData(item)
                    setIsEdit(true)
                    setOpen(true)
                }}
                onDelete={handleDelete}
            />

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>{isEdit ? "Edit Warehouse" : "Add Warehouse"}</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="space-y-2">
                            <Label>ID</Label>
                            <Input
                                disabled={isEdit}
                                value={formData.warehouse_id || ''}
                                onChange={e => setFormData({ ...formData, warehouse_id: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Name</Label>
                            <Input
                                value={formData.warehouse_name || ''}
                                onChange={e => setFormData({ ...formData, warehouse_name: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Branch ID</Label>
                            <Input
                                value={formData.branch_id || ''}
                                onChange={e => setFormData({ ...formData, branch_id: e.target.value })}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button onClick={handleSubmit}>Save</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
