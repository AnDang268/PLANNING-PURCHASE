
"use client";
import Link from 'next/link';

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
import { Download, Upload, Play, Save, Loader2, ChevronDown, ChevronRight, Settings } from 'lucide-react';
import { format, parseISO, startOfMonth, endOfMonth, isSameMonth } from "date-fns";
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

const safeFormat = (dateStr: string, fmt: string) => {
    try {
        if (!dateStr) return "-";
        return format(parseISO(dateStr), fmt);
    } catch (e) {
        return dateStr;
    }
};

interface MonthlyAggregate {
    planned: number;
    closing: number;
    forecast: number;
    incoming: number;
    net_req: number;
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
    group_name?: string;
    weeks: {
        [date: string]: RollingRecord;
    }
    months: { [month: string]: MonthlyAggregate };
}

export default function RollingPlanningPage() {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<MatrixRow[]>([]);
    const [uniqueDates, setUniqueDates] = useState<string[]>([]);
    const [uniqueMonths, setUniqueMonths] = useState<string[]>([]); // YYYY-MM
    const [collapsedMonths, setCollapsedMonths] = useState<Set<string>>(new Set());
    const [calculating, setCalculating] = useState(false);

    // Edits: key = "sku|date", value = number
    const [edits, setEdits] = useState<{ [key: string]: number }>({});
    const [saving, setSaving] = useState(false);

    // Filters
    const [groups, setGroups] = useState<any[]>([]);
    const [selectedGroup, setSelectedGroup] = useState<string>("ALL");

    // New Warehouse Filter
    const [warehouses, setWarehouses] = useState<any[]>([]);
    const [selectedWarehouse, setSelectedWarehouse] = useState<string>("ALL");

    // Profile State
    const [profiles, setProfiles] = useState<PlanningProfile[]>([]);
    const [selectedProfile, setSelectedProfile] = useState<string>("STD");

    useEffect(() => {
        fetchData();
        fetchProfiles();
        fetchWarehouses();
    }, []);

    const fetchWarehouses = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/data/warehouses`)
            if (Array.isArray(res.data)) setWarehouses(res.data)
            else console.warn("Warehouses API did not return array", res.data)
        } catch (e) { console.error(e) }
    }

    const fetchProfiles = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/planning/rolling/profiles`);
            if (res.data && Array.isArray(res.data)) {
                setProfiles(res.data);
            } else {
                setProfiles([]);
            }

            // Fetch Groups for Filter
            const gRes = await axios.get(`${API_BASE_URL}/api/data/groups`);
            if (gRes.data && Array.isArray(gRes.data)) {
                setGroups(gRes.data);
            } else {
                setGroups([]);
            }
        } catch (e) {
            console.error("Failed to fetch initial data", e);
        }
    };

    const fetchData = async () => {
        setLoading(true);
        try {
            let url = `${API_BASE_URL}/api/planning/rolling/matrix?limit=5000`;
            if (selectedGroup && selectedGroup !== 'ALL') url += `&group_id=${selectedGroup}`;
            if (selectedWarehouse && selectedWarehouse !== 'ALL') url += `&warehouse_id=${selectedWarehouse}`;

            const res = await axios.get(url);
            processData(res.data);
        } catch (error) {
            console.error("Failed to fetch matrix", error);
        } finally {
            setLoading(false);
        }
    };

    // Filter Listeners
    useEffect(() => {
        fetchData()
    }, [selectedGroup, selectedWarehouse])

    const processData = (rawData: RollingRecord[]) => {
        if (!Array.isArray(rawData)) {
            console.error("Invalid data format", rawData);
            return;
        }

        // 1. Get Unique Dates and Months
        const validDates = rawData
            .map(r => r.bucket_date)
            .filter(d => {
                if (!d) return false;
                // Simple regex check YYYY-MM-DD, allowing for time component
                return /^\d{4}-\d{2}-\d{2}/.test(d);
            });

        const dates = Array.from(new Set(validDates)).sort();
        setUniqueDates(dates);

        const months = Array.from(new Set(dates.map(d => d.substring(0, 7)))).sort(); // YYYY-MM
        setUniqueMonths(months);

        // Default: Collapse ALL months to show Yearly Summary initially (Cleaner look)
        setCollapsedMonths(new Set(months));

        // 2. Group by Product
        const grouped: { [sku: string]: MatrixRow } = {};

        rawData.forEach(r => {
            // Skip invalid date records
            if (!r.bucket_date || !/^\d{4}-\d{2}-\d{2}/.test(r.bucket_date)) return;

            if (!grouped[r.sku_id]) {
                grouped[r.sku_id] = {
                    sku_id: r.sku_id,
                    product_name: r.product_name,
                    category: r.category,
                    group_name: r.category,
                    weeks: {},
                    months: {}
                };
            }
            grouped[r.sku_id].weeks[r.bucket_date] = r;
        });

        // 3. Compute Monthly Aggregates
        Object.values(grouped).forEach(row => {
            months.forEach(m => {
                const mWeeks = dates.filter(d => d.startsWith(m));
                if (mWeeks.length === 0) return;

                let sumPlanned = 0;
                let sumForecast = 0;
                let sumIncoming = 0;
                let sumNetReq = 0;

                // Closing stock is the closing of the LAST week of the month
                const lastWeekDate = mWeeks[mWeeks.length - 1];
                const lastWeekRec = row.weeks[lastWeekDate];
                const closing = lastWeekRec ? lastWeekRec.closing : 0;

                mWeeks.forEach(d => {
                    const rec = row.weeks[d];
                    if (rec) {
                        sumPlanned += rec.planned;
                        sumForecast += rec.forecast;
                        sumIncoming += rec.incoming;
                        sumNetReq += rec.net_req;
                    }
                });

                row.months[m] = {
                    planned: sumPlanned,
                    forecast: sumForecast,
                    incoming: sumIncoming,
                    net_req: sumNetReq,
                    closing: closing
                };
            });
        });

        setData(Object.values(grouped));
    };

    const toggleMonth = (month: string) => {
        const newSet = new Set(collapsedMonths);
        if (newSet.has(month)) newSet.delete(month);
        else newSet.add(month);
        setCollapsedMonths(newSet);
    };

    const handleEdit = (sku_id: string, bucket_date: string, valStr: string) => {
        const val = parseFloat(valStr);
        if (isNaN(val)) return;

        setEdits(prev => ({
            ...prev,
            [`${sku_id}|${bucket_date}`]: val
        }));
    };

    const saveChanges = async () => {
        if (Object.keys(edits).length === 0) return;
        setSaving(true);
        try {
            const updates = Object.entries(edits).map(([key, val]) => {
                const [sku_id, bucket_date] = key.split('|');
                return {
                    sku_id,
                    warehouse_id: selectedWarehouse === 'ALL' ? 'ALL' : selectedWarehouse, // Caution: If ALL, assuming global update or default 'ALL' WH
                    bucket_date,
                    planned_supply: val
                };
            });

            const res = await axios.post(`${API_BASE_URL}/api/planning/rolling/update`, updates);
            if (res.data.status === 'success') {
                alert(`Saved ${res.data.updated} changes!`);
                setEdits({});
                fetchData(); // Refresh
            }
        } catch (e: any) {
            console.error("Save failed", e);
            alert("Failed to save changes: " + (e.response?.data?.detail || e.message));
        } finally {
            setSaving(false);
        }
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

    const handleImportOpenStock = async (file: File) => {
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append("file", file);
            const res = await axios.post(`${API_BASE_URL}/api/data/import/upload?type=opening_stock`, formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            if (res.status === 200) {
                alert(res.data.message);
                fetchData();
            }
        } catch (e: any) {
            console.error(e);
            alert(e.response?.data?.detail || "Import Failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto p-4 space-y-8">
            <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-6">
                <div className="space-y-1">
                    <div className="flex items-center gap-2">
                        <h1 className="text-3xl font-bold tracking-tight text-foreground">Rolling Supply Planning</h1>
                        <Link href="/dashboard/planning/settings">
                            <Button variant="ghost" size="icon" title="Configure Policies">
                                <Settings className="h-5 w-5 text-gray-500 hover:text-primary" />
                            </Button>
                        </Link>
                    </div>
                    <p className="text-muted-foreground text-sm max-w-lg">
                        Master Schedule for Procurement & Production.
                        <br />
                        Analyzing Week 1 - 52 based on Forecast, Stock & Lead Time.
                    </p>
                </div>

                <div className="flex flex-col gap-4 w-full md:w-auto">
                    <div className="flex flex-wrap gap-2 justify-end">
                        <div className="w-[240px]">
                            <Select value={selectedProfile} onValueChange={setSelectedProfile}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select Analysis Mode" />
                                </SelectTrigger>
                                <SelectContent className="bg-white">
                                    {profiles.map(p => (
                                        <SelectItem key={p.profile_id} value={p.profile_id} title={p.description}>
                                            <span className="font-semibold">{p.profile_name}</span>
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="flex gap-2">
                            <Button onClick={handleRunCalculation} disabled={calculating} className="bg-primary hover:bg-primary/90">
                                {calculating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                                Run Calculation
                            </Button>
                            {Object.keys(edits).length > 0 && (
                                <Button onClick={saveChanges} disabled={saving} variant="destructive">
                                    {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                                    Save ({Object.keys(edits).length})
                                </Button>
                            )}
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-2 justify-end items-center">
                        <div className="w-[180px]">
                            <Select value={selectedGroup} onValueChange={setSelectedGroup}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Filter by Group" />
                                </SelectTrigger>
                                <SelectContent className="bg-white">
                                    <SelectItem value="ALL">All Groups</SelectItem>
                                    {groups.map((g: any) => (
                                        <SelectItem key={g.group_id} value={g.group_id}>{g.group_name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="w-[180px]">
                            <Select value={selectedWarehouse} onValueChange={setSelectedWarehouse}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Filter by Warehouse" />
                                </SelectTrigger>
                                <SelectContent className="bg-white">
                                    <SelectItem value="ALL">All Warehouses</SelectItem>
                                    {warehouses.map((w: any) => (
                                        <SelectItem key={w.warehouse_id} value={w.warehouse_id}>{w.warehouse_name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <Button variant="outline" size="icon" title="Import Opening Stock" onClick={() => document.getElementById('openStockInput')?.click()}>
                            <Upload className="h-4 w-4" />
                        </Button>

                        <Button variant="outline" size="icon" title="Export Excel" onClick={handleExportExcel}>
                            <Download className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </div>

            <input
                id="openStockInput"
                type="file"
                className="hidden"
                accept=".xlsx,.xls,.csv"
                onChange={(e) => {
                    if (e.target.files?.[0]) handleImportOpenStock(e.target.files[0]);
                    e.target.value = '';
                }}
            />

            <Card className="overflow-hidden">
                <CardHeader className="bg-muted/50 pb-4">
                    <CardTitle>Supply Matrix Worksheet</CardTitle>
                    <CardDescription>Review projected inventory and adjust planned orders.</CardDescription>
                </CardHeader>
                <div className="overflow-x-auto">
                    <Table className="border-collapse">
                        <TableHeader>
                            <TableRow>
                                <TableHead rowSpan={2} className="w-[100px] sticky left-0 bg-background z-20 border-r text-center align-middle h-auto">SKU</TableHead>
                                <TableHead rowSpan={2} className="w-[200px] sticky left-[100px] bg-background z-20 border-r text-center align-middle h-auto">Product</TableHead>
                                {uniqueMonths.map(m => {
                                    const mWeeks = uniqueDates.filter(d => d.startsWith(m));
                                    const isCollapsed = collapsedMonths.has(m);

                                    // If collapsed: colSpan=1. Else: colSpan=weeks.length
                                    const colSpan = isCollapsed ? 1 : mWeeks.length;

                                    return (
                                        <TableHead key={m} colSpan={colSpan} className={`text-center border-l border-r ${isCollapsed ? 'bg-orange-100 font-bold' : 'bg-muted/20'}`}>
                                            <div className="flex items-center justify-center gap-2 cursor-pointer select-none" onClick={() => toggleMonth(m)}>
                                                {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                                                {safeFormat(m + "-01", "MMMM yyyy")}
                                                {isCollapsed && <span className="text-xs text-muted-foreground ml-1">(Summary)</span>}
                                            </div>
                                        </TableHead>
                                    );
                                })}
                            </TableRow>
                            <TableRow>
                                {uniqueMonths.flatMap(m => {
                                    const isCollapsed = collapsedMonths.has(m);
                                    if (isCollapsed) {
                                        // Render ONE sub-header for summary
                                        return [
                                            <TableHead key={`${m}-sum`} className="text-center min-w-[80px] border-l h-auto py-1 bg-orange-50">
                                                <div className="text-xs font-bold text-orange-700">Total</div>
                                            </TableHead>
                                        ];
                                    } else {
                                        // Render Weekly Headers
                                        const mWeeks = uniqueDates.filter(d => d.startsWith(m));
                                        return mWeeks.map(d => (
                                            <TableHead key={d} className="text-center min-w-[100px] border-l h-auto py-1">
                                                <div className="text-xs">{safeFormat(d, 'dd/MM')}</div>
                                                <div className="text-[10px] text-muted-foreground font-normal">Week</div>
                                            </TableHead>
                                        ));
                                    }
                                })}
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={uniqueDates.length + 2} className="text-center h-24">
                                        <Loader2 className="h-8 w-8 animate-spin mx-auto" />
                                    </TableCell>
                                </TableRow>
                            ) : (data
                                .filter(row => selectedGroup === "ALL" || row.category === selectedGroup || row.group_name === selectedGroup) // Filter Logic
                                .map(row => (
                                    <TableRow key={row.sku_id}>
                                        <TableCell className="font-medium sticky left-0 bg-background z-10 border-r">{row.sku_id}</TableCell>
                                        <TableCell className="sticky left-[100px] bg-background z-10 border-r truncate max-w-[200px]" title={row.product_name}>{row.product_name}</TableCell>
                                        {uniqueMonths.flatMap(m => {
                                            const isCollapsed = collapsedMonths.has(m);

                                            if (isCollapsed) {
                                                // Render Summary Cell
                                                const agg = row.months[m];
                                                if (!agg) return [<TableCell key={`${m}-sum`} className="bg-orange-50 border-l">-</TableCell>];

                                                return [
                                                    <TableCell key={`${m}-sum`} className="text-center border-l text-xs p-1 bg-orange-50 align-top">
                                                        <div className="flex flex-col gap-1 h-full justify-between font-medium">
                                                            <div className="text-[10px] text-gray-500">Fc: {Math.round(agg.forecast)}</div>

                                                            {/* Monthly Plan (Could be editable if desired, but confusing. Keep read-only sum) */}
                                                            <div className="bg-white border rounded px-1 py-0.5 text-sm font-bold shadow-sm">
                                                                {Math.round(agg.planned)}
                                                            </div>

                                                            <div className="flex justify-between items-center text-[10px] px-1 mt-1">
                                                                <span title="Closing End of Month">End: {Math.round(agg.closing)}</span>
                                                                {agg.net_req > 0 && <span className="text-red-600 font-bold bg-white px-1 border rounded">Buy:{Math.round(agg.net_req)}</span>}
                                                            </div>
                                                        </div>
                                                    </TableCell>
                                                ];
                                            } else {
                                                // Render Weekly Cells
                                                const mWeeks = uniqueDates.filter(d => d.startsWith(m));
                                                return mWeeks.map(d => {
                                                    const cell = row.weeks[d];
                                                    if (!cell) return <TableCell key={d} className="border-l bg-gray-50">-</TableCell>;

                                                    // Edit check
                                                    const editKey = `${row.sku_id}|${d}`;
                                                    const editedVal = edits[editKey];
                                                    const displayPlan = editedVal !== undefined ? editedVal : cell.planned;
                                                    const isEdited = editedVal !== undefined;

                                                    // Status Color
                                                    let bgClass = "";
                                                    if (cell.status === 'CRITICAL') bgClass = "bg-red-50";
                                                    else if (cell.status === 'LOW') bgClass = "bg-yellow-50";
                                                    else if (cell.status === 'OVERSTOCK') bgClass = "bg-blue-50";

                                                    return (
                                                        <TableCell key={d} className={`text-center border-l text-xs p-1 ${bgClass} align-top`}>
                                                            <div className="flex flex-col gap-1 h-full justify-between">
                                                                <div className="flex justify-between items-center text-[10px] text-gray-500 px-1">
                                                                    <span>Fc: {Math.round(cell.forecast)}</span>
                                                                    {cell.incoming > 0 && <span className="text-blue-600 font-bold">In: {cell.incoming}</span>}
                                                                </div>

                                                                {/* Editable Plan */}
                                                                <div className="px-1">
                                                                    <input
                                                                        className={`w-full text-center border rounded px-1 py-0.5 text-sm font-bold ${isEdited ? 'bg-yellow-100 border-yellow-400' : 'bg-white border-gray-200'}`}
                                                                        value={displayPlan}
                                                                        onChange={(e) => handleEdit(row.sku_id, d, e.target.value)}
                                                                    />
                                                                </div>

                                                                {/* Closing & Net */}
                                                                <div className="flex justify-between items-center text-[10px] px-1 mt-1">
                                                                    <span title="Closing Stock">End: {Math.round(cell.closing)}</span>
                                                                    {cell.net_req > 0 && (
                                                                        <span className="text-red-600 font-bold bg-white px-1 rounded border border-red-100">
                                                                            Buy: {Math.round(cell.net_req)}
                                                                        </span>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </TableCell>
                                                    )
                                                });
                                            }
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
