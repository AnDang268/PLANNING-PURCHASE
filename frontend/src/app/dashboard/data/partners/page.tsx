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

interface Vendor {
    vendor_id: string
    vendor_name: string
    lead_time_avg: number
    updated_at: string
}

export default function PartnersPage() {
    const router = useRouter()
    const [data, setData] = useState<Vendor[]>([])
    const [loading, setLoading] = useState(true)

    // CRUD
    const [open, setOpen] = useState(false)
    const [isEdit, setIsEdit] = useState(false)
    const [formData, setFormData] = useState<Partial<Vendor>>({})

    const fetchData = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/vendors`)
            if (res.ok) {
                const json = await res.json()
                setData(json.data || [])
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    useEffect(() => { fetchData() }, [])

    const handleSync = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/sync/partners`, { method: "POST" })
            if (res.ok) {
                alert("Sync Started")
                setTimeout(() => {
                    fetchData()
                    setLoading(false)
                }, 3000)
            } else {
                alert("Sync Failed")
                setLoading(false)
            }
        } catch (e) { setLoading(false) }
    }

    const handleExport = async () => {
        const headers = ["vendor_id", "vendor_name", "lead_time_avg", "updated_at"]
        const csvContent = [
            headers.join(","),
            ...data.map(item => [
                `"${item.vendor_id}"`,
                `"${item.vendor_name}"`,
                `"${item.lead_time_avg || 0}"`,
                `"${item.updated_at || ''}"`
            ].join(","))
        ].join("\n")
        downloadCSV(csvContent, "partners_export")
    }

    const handleSubmit = async () => {
        const method = isEdit ? "PUT" : "POST"
        // Note: Partners/Vendors create endpoint is /api/data/vendors
        const url = isEdit
            ? `${API_BASE_URL}/api/data/vendors/${formData.vendor_id}` // UPDATE endpoint needs to be checked
            : `${API_BASE_URL}/api/data/vendors`

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

    const handleDelete = async (item: Vendor) => {
        if (!confirm(`Delete ${item.vendor_name}?`)) return
        await fetch(`${API_BASE_URL}/api/data/vendors/${item.vendor_id}`, { method: "DELETE" })
        fetchData()
    }

    const handleImport = async (file: File) => {
        setLoading(true)
        try {
            const formData = new FormData()
            formData.append("file", file)
            const res = await fetch(`${API_BASE_URL}/api/data/import/upload?type=vendors`, {
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

    const columns: ColumnDef<Vendor>[] = [
        { header: "Partner ID", accessorKey: "vendor_id", className: "font-medium" },
        { header: "Partner Name", accessorKey: "vendor_name" },
        {
            header: "Lead Time",
            accessorKey: "lead_time_avg",
            cell: (item) => `${item.lead_time_avg} days`
        },
        {
            header: "Last Synced",
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
                title="Partners (Vendors)"
                description="Manage Suppliers and Customers."
                data={data}
                columns={columns}
                searchKey="vendor_name"
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
                        <DialogTitle>{isEdit ? "Edit Partner" : "Add Partner"}</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="space-y-2">
                            <Label>ID</Label>
                            <Input
                                disabled={isEdit}
                                value={formData.vendor_id || ''}
                                onChange={e => setFormData({ ...formData, vendor_id: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Name</Label>
                            <Input
                                value={formData.vendor_name || ''}
                                onChange={e => setFormData({ ...formData, vendor_name: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Lead Time (Days)</Label>
                            <Input
                                type="number"
                                value={formData.lead_time_avg || 0}
                                onChange={e => setFormData({ ...formData, lead_time_avg: parseFloat(e.target.value) })}
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
