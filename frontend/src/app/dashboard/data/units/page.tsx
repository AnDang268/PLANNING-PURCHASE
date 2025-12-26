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

interface Unit {
    unit_id: string
    unit_name: string
    updated_at: string
}

export default function UnitsPage() {
    const router = useRouter()
    const [data, setData] = useState<Unit[]>([])
    const [loading, setLoading] = useState(true)

    // CRUD State
    const [open, setOpen] = useState(false)
    const [isEdit, setIsEdit] = useState(false)
    const [formData, setFormData] = useState<Partial<Unit>>({})

    const fetchData = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/units`)
            if (res.ok) setData(await res.json())
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    useEffect(() => { fetchData() }, [])

    const handleSync = async () => {
        const res = await fetch(`${API_BASE_URL}/api/data/sync/units`, { method: "POST" })
        if (res.ok) {
            alert("Sync Started")
            setTimeout(fetchData, 2000)
        } else alert("Sync Failed")
    }

    const handleSubmit = async () => {
        const method = isEdit ? "PUT" : "POST"
        const url = isEdit
            ? `${API_BASE_URL}/api/data/units/${formData.unit_id}`
            : `${API_BASE_URL}/api/data/units`

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

    const handleDelete = async (item: Unit) => {
        if (!confirm(`Delete ${item.unit_name}?`)) return
        await fetch(`${API_BASE_URL}/api/data/units/${item.unit_id}`, { method: "DELETE" })
        fetchData()
    }

    const columns: ColumnDef<Unit>[] = [
        { header: "Unit ID", accessorKey: "unit_id", className: "font-medium" },
        { header: "Unit Name", accessorKey: "unit_name" },
        {
            header: "Last Updated",
            accessorKey: "updated_at",
            cell: (item) => item.updated_at ? new Date(item.updated_at).toLocaleDateString() : '-'
        }
    ]

    const handleExport = async () => {
        const headers = ["unit_id", "unit_name", "updated_at"]
        const csvContent = [
            headers.join(","),
            ...data.map(item => [
                `"${item.unit_id}"`,
                `"${item.unit_name}"`,
                `"${item.updated_at || ''}"`
            ].join(","))
        ].join("\n")
        downloadCSV(csvContent, "units_export")
    }

    const handleImport = async (file: File) => {
        setLoading(true)
        try {
            const fd = new FormData()
            fd.append("file", file)
            const res = await fetch(`${API_BASE_URL}/api/data/import/upload?type=units`, {
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

    return (
        <>
            <StandardDataTable
                title="Units of Measure"
                description="Manage units for products."
                data={data}
                columns={columns}
                searchKey="unit_name"
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
                        <DialogTitle>{isEdit ? "Edit Unit" : "Add Unit"}</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="space-y-2">
                            <Label>Unit ID</Label>
                            <Input
                                disabled={isEdit}
                                value={formData.unit_id || ''}
                                onChange={e => setFormData({ ...formData, unit_id: e.target.value })}
                                placeholder="e.g. PCS"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Unit Name</Label>
                            <Input
                                value={formData.unit_name || ''}
                                onChange={e => setFormData({ ...formData, unit_name: e.target.value })}
                                placeholder="e.g. Pieces"
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button onClick={handleSubmit}>Save</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </>
    )
}
