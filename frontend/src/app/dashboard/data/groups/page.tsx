"use client"

import { useState, useEffect } from "react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"

interface Group {
    group_id: string
    group_name: string
    misa_code: string
    parent_id: string
    updated_at: string
}

export default function GroupsPage() {
    const [data, setData] = useState<Group[]>([])
    const [loading, setLoading] = useState(true)

    const fetchData = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/groups`)
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
        const res = await fetch(`${API_BASE_URL}/api/data/sync/groups`, { method: "POST" })
        if (res.ok) {
            alert("Sync Started for Groups. Please refresh shortly.")
            setTimeout(fetchData, 2000)
        } else {
            alert("Sync Failed")
        }
    }

    const handleCancelSync = async () => {
        const res = await fetch(`${API_BASE_URL}/api/data/sync/cancel`, { method: "POST" })
        if (res.ok) alert("Cancellation Requested.")
    }

    // Map parent_id to name for display
    const groupMap = new Map(data.map(g => [g.group_id, g.group_name]))
    const enrichedData = data.map(g => ({
        ...g,
        parent_name: groupMap.get(g.parent_id) || '-'
    }))

    // Unique Parents for Filter
    const uniqueParents = Array.from(new Set(enrichedData.map(g => g.parent_name))).filter(n => n !== '-').sort()

    const columns: ColumnDef<any>[] = [
        { header: "Group ID", accessorKey: "group_id", className: "font-medium" },
        { header: "Code (MISA)", accessorKey: "misa_code" },
        { header: "Group Name", accessorKey: "group_name" },
        { header: "Parent Group", accessorKey: "parent_name" },
        {
            header: "Last Updated",
            accessorKey: "updated_at",
            cell: (item) => item.updated_at ? new Date(item.updated_at).toLocaleDateString() : '-'
        }
    ]

    return (
        <StandardDataTable
            title="Product Groups"
            description="Classification groups for products."
            data={enrichedData}
            columns={columns}
            searchKey="group_name"
            filters={[
                {
                    key: "parent_name",
                    title: "Parent Group",
                    options: uniqueParents.map(p => ({ label: p, value: p }))
                }
            ]}
            loading={loading}
            onSync={handleSync}
            onCancelSync={handleCancelSync}
        />
    )
}
