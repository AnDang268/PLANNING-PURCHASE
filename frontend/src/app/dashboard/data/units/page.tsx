"use client"

import { useState, useEffect } from "react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"

interface Unit {
    unit_id: string
    unit_name: string
    updated_at: string
}

export default function UnitsPage() {
    const [data, setData] = useState<Unit[]>([])
    const [loading, setLoading] = useState(true)

    const fetchData = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/units`)
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
        const res = await fetch(`${API_BASE_URL}/api/data/sync/units`, { method: "POST" })
        if (res.ok) {
            alert("Sync Started for Units.")
            setTimeout(fetchData, 2000)
        } else {
            alert("Sync Failed")
        }
    }

    const handleCancelSync = async () => {
        const res = await fetch(`${API_BASE_URL}/api/data/sync/cancel`, { method: "POST" })
        if (res.ok) alert("Cancellation Requested.")
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

    return (
        <StandardDataTable
            title="Units of Measure"
            description="Manage units for products."
            data={data}
            columns={columns}
            searchKey="unit_name"
            loading={loading}
            onSync={handleSync}
            onCancelSync={handleCancelSync}
        />
    )
}
