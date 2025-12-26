"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"
import { Button } from "@/components/ui/button"
import { format } from "date-fns"
import { PeriodFilter, DateRange } from "@/components/PeriodFilter"

interface SaleRecord {
    transaction_id: string
    order_date: string
    sku_id: string
    product_name: string
    quantity: number
    amount: number
    source: string
    extra_data: string
}

export default function SalesPage() {
    const router = useRouter()
    const [data, setData] = useState<SaleRecord[]>([])
    const [loading, setLoading] = useState(true)
    const [totalCount, setTotalCount] = useState(0)
    const [page, setPage] = useState(1)
    const [search, setSearch] = useState("")

    // Default to this year
    const currentYear = new Date().getFullYear()
    const [dateRange, setDateRange] = useState<DateRange>({
        from: new Date(currentYear, 0, 1),
        to: new Date(currentYear, 11, 31)
    })

    const fetchData = async () => {
        setLoading(true)
        try {
            const limit = 20
            const skip = (page - 1) * limit

            const params = new URLSearchParams()
            params.append('skip', skip.toString())
            params.append('limit', limit.toString())
            if (search) params.append('search', search)
            if (dateRange.from) params.append('start_date', format(dateRange.from, 'yyyy-MM-dd'))
            if (dateRange.to) params.append('end_date', format(dateRange.to, 'yyyy-MM-dd'))

            const res = await fetch(`${API_BASE_URL}/api/data/sales?${params.toString()}`)
            if (res.ok) {
                const json = await res.json()
                setData(json.data)
                setTotalCount(json.total)
            }
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [page, search, dateRange])

    const handleImport = async (file: File) => {
        setLoading(true)
        try {
            const fd = new FormData()
            fd.append("file", file)
            const res = await fetch(`${API_BASE_URL}/api/data/import/upload?type=sales_details`, {
                method: "POST",
                body: fd
            })
            if (res.ok) {
                const json = await res.json()
                alert(`Upload Successful: ${json.message}`)
                fetchData() // Refresh
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

    const columns: ColumnDef<SaleRecord>[] = [
        { header: "Date", accessorKey: "order_date" },
        { header: "Tx ID", accessorKey: "transaction_id" },
        { header: "SKU", accessorKey: "sku_id", className: "font-medium" },
        { header: "Product", accessorKey: "product_name" },
        { header: "Qty", accessorKey: "quantity", className: "text-right" },
        {
            header: "Source",
            accessorKey: "source",
            cell: (item) => <span className="badge badge-sm">{item.source}</span>
        },
        {
            header: "Extra",
            accessorKey: "extra_data",
            cell: (item) => item.extra_data ? <span title={item.extra_data} className="text-xs text-muted-foreground truncate max-w-[150px] block">{item.extra_data}</span> : '-'
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

            <PeriodFilter onFilterChange={(r) => { setDateRange(r); setPage(1); }} />

            <StandardDataTable
                title="Sales Details (Chi tiết bán hàng)"
                description="Transaction history from 'So chi tiet ban hang'."
                data={data}
                columns={columns}
                searchKey="sku_id" // or product name support? StandardDataTable usually supports one?
                // Actually StandardDataTable usually uses searchKey for local filter or passing to onSearchChange.
                // We handle onSearchChange manually.

                loading={loading}
                mode="server"
                totalCount={totalCount}
                page={page}
                pageSize={20}
                onPaginationChange={setPage}
                onSearchChange={setSearch}
                onImport={handleImport}

                filters={[]}
            />
        </div>
    )
}
