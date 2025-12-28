"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Search, RefreshCw, Upload, FileDown, Calendar } from "lucide-react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { API_BASE_URL } from "@/config"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { format, getISOWeek, isValid, parseISO } from "date-fns"

interface PurchaseRecord {
    transaction_id: string
    order_date: string
    sku_id: string
    product_name: string
    quantity: number
    purchase_type: string
    order_id: string
    source: string
    extra_data: string
}

interface ProductGroup {
    group_id: string
    group_name: string
}

export default function PurchasesPage() {
    const router = useRouter()
    const [data, setData] = useState<PurchaseRecord[]>([])
    const [loading, setLoading] = useState(true)
    const [totalCount, setTotalCount] = useState(0)
    const [page, setPage] = useState(1)

    // Filters
    const [search, setSearch] = useState("")
    const [monthFilter, setMonthFilter] = useState<string>("") // e.g., "2025-11"
    const [groupFilter, setGroupFilter] = useState("ALL")
    const [typeFilter, setTypeFilter] = useState("ALL")

    // Filter Options
    const [groups, setGroups] = useState<ProductGroup[]>([])

    // Load Filters
    useEffect(() => {
        const fetchFilters = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/data/groups`)
                if (res.ok) setGroups(await res.json())
            } catch (e) {
                console.error("Failed to load filters", e)
            }
        }
        fetchFilters()
    }, [])

    const fetchData = async () => {
        setLoading(true)
        try {
            const limit = 20
            const skip = (page - 1) * limit

            const params = new URLSearchParams()
            params.append('skip', skip.toString())
            params.append('limit', limit.toString())

            if (search) params.append('search', search)
            if (typeFilter && typeFilter !== 'ALL') params.append('type', typeFilter)
            if (groupFilter && groupFilter !== 'ALL') params.append('group_id', groupFilter)

            if (monthFilter) {
                const d = new Date(monthFilter)
                if (isValid(d)) {
                    const y = d.getFullYear()
                    const m = d.getMonth()
                    // Set range to full month
                    const start = new Date(y, m, 1)
                    const end = new Date(y, m + 1, 0)
                    params.append('start_date', format(start, 'yyyy-MM-dd'))
                    params.append('end_date', format(end, 'yyyy-MM-dd'))
                }
            }

            const res = await fetch(`${API_BASE_URL}/api/data/purchases?${params.toString()}`)
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
        setPage(1)
        fetchData()
    }, [search, monthFilter, groupFilter, typeFilter])

    useEffect(() => {
        fetchData()
    }, [page])

    const handleImport = async (file: File) => {
        setLoading(true)
        try {
            const fd = new FormData()
            fd.append("file", file)
            const res = await fetch(`${API_BASE_URL}/api/data/import/upload?type=purchase_details`, {
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

    const columns: ColumnDef<PurchaseRecord>[] = [
        {
            header: "Week",
            accessorKey: "order_date",
            cell: (item) => {
                if (!item.order_date) return "-"
                const date = parseISO(item.order_date)
                return isValid(date) ? `W${getISOWeek(date)}` : "-"
            }
        },
        { header: "Date", accessorKey: "order_date" },
        { header: "Tx ID", accessorKey: "transaction_id" },
        { header: "SKU", accessorKey: "sku_id", className: "font-medium" },
        { header: "Product", accessorKey: "product_name" },
        {
            header: "Type",
            accessorKey: "purchase_type",
            cell: (item) => (
                <span className={item.purchase_type === 'ACTUAL' ? "text-green-600 font-bold" : "text-blue-600"}>
                    {item.purchase_type}
                </span>
            )
        },
        { header: "Qty", accessorKey: "quantity", className: "text-right" },
        { header: "Doc No", accessorKey: "order_id" },
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
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Purchase Details</h2>
                    <p className="text-muted-foreground">
                        Manage Actual vs Planned Purchases.
                    </p>
                </div>
                <div className="flex items-center space-x-2">
                    <Input
                        id="purchase-import-file"
                        type="file"
                        className="hidden"
                        accept=".xlsx, .xls, .csv"
                        onChange={(e) => {
                            if (e.target.files?.[0]) handleImport(e.target.files[0])
                        }}
                    />
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => document.getElementById('purchase-import-file')?.click()}
                    >
                        <Upload className="mr-2 h-4 w-4" />
                        Import
                    </Button>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="w-full sm:w-[250px]">
                    <div className="relative">
                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search Tx, SKU, Doc..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="pl-8"
                        />
                    </div>
                </div>

                <Select value={groupFilter} onValueChange={setGroupFilter}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Product Group" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="ALL">All Groups</SelectItem>
                        {groups.map(g => (
                            <SelectItem key={g.group_id} value={g.group_id}>{g.group_name}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>

                <Select value={typeFilter} onValueChange={setTypeFilter}>
                    <SelectTrigger className="w-[150px]">
                        <SelectValue placeholder="Type" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="ALL">All Types</SelectItem>
                        <SelectItem value="ACTUAL">ACTUAL</SelectItem>
                        <SelectItem value="PLANNED">PLANNED</SelectItem>
                    </SelectContent>
                </Select>

                <div className="flex-1"></div>

                <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">Month:</span>
                    <Input
                        type="month"
                        value={monthFilter}
                        className="w-[180px]"
                        onChange={(e) => setMonthFilter(e.target.value)}
                    />
                </div>
            </div>

            <StandardDataTable
                title="Purchase Records"
                description=""
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
                onImport={async (f) => { }} // Handle manually above to customize
                filters={[]}
            />
        </div>
    )
}
