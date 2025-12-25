"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
// import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend } from 'recharts'
import { Play, TrendingUp, AlertTriangle, ShieldCheck, Clock } from "lucide-react"
import { API_BASE_URL } from "@/config"

export default function SupplierPerformancePage() {
    const [ranking, setRanking] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [mocking, setMocking] = useState(false)

    const fetchRanking = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/vendors/performance/ranking`)
            const data = await res.json()
            setRanking(data)
        } catch (e) {
            console.error("Failed to fetch ranking", e)
        } finally {
            setLoading(false)
        }
    }

    const generateMock = async () => {
        setMocking(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/vendors/performance/generate-mock`, { method: "POST" })
            if (res.ok) {
                alert("Data Generated!")
                fetchRanking()
            }
        } catch (e) {
            alert("Error generating data")
        } finally {
            setMocking(false)
        }
    }

    useEffect(() => {
        fetchRanking()
    }, [])

    return (
        <div className="container py-8 space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-text-heading">Supplier 360°</h1>
                    <p className="text-text-muted">Performance evaluation based on Quality, Lead Time, and Reliability.</p>
                </div>
                <div className="flex gap-2">
                    <Button onClick={generateMock} disabled={mocking} variant="outline" className="border-warning text-warning hover:bg-warning/10">
                        {mocking ? "Generating..." : "Simulate Data (Demo)"}
                    </Button>
                    <Button onClick={fetchRanking} disabled={loading}>
                        Refresh
                    </Button>
                </div>
            </div>

            {/* KPI Overview (Avg of Top 5) */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Top Vendor Score</CardTitle>
                        <TrendingUp className="h-4 w-4 text-success" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{ranking.length > 0 ? ranking[0].score : "--"}</div>
                        <p className="text-xs text-text-muted">Best performer this month</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Avg Lead Time</CardTitle>
                        <Clock className="h-4 w-4 text-text-muted" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {ranking.length > 0
                                ? (ranking.reduce((acc, curr) => acc + curr.lead_time, 0) / ranking.length).toFixed(1)
                                : "--"} days
                        </div>
                        <p className="text-xs text-text-muted">Across all active vendors</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Quality Index</CardTitle>
                        <ShieldCheck className="h-4 w-4 text-info" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {ranking.length > 0
                                ? (ranking.reduce((acc, curr) => acc + curr.quality, 0) / ranking.length).toFixed(1)
                                : "--"}%
                        </div>
                        <p className="text-xs text-text-muted">Average pass rate</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Reliability Risk</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-danger" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {ranking.length > 0
                                ? ((ranking.reduce((acc, curr) => acc + curr.delay_rate, 0) / ranking.length) * 100).toFixed(1)
                                : "--"}%
                        </div>
                        <p className="text-xs text-text-muted">Average delay probability</p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-7">
                {/* Ranking Table */}
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>Vendor Ranking</CardTitle>
                        <CardDescription>
                            Composite score based on Quality (60%) and Reliability (40%).
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Rank</TableHead>
                                    <TableHead>Vendor</TableHead>
                                    <TableHead className="text-right">Score</TableHead>
                                    <TableHead className="text-right">Quality</TableHead>
                                    <TableHead className="text-right">Lead Time</TableHead>
                                    <TableHead className="text-right">Delay Rate</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {ranking.map((vendor, index) => (
                                    <TableRow key={vendor.vendor_id}>
                                        <TableCell className="font-medium">#{index + 1}</TableCell>
                                        <TableCell>{vendor.vendor_name}</TableCell>
                                        <TableCell className="text-right">
                                            <span className={`text-xs border px-2 py-0.5 rounded-full ${vendor.score >= 90 ? "bg-primary text-primary-foreground" : vendor.score >= 70 ? "bg-secondary text-secondary-foreground" : "bg-destructive text-destructive-foreground"}`}>
                                                {vendor.score}
                                            </span>
                                        </TableCell>
                                        <TableCell className="text-right">{vendor.quality}%</TableCell>
                                        <TableCell className="text-right">{vendor.lead_time}d</TableCell>
                                        <TableCell className="text-right">{(vendor.delay_rate * 100).toFixed(0)}%</TableCell>
                                    </TableRow>
                                ))}
                                {ranking.length === 0 && !loading && (
                                    <TableRow>
                                        <TableCell colSpan={6} className="text-center h-24 text-text-muted">
                                            No performance data found. Click "Simulate Data" to generate.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>

                {/* Performance Chart */}
                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>Top 5 Performance Breakdown</CardTitle>
                        <CardDescription>Quality vs. Reliability Comparison</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[350px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={ranking.slice(0, 5)} layout="vertical" margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" domain={[0, 100]} />
                                <YAxis dataKey="vendor_name" type="category" width={100} tick={{ fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)' }}
                                    itemStyle={{ color: 'var(--foreground)' }}
                                />
                                <Legend />
                                <Bar dataKey="quality" name="Quality Score" fill="#10b981" radius={[0, 4, 4, 0]} barSize={20} />
                                <Bar dataKey="score" name="Composite Score" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
