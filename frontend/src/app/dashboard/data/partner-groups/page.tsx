"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"
import { Button } from "@/components/ui/button"
import { downloadCSV } from "@/lib/exportUtils"

interface CustomerGroup {
    group_id: string
    group_name: string
    updated_at: string
}

export default function PartnerGroupsPage() {
    const router = useRouter()
    const [data, setData] = useState<CustomerGroup[]>([])
    const [loading, setLoading] = useState(true)

    const fetchData = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/partner-groups`)
            if (res.ok) setData(await res.json())
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    useEffect(() => { fetchData() }, [])

    const handleSync = async () => {
        setLoading(true)
        try {
            // Re-use SYNC PARTNERS logic as it pulls Groups implicitly
            const res = await fetch(`${API_BASE_URL}/api/data/sync/partners`, { method: "POST" })
            if (res.ok) {
                alert("Sync Started (Syncing Partners will update Groups)")
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
        const headers = ["group_id", "group_name", "updated_at"]
        const csvContent = [
            headers.join(","),
            ...data.map(item => [
                `"${item.group_id}"`,
                `"${item.group_name}"`,
                `"${item.updated_at || ''}"`
            ].join(","))
        ].join("\n")
        downloadCSV(csvContent, "partner_groups_export")
    }

    const handleImport = async (file: File) => {
        setLoading(true)
        try {
            const formData = new FormData()
            formData.append("file", file)
            const res = await fetch(`${API_BASE_URL}/api/data/import/upload?type=partner-groups`, {
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

    const columns: ColumnDef<CustomerGroup>[] = [
        { header: "Group ID", accessorKey: "group_id", className: "font-medium" },
        { header: "Group Name", accessorKey: "group_name" },
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
                title="Partner Groups (Subject Groups)"
                description="Manage Vendor/Customer Groups (Synced from MISA)."
                data={data}
                columns={columns}
                searchKey="group_name"
                loading={loading}
                onSync={handleSync}
                onExport={handleExport}
                onImport={handleImport}
            // Read-only from MISA primarily, so we can disable manual Add/Edit for now or leave generic
            // onAdd={() => alert("Managed by MISA")}
            />
        </div>
    )
}
