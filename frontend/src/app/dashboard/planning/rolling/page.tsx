
"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { API_BASE_URL } from "@/config";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Loader2, Download, Play, Save } from "lucide-react";
import { format } from "date-fns";
import * as XLSX from 'xlsx';

// Types
interface RollingRecord {
    sku_id: string;
    product_name: string;
    category: string;
    bucket_date: string;
    opening_stock: number;
    forecast: number;
    incoming: number;
    planned: number;
    closing: number;
    status: string;
    net_req: number;
    dos: number;
}

interface PlanningProfile {
    profile_id: string;
    profile_name: string;
    description: string;
}

interface MatrixRow {
    sku_id: string;
    product_name: string;
    category: string;
    weeks: {
        [date: string]: RollingRecord;
    }
}

export default function RollingPlanningPage() {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<MatrixRow[]>([]);
    const [uniqueDates, setUniqueDates] = useState<string[]>([]);
    const [calculating, setCalculating] = useState(false);

    // Profile State
    const [profiles, setProfiles] = useState<PlanningProfile[]>([]);
    const [selectedProfile, setSelectedProfile] = useState<string>("STD");

    useEffect(() => {
        fetchData();
        fetchProfiles();
    }, []);

    const fetchProfiles = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/planning/rolling/profiles`);
            if (res.data && res.data.length > 0) {
                setProfiles(res.data);
                setSelectedProfile(res.data[0].profile_id);
            }
        } catch (e) {
            console.error("Failed to fetch profiles", e);
        }
    };

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE_URL}/api/planning/rolling/matrix`);
            processData(res.data);
        } catch (error) {
            console.error("Failed to fetch matrix", error);
        } finally {
            setLoading(false);
        }
    };

    const processData = (rawData: RollingRecord[]) => {
        // 1. Get Unique Dates for Columns
        const dates = Array.from(new Set(rawData.map(r => r.bucket_date))).sort();
        setUniqueDates(dates);

        // 2. Group by Product
        const grouped: { [sku: string]: MatrixRow } = {};

        rawData.forEach(r => {
            if (!grouped[r.sku_id]) {
                grouped[r.sku_id] = {
                    sku_id: r.sku_id,
                    product_name: r.product_name,
                    category: r.category,
                    weeks: {}
                };
            }
            grouped[r.sku_id].weeks[r.bucket_date] = r;
        });

        setData(Object.values(grouped));
    };

    const handleRunCalculation = async () => {
        setCalculating(true);
        try {
            await axios.post(`${API_BASE_URL}/api/planning/rolling/run`, {
                horizon_months: 12,
                profile_id: selectedProfile
            });
            await fetchData(); // Refresh
            alert(`Calculation Complete (Mode: ${selectedProfile})!`);
        } catch (error) {
            console.error("Run failed", error);
            alert("Failed to run calculation.");
        } finally {
            setCalculating(false);
        }
    };

    const handleExportExcel = () => {
        // Flatten for Excel
        const exportData: any[] = [];

        // Header Row
        // ... Simplified Logic ...
        data.forEach(row => {
            const xlRow: any = {
                "SKU": row.sku_id,
                "Product": row.product_name,
                "Category": row.category
            };
            uniqueDates.forEach(d => {
                const cell = row.weeks[d];
                if (cell) {
                    xlRow[`${d} Close`] = cell.closing;
                    xlRow[`${d} Plan`] = cell.planned;
                    if (cell.net_req > 0) xlRow[`${d} NetReq`] = cell.net_req;
                }
            });
            exportData.push(xlRow);
        });

        const ws = XLSX.utils.json_to_sheet(exportData);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "RollingPlan");
        XLSX.writeFile(wb, "Supply_Plan_Rolling.xlsx");
    };

    return (
        <div className="container mx-auto p-4 space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Rolling Supply Planning</h1>
                    <p className="text-muted-foreground">Master Plan & Order Generation (Week 1 - 52)</p>
                </div>
                <div className="flex space-x-2 items-center">
                    <div className="w-[280px]">
                        <Select value={selectedProfile} onValueChange={setSelectedProfile}>
                            <SelectTrigger>
                                <SelectValue placeholder="Select Analysis Mode" />
                            </SelectTrigger>
                            <SelectContent>
                                {profiles.map(p => (
                                    <SelectItem key={p.profile_id} value={p.profile_id} title={p.description}>
                                        <span className="font-semibold">{p.profile_name}</span>
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    <Button onClick={handleRunCalculation} disabled={calculating}>
                        {calculating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                        Run Calculation
                    </Button>
                    <Button variant="outline" onClick={handleExportExcel}>
                        <Download className="mr-2 h-4 w-4" />
                        Export PO Excel
                    </Button>
                </div>
            </div>

            <Card className="overflow-hidden">
                <CardHeader className="bg-muted/50 pb-4">
                    <CardTitle>Supply Matrix Worksheet</CardTitle>
                    <CardDescription>Review projected inventory and adjust planned orders.</CardDescription>
                </CardHeader>
                <div className="overflow-x-auto">
                    <Table className="border-collapse">
                        <TableHeader>
                            <TableRow>
                                <TableHead className="w-[100px] sticky left-0 bg-background z-10 border-r">SKU</TableHead>
                                <TableHead className="w-[200px] sticky left-[100px] bg-background z-10 border-r">Product</TableHead>
                                {uniqueDates.map(d => (
                                    <TableHead key={d} className="text-center min-w-[120px] border-l">
                                        {format(new Date(d), 'dd/MM')} <br />
                                        <span className="text-xs text-muted-foreground font-normal">Week</span>
                                    </TableHead>
                                ))}
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={uniqueDates.length + 2} className="text-center h-24">
                                        <Loader2 className="h-8 w-8 animate-spin mx-auto" />
                                    </TableCell>
                                </TableRow>
                            ) : (data.map(row => (
                                <TableRow key={row.sku_id}>
                                    <TableCell className="font-medium sticky left-0 bg-background z-10 border-r">{row.sku_id}</TableCell>
                                    <TableCell className="sticky left-[100px] bg-background z-10 border-r truncate max-w-[200px]" title={row.product_name}>{row.product_name}</TableCell>
                                    {uniqueDates.map(d => {
                                        const cell = row.weeks[d];
                                        if (!cell) return <TableCell key={d} className="border-l bg-gray-50">-</TableCell>;

                                        // Color Logic
                                        let bgClass = "";
                                        if (cell.status === 'CRITICAL') bgClass = "bg-red-100 text-red-700 font-bold";
                                        else if (cell.status === 'LOW') bgClass = "bg-yellow-50 text-yellow-700";
                                        else if (cell.status === 'OVERSTOCK') bgClass = "bg-blue-50 text-blue-700";

                                        return (
                                            <TableCell key={d} className={`text-center border-l text-xs p-1 ${bgClass}`}>
                                                <div className="flex flex-col gap-1">
                                                    <div title="Closing Stock">C: {Math.round(cell.closing)}</div>
                                                    {cell.net_req > 0 && (
                                                        <div className="text-red-600 font-bold border border-red-200 bg-white rounded px-1">
                                                            Buy: {Math.round(cell.net_req)}
                                                        </div>
                                                    )}
                                                    <div className="text-[10px] text-gray-400">Fc: {Math.round(cell.forecast)}</div>
                                                </div>
                                            </TableCell>
                                        )
                                    })}
                                </TableRow>
                            )))}
                        </TableBody>
                    </Table>
                </div>
            </Card>
        </div>
    );
}
