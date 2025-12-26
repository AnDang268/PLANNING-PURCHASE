```javascript
"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"
import { Button } from "@/components/ui/button"
import { format } from "date-fns"
import { PeriodFilter, DateRange } from "@/components/PeriodFilter"

interface RollingRecord {
    bucket_date: string
    sku_id: string
    product_name: string
    warehouse_id: string
    opening_stock: number
    closing_stock: number
    net_requirement: number
    actual_sold_qty: number
    actual_imported_qty: number
    forecast_demand: number
    status: string
}

export default function RollingDataPage() {
    const router = useRouter()
    const [data, setData] = useState<RollingRecord[]>([])
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

            const res = await fetch(`${ API_BASE_URL } /api/data / rolling - raw ? ${ params.toString() } `)
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

    const columns: ColumnDef<RollingRecord>[] = [
        { header: "Date", accessorKey: "bucket_date" },
        { header: "SKU", accessorKey: "sku_id", className: "font-medium" },
        { header: "Product", accessorKey: "product_name" },
        { header: "WH", accessorKey: "warehouse_id" },
        { header: "Open", accessorKey: "opening_stock", className: "text-right font-bold text-blue-600" },
        { header: "Sold (Act)", accessorKey: "actual_sold_qty", className: "text-right" },
        { header: "Imp (Act)", accessorKey: "actual_imported_qty", className: "text-right" },
        { header: "Forecast", accessorKey: "forecast_demand", className: "text-right text-gray-400" },
        { header: "Net Req", accessorKey: "net_requirement", className: "text-right text-red-600" },
        { header: "Close", accessorKey: "closing_stock", className: "text-right font-bold" },
        {
            header: "Status",
            accessorKey: "status",
            cell: (item) => <span className={`badge badge - sm ${ item.status === 'OK' ? 'badge-success' : 'badge-error' } `}>{item.status}</span>
        },
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
                title="Rolling Inventory Data (Dữ liệu Tính toán)"
                description="Raw calculation buckets from Fact_Rolling_Inventory."
                data={data}
                columns={columns}
                searchKey="sku_id"
                loading={loading}
                mode="server"
                totalCount={totalCount}
                page={page}
                pageSize={20}
                onPaginationChange={setPage}
                onSearchChange={setSearch}

                filters={[]}
                onImport={undefined} // No import here, this is a calculated table
            />
        </div>
    )
}
