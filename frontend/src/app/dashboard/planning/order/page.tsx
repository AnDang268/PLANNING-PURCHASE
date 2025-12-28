"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "@/config";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Loader2, Download, Search, RefreshCw } from "lucide-react";
import * as XLSX from "xlsx";

interface OrderPlanRow {
    sku_id: string;
    product_name: string;
    current_stock: number;
    stock_on_order: number;
    safety_stock: number;
    lead_time_days: number;
    avg_sales: number;
    forecast_month_1: number;
    forecast_month_2: number;
    forecast_month_3: number;
    suggested_order: number;
    notes: string;
}

export default function OrderPlanningPage() {
    const [data, setData] = useState<OrderPlanRow[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE_URL}/api/planning/order-plan`);
            setData(res.data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleExport = () => {
        const ws = XLSX.utils.json_to_sheet(data);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Order Plan");
        XLSX.writeFile(wb, "Order_Plan.xlsx");
    };

    const filteredData = data.filter(r =>
        r.sku_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.product_name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="container mx-auto p-4 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold tracking-tight">Order Planning</h1>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={handleExport}>
                        <Download className="mr-2 h-4 w-4" /> Export
                    </Button>
                    <Button onClick={fetchData} disabled={loading}>
                        {loading ? <Loader2 className="animate-spin mr-2 h-4 w-4" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                        Refresh
                    </Button>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Suggested Orders</CardTitle>
                    <CardDescription>Generated based on Forecast, Safety Stock Policy, and Lead Time.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex items-center gap-2">
                        <Search className="h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search SKU or Product Name..."
                            value={searchTerm}
                            onChange={e => setSearchTerm(e.target.value)}
                            className="max-w-sm"
                        />
                    </div>

                    <div className="border rounded-md">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>SKU</TableHead>
                                    <TableHead>Product Name</TableHead>
                                    <TableHead className="text-right">Current Stock</TableHead>
                                    <TableHead className="text-right">On Order</TableHead>
                                    <TableHead className="text-right">Safety Stock</TableHead>
                                    <TableHead className="text-right">Forecast (M1)</TableHead>
                                    <TableHead className="text-right">Forecast (M2)</TableHead>
                                    <TableHead className="text-right font-bold text-blue-600">Suggested</TableHead>
                                    <TableHead>Notes</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loading ? (
                                    <TableRow>
                                        <TableCell colSpan={9} className="text-center py-8">Loading...</TableCell>
                                    </TableRow>
                                ) : filteredData.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">No records found.</TableCell>
                                    </TableRow>
                                ) : (
                                    filteredData.map(row => (
                                        <TableRow key={row.sku_id}>
                                            <TableCell className="font-medium">{row.sku_id}</TableCell>
                                            <TableCell>{row.product_name}</TableCell>
                                            <TableCell className="text-right">{row.current_stock.toLocaleString()}</TableCell>
                                            <TableCell className="text-right">{row.stock_on_order.toLocaleString()}</TableCell>
                                            <TableCell className="text-right">{row.safety_stock.toLocaleString()}</TableCell>
                                            <TableCell className="text-right">{row.forecast_month_1.toLocaleString()}</TableCell>
                                            <TableCell className="text-right">{row.forecast_month_2.toLocaleString()}</TableCell>
                                            <TableCell className="text-right font-bold text-blue-600">
                                                {row.suggested_order > 0 ? row.suggested_order.toLocaleString() : "-"}
                                            </TableCell>
                                            <TableCell className="text-xs text-gray-500">{row.notes}</TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
