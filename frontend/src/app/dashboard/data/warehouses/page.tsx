"use client"

import { useState, useEffect } from "react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"

interface Warehouse {
    warehouse_id: string
    warehouse_name: string
    address: string
    updated_at: string
}

export default function WarehousesPage() {
    const [data, setData] = useState<Warehouse[]>([])
    const [loading, setLoading] = useState(true)

    const fetchData = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/warehouses`)
            if (res.ok) {
                const json = await res.json()
                setData(json)
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    useEffect(() => {
        fetchData()
    }, [])

    const handleSync = async () => {
        const res = await fetch(`${API_BASE_URL}/api/data/sync/warehouses`, { method: "POST" })
        if (res.ok) {
            alert("Sync Started for Warehouses.")
            setTimeout(fetchData, 2000)
        } else {
            alert("Sync Failed")
        }
    }

    const handleCancelSync = async () => {
        const res = await fetch(`${API_BASE_URL}/api/data/sync/cancel`, { method: "POST" })
        if (res.ok) alert("Cancellation Requested.")
    }

    const columns: ColumnDef<Warehouse>[] = [
        { header: "Warehouse ID", accessorKey: "warehouse_id", className: "font-medium" },
        { header: "Name", accessorKey: "warehouse_name" },
        { header: "Address", accessorKey: "address" },
        {
            header: "Last Updated",
            accessorKey: "updated_at",
            cell: (item) => item.updated_at ? new Date(item.updated_at).toLocaleDateString() : '-'
        }
    ]

    return (
        <StandardDataTable
            title="Warehouses"
            description="Manage storage locations."
            data={data}
            columns={columns}
            searchKey="warehouse_name"
            loading={loading}
            onSync={handleSync}
            onCancelSync={handleCancelSync}
        />
    )
}
