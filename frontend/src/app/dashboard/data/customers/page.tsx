"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"
import { Button } from "@/components/ui/button"
import { downloadCSV } from "@/lib/exportUtils"

interface Customer {
    customer_id: string
    customer_name: string
    address: string
    phone: string
    email: string
    misa_code: string
    updated_at: string
}

export default function CustomersPage() {
    const router = useRouter()
    const [data, setData] = useState<Customer[]>([])
    const [loading, setLoading] = useState(true)

    const fetchData = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/customers`)
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
        const headers = ["customer_id", "misa_code", "customer_name", "address", "phone", "email", "updated_at"]
        const csvContent = [
            headers.join(","),
            ...data.map(item => [
                `"${item.customer_id}"`,
                `"${item.misa_code || ''}"`,
                `"${item.customer_name}"`,
                `"${item.address || ''}"`,
                `"${item.phone || ''}"`,
                `"${item.email || ''}"`,
                `"${item.updated_at || ''}"`
            ].join(","))
        ].join("\n")
        downloadCSV(csvContent, "customers_export")
    }

    const handleImport = async (file: File) => {
        setLoading(true)
        try {
            const formData = new FormData()
            formData.append("file", file)
            const res = await fetch(`${API_BASE_URL}/api/data/import/upload?type=customers`, {
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

    const columns: ColumnDef<Customer>[] = [
        { header: "Customer ID", accessorKey: "customer_id", className: "font-medium" },
        { header: "MISA Code", accessorKey: "misa_code" },
        { header: "Customer Name", accessorKey: "customer_name" },
        { header: "Address", accessorKey: "address", className: "hidden md:table-cell" },
        { header: "Phone", accessorKey: "phone" },
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
                title="Customers (Khách hàng)"
                description="View MISA Customers."
                data={data}
                columns={columns}
                searchKey="customer_name"
                loading={loading}
                onSync={handleSync}
                onExport={handleExport}
                onImport={handleImport}
            // Read-only from MISA primarily
            // onAdd={() => alert("Managed by MISA")}
            />
        </div>
    )
}
