"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { TrendingUp, RefreshCw, AlertCircle, Download, FileSpreadsheet } from "lucide-react"
import { API_BASE_URL } from "@/config"

interface Product {
    sku_id: string
    product_name: string
}

interface Group {
    group_id: string
    group_name: string
}

interface ForecastData {
    date: string
    actual: number | null
    forecast: number | null
}

export default function ForecastingPage() {
    const [scope, setScope] = useState<"product" | "group">("product")

    const [products, setProducts] = useState<Product[]>([])
    const [groups, setGroups] = useState<Group[]>([])

    const [selectedSku, setSelectedSku] = useState<string>("")
    const [selectedGroup, setSelectedGroup] = useState<string>("")

    const [model, setModel] = useState<string>("SMA")
    const [chartData, setChartData] = useState<ForecastData[]>([])
    const [loading, setLoading] = useState(false)
    const [running, setRunning] = useState(false)

    // Load products and groups on mount
    useEffect(() => {
        // Products
        fetch(`${API_BASE_URL}/api/data/products`)
            .then(res => res.json())
            .then((data: any) => {
                const list = Array.isArray(data) ? data : (data.data || [])
                setProducts(list)
                if (list.length > 0) setSelectedSku(list[0].sku_id)
            })
            .catch(err => console.error(err))

        // Groups
        fetch(`${API_BASE_URL}/api/data/groups`)
            .then(res => res.json())
            .then((data: any) => {
                setGroups(Array.isArray(data) ? data : [])
                if (Array.isArray(data) && data.length > 0) setSelectedGroup(data[0].group_id)
            })
            .catch(err => console.error(err))
    }, [])

    // Load chart data
    useEffect(() => {
        if (scope === 'product' && selectedSku) {
            fetchChartData()
        } else if (scope === 'group' && selectedGroup) {
            fetchChartData()
        }
    }, [selectedSku, selectedGroup, scope])

    const fetchChartData = async () => {
        setLoading(true)
        try {
            let url = `${API_BASE_URL}/api/planning/forecast/data?scope=${scope}`
            if (scope === 'product') url += `&sku_id=${selectedSku}`
            else url += `&group_id=${selectedGroup}`

            const res = await fetch(url)
            if (res.ok) {
                const data = await res.json()
                setChartData(data)
            }
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    const runForecast = async () => {
        setRunning(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/planning/forecast`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    scope: scope,
                    sku_id: scope === 'product' ? selectedSku : undefined,
                    group_id: scope === 'group' ? selectedGroup : undefined,
                    model: model,
                    periods: 30
                })
            })
            if (res.ok) {
                const result = await res.json()
                fetchChartData()
                alert(`Success! Avg predicted: ${result.avg_predicted_qty}`)
            } else {
                alert("Failed to generate forecast")
            }
        } catch (e) {
            alert("Network error")
        } finally {
            setRunning(false)
        }
    }

    const handleExport = () => {
        let url = `${API_BASE_URL}/api/planning/forecast/export?scope=${scope}`
        if (scope === 'product') url += `&sku_id=${selectedSku}`
        else url += `&group_id=${selectedGroup}`

        // Trigger download
        window.open(url, '_blank')
    }

    return (
        <div className="container py-8 space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-text-heading">Demand Forecasting</h1>
                    <p className="text-text-muted">Predict future inventory requirements using standard time-series models.</p>
                </div>

                <Button variant="outline" onClick={handleExport}>
                    <FileSpreadsheet className="mr-2 h-4 w-4 text-green-600" />
                    Export Analysis (Excel)
                </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-4">
                {/* Controls */}
                <Card className="col-span-1">
                    <CardHeader>
                        <CardTitle>Configuration</CardTitle>
                        <CardDescription>Select analysis level</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Analysis Scope</label>
                            <Tabs value={scope} onValueChange={(v) => setScope(v as any)} className="w-full">
                                <TabsList className="grid w-full grid-cols-2">
                                    <TabsTrigger value="product">Product</TabsTrigger>
                                    <TabsTrigger value="group">Group</TabsTrigger>
                                </TabsList>
                            </Tabs>
                        </div>

                        {scope === 'product' ? (
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Product</label>
                                <Select value={selectedSku} onValueChange={setSelectedSku}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select Product" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {products.map(p => (
                                            <SelectItem key={p.sku_id} value={p.sku_id}>{p.product_name} ({p.sku_id})</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Product Group</label>
                                <Select value={selectedGroup} onValueChange={setSelectedGroup}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select Group" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {groups.map(g => (
                                            <SelectItem key={g.group_id} value={g.group_id}>{g.group_name}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Model</label>
                            <Select value={model} onValueChange={setModel}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="SMA">Mức tiêu thụ bình quân (Average Selling)</SelectItem>
                                    <SelectItem value="EMA">Dự báo theo xu hướng (Trend Based)</SelectItem>
                                </SelectContent>
                            </Select>
                            <p className="text-xs text-text-muted">
                                {model === 'SMA' ? "Dựa trên trung bình bán hàng 7 ngày gần nhất." : "Dựa trên xu hướng tăng/giảm gần đây."}
                            </p>
                        </div>

                        <Button className="w-full" onClick={runForecast} disabled={running}>
                            {running ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <TrendingUp className="mr-2 h-4 w-4" />}
                            Run Forecast
                        </Button>
                    </CardContent>
                </Card>

                {/* Chart */}
                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>Forecast Visualization</CardTitle>
                        <CardDescription>
                            Historical Sales (Blue) vs Predicted Demand (Orange). Scope: <strong>{scope === 'product' ? 'Single Product' : 'Product Group'}</strong>.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="h-[400px]">
                        {loading ? (
                            <div className="flex items-center justify-center h-full">
                                <RefreshCw className="h-8 w-8 animate-spin text-primary" />
                            </div>
                        ) : chartData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" tick={{ fontSize: 12 }} tickFormatter={(val) => val.substring(5)} />
                                    <YAxis />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)' }}
                                    />
                                    <Legend />
                                    <Line type="monotone" dataKey="actual" name="Actual Sales" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
                                    <Line type="monotone" dataKey="forecast" name="Forecast" stroke="#f97316" strokeDasharray="5 5" strokeWidth={2} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full text-text-muted">
                                <AlertCircle className="h-8 w-8 mb-2" />
                                <p>No data available for this selection.</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Forecast Data Points</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Date</TableHead>
                                <TableHead className="text-right">Actual Qty</TableHead>
                                <TableHead className="text-right">Forecast Qty</TableHead>
                                <TableHead className="text-right">Status</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {/* Show last 10 historical + all forecast */}
                            {chartData.slice(-20).map((row, i) => (
                                <TableRow key={i}>
                                    <TableCell>{row.date}</TableCell>
                                    <TableCell className="text-right">{row.actual !== null ? row.actual.toLocaleString() : "-"}</TableCell>
                                    <TableCell className="text-right text-warning">{row.forecast !== null ? row.forecast.toLocaleString() : "-"}</TableCell>
                                    <TableCell className="text-right">
                                        {row.forecast !== null && row.actual === null ? (
                                            <span className="text-xs border px-2 py-0.5 rounded-full border-warning text-warning">Predicted</span>
                                        ) : (
                                            <span className="text-xs border px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground">History</span>
                                        )}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    )
}
