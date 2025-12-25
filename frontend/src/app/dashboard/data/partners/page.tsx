"use client"

import { useState, useEffect } from "react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface Vendor {
    vendor_id: string
    vendor_name: string
    address: string
    email: string
    phone: string
    lead_time_avg: number
}

export default function PartnersPage() {
    const [data, setData] = useState<Vendor[]>([])
    const [loading, setLoading] = useState(true)
    const [addOpen, setAddOpen] = useState(false)
    const [formData, setFormData] = useState<any>({})

    const fetchData = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/vendors?limit=1000`)
            if (res.ok) {
                const json = await res.json()
                setData(json.data || [])
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    useEffect(() => {
        fetchData()
    }, [])

    const handleSync = async () => {
        const res = await fetch(`${API_BASE_URL}/api/data/sync/partners`, { method: "POST" })
        if (res.ok) {
            alert("Sync Started for Partners (Vendors/Customers).")
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
        const res = await fetch(`${API_BASE_URL}/api/data/import/upload?type=vendors`, {
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
            const res = await fetch(`${API_BASE_URL}/api/data/vendors`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            })
            if (res.ok) {
                alert("Vendor Created")
                setAddOpen(false)
                setFormData({})
                fetchData()
            } else {
                const err = await res.json()
                alert(`Error: ${err.detail}`)
            }
        } catch (e) { alert("Network Error") }
    }

    const columns: ColumnDef<Vendor>[] = [
        { header: "Vendor ID", accessorKey: "vendor_id", className: "font-medium" },
        { header: "Name", accessorKey: "vendor_name" },
        { header: "Phone", accessorKey: "phone" },
        { header: "Email", accessorKey: "email" },
        { header: "Avg Lead Time", accessorKey: "lead_time_avg", className: "text-right" }
    ]

    return (
        <>
            <StandardDataTable
                title="Partners (Vendors)"
                description="Manage suppliers and customers."
                data={data}
                columns={columns}
                searchKey="vendor_name"
                loading={loading}
                onSync={handleSync}
                onCancelSync={handleCancelSync}
                onImport={handleImport}
                onAdd={() => setAddOpen(true)}
            />

            <Dialog open={addOpen} onOpenChange={setAddOpen}>
                <DialogContent className="max-w-lg">
                    <DialogHeader>
                        <DialogTitle>Add New Partner/Vendor</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <Input placeholder="Vendor ID" onChange={e => setFormData({ ...formData, vendor_id: e.target.value })} />
                        <Input placeholder="Vendor Name" onChange={e => setFormData({ ...formData, vendor_name: e.target.value })} />
                        <Input type="number" placeholder="Lead Time (Days)" onChange={e => setFormData({ ...formData, lead_time_avg: parseFloat(e.target.value) })} />
                    </div>
                    <DialogFooter>
                        <Button onClick={handleAddSubmit}>Save Vendor</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </>
    )
}
