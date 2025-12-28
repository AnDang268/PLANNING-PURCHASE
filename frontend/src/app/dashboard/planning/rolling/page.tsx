
"use client";
import Link from 'next/link';

import { useEffect, useState, useMemo, Fragment } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { API_BASE_URL } from "@/config";
import { ChevronsUpDown, Maximize2, Minimize2, ChevronLeft, ChevronRight, ChevronDown, Check, Search, Upload, FileDown, Columns } from "lucide-react";
import { ProductMultiSelect } from "@/components/ProductMultiSelect";
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
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
import { Download, Upload, Play, Save, Loader2, ChevronDown, ChevronRight, Settings, Maximize2, Minimize2, Columns, Check, FileDown, Search, ChevronLeft } from 'lucide-react';
import { format, parseISO, startOfMonth, endOfMonth, isSameMonth } from "date-fns";
import * as XLSX from 'xlsx';
import { Combobox } from "@/components/ui/combobox";
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
} from "@/components/ui/command";
import { useToast } from "@/components/ui/use-toast";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";


// Types
interface RollingRecord {
    sku_id: string;
    product_name: string;
    category: string; // Group
    parent_group?: string; // [NEW] For Tree Structure
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
    min_stock_policy?: number;
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
    const [visibleMonths, setVisibleMonths] = useState<Set<string>>(new Set()); // [NEW] Visibility Filter
    const [collapsedMonths, setCollapsedMonths] = useState<Set<string>>(new Set());
    const [calculating, setCalculating] = useState(false);

    // Edits: key = "sku|date", value = number
    const [edits, setEdits] = useState<{ [key: string]: number }>({});
    const [saving, setSaving] = useState(false);

    // Filters
    const [groups, setGroups] = useState<any[]>([]);
    const [selectedGroup, setSelectedGroup] = useState<string>("ALL");
    const [openGroupParam, setOpenGroupParam] = useState(false); // For Popover

    // New Warehouse Filter
    const [warehouses, setWarehouses] = useState<any[]>([]);
    const [selectedWarehouse, setSelectedWarehouse] = useState<string>("ALL");

    // Profile State
    const [profiles, setProfiles] = useState<PlanningProfile[]>([]);
    const [selectedProfile, setSelectedProfile] = useState<string>("STD");
    const [runDate, setRunDate] = useState<string>(new Date().toISOString().slice(0, 10)); // Default Today

    // UI State
    const [isFullScreen, setIsFullScreen] = useState(false);

    // Group Expansion State
    const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
    const toggleGroup = (e: React.MouseEvent, groupId: string) => {
        e.stopPropagation();
        const newSet = new Set(expandedGroups);
        if (newSet.has(groupId)) newSet.delete(groupId);
        else newSet.add(groupId);
        setExpandedGroups(newSet);
    };

    // --- Initialization ---
    useEffect(() => {
        fetchData();
        fetchProfiles(); // fetchProfiles calls fetchGroups and fetchWarehouses internally now
    }, []);

    // --- Data Fetching ---
    interface GroupNode {
        id: string;
        name: string;
        parent?: string;
        level: number;
        children: GroupNode[];
    }

    const buildGroupTree = (rawGroups: any[]): GroupNode[] => {
        const map: Record<string, GroupNode> = {};
        const roots: GroupNode[] = [];

        // 1. Init Map
        rawGroups.forEach((g: any) => {
            const gid = g.group_id || g.id;
            map[gid] = {
                id: gid,
                name: g.group_name || g.name,
                parent: g.parent_id || g.parent, // Normalize
                level: 0,
                children: []
            };
        });

        // 2. Build Tree
        rawGroups.forEach((g: any) => {
            const gid = g.group_id || g.id;
            const node = map[gid];
            const pid = g.parent_id || g.parent;

            if (pid && map[pid]) {
                map[pid].children.push(node);
            } else {
                roots.push(node); // No parent or parent not found -> Root
            }
        });

        return roots;
    };

    const flattenGroupTree = (nodes: GroupNode[], level = 0, result: any[] = []): any[] => {
        nodes.forEach(node => {
            node.level = level;
            result.push(node);
            if (node.children && node.children.length > 0) {
                // Sort children by name
                node.children.sort((a, b) => a.name.localeCompare(b.name));
                flattenGroupTree(node.children, level + 1, result);
            }
        });
        return result;
    };

    // --- Data Fetching ---
    const fetchGroups = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/data/groups`);
            if (Array.isArray(res.data)) {
                const tree = buildGroupTree(res.data);
                tree.sort((a, b) => a.name.localeCompare(b.name));
                const flat = flattenGroupTree(tree);
                setGroups(flat);
            }
        } catch (e) {
            console.error("Failed to fetch groups", e);
        }
    };

    const fetchWarehouses = async () => {
        try {
            // New endpoint we just added
            const res = await axios.get(`${API_BASE_URL}/api/planning/rolling/warehouses`);
            if (Array.isArray(res.data)) {
                // Deduplicate by warehouse_id
                const uniqueWh = Array.from(new Map(res.data.map((w: any) => [w.warehouse_id, w])).values());
                setWarehouses(uniqueWh as any[]);
            }
        } catch (e) {
            console.error("Failed to fetch warehouses", e);
        }
    };

    const fetchProfiles = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/planning/rolling/profiles`);
            if (res.data && Array.isArray(res.data)) {
                setProfiles(res.data);
            } else {
                setProfiles([]);
            }
            // Chain initial fetches
            fetchGroups();
            fetchWarehouses();
        } catch (e) {
            console.error("Failed to fetch initial data", e);
        }
    };


    // Prepare Group Options with Hierarchy
    const groupOptions = useMemo(() => {
        // The groups state is now flattened tree: { id, name, level, parent, children }
        // We can just use it directly, but for compatibility with existing UI Select (if used elsewhere)
        // or just to be safe, we map it.
        const opts = groups.map(g => {
            // "name" is guaranteed by buildGroupTree/fetchWarehouses logic
            return { value: g.id, label: g.name };
        });

        // Add "All"
        opts.unshift({ value: "ALL", label: "All Groups" });

        // Safety Sort
        return opts.sort((a, b) => {
            const la = a.label || "";
            const lb = b.label || "";
            return la.localeCompare(lb);
        });
    }, [groups]);
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(20);
    const [totalItems, setTotalItems] = useState(0);

    // Date Range Filters
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    const endOfYear = new Date(now.getFullYear(), 11, 31);

    // Use string YYYY-MM-DD for simpler handling or Date objects
    // Using Date objects with DatePicker is standard.
    const [fromDate, setFromDate] = useState<Date | undefined>(startOfMonth);
    const [toDate, setToDate] = useState<Date | undefined>(endOfYear);

    const [searchTerm, setSearchTerm] = useState("");

    const fetchData = async () => {
        setLoading(true);
        try {
            let url = `${API_BASE_URL}/api/planning/rolling/matrix?page=${page}&limit=${pageSize}`;

            if (selectedGroup && selectedGroup !== 'ALL') url += `&group_id=${selectedGroup}`;
            if (selectedWarehouse && selectedWarehouse !== 'ALL') url += `&warehouse_id=${selectedWarehouse}`;
            if (selectedProfile) url += `&profile_id=${selectedProfile}`;
            if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;

            console.log("Fetching Rolling Data:", url);

            console.log("Fetching Rolling Data:", url);
            const res = await axios.get(url);

            // Handle Paginated Response
            if (res.data && res.data.data) {
                processData(res.data.data);
                setTotalItems(res.data.total);
            } else if (Array.isArray(res.data)) {
                // Fallback for older API?
                processData(res.data);
                setTotalItems(res.data.length);
            }
        } catch (error) {
            console.error("Failed to fetch matrix", error);
        } finally {
            setLoading(false);
        }
    };

    // Filter Listeners (Reset Page on Filter Change)
    useEffect(() => {
        setPage(1);
        fetchData();
    }, [selectedGroup, selectedWarehouse, selectedProfile]); // Reset Page on filter change

    // Page Change Listener
    useEffect(() => {
        fetchData();
    }, [page, pageSize]);

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
                // Simple regex check YYYY-MM-DD
                return /^\d{4}-\d{2}-\d{2}/.test(d);
            });

        // Filter Columns by Date Range Scope (Frontend Display Logic)
        // If we want Backend to filter columns, we pass params.
        // For now, let's filter the Displayed Columns here based on `fromDate` and `toDate`.
        const filteredDates = validDates.filter(d => {
            if (!fromDate && !toDate) return true;
            const dObj = new Date(d);
            if (fromDate && dObj < fromDate) return false;
            if (toDate && dObj > toDate) return false;
            return true;
        });

        const dates = Array.from(new Set(filteredDates)).sort();
        setUniqueDates(dates);

        const months = Array.from(new Set(dates.map(d => d.substring(0, 7)))).sort(); // YYYY-MM
        setUniqueMonths(months);

        // Update Visibility based on filtered months
        setVisibleMonths(new Set(months));
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
                profile_id: selectedProfile,
                group_id: selectedGroup,
                warehouse_id: selectedWarehouse,
                run_date: runDate
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
        // 1. Meta Data Sheet
        const metaData = [
            ["Rolling Supply Plan Export"],
            ["Generated At", new Date().toLocaleString()],
            ["Profile", selectedProfile],
            ["Group Filter", selectedGroup],
            ["Warehouse Filter", selectedWarehouse],
            ["Calculation Date", runDate],
            ["Total SKUs", data.length]
        ];
        const wsMeta = XLSX.utils.aoa_to_sheet(metaData);

        // 2. Main Data Sheet
        const exportData: any[] = [];

        data.forEach(row => {
            // Base Columns
            const baseRow: any = {
                "SKU": row.sku_id,
                "Product Name": row.product_name,
                "Category": row.category,
                "Min Stock Policy": Math.round(row.min_stock_policy || 0)
            };

            // Dynamic Date Columns
            uniqueDates.forEach(d => {
                const cell = row.weeks[d];
                if (cell) {
                    // Group by Date for readability? 
                    // Excel flat format: [Date] Forecast, [Date] Stock, etc.
                    baseRow[`${d} (Forecast)`] = cell.forecast;
                    baseRow[`${d} (Open Stock)`] = cell.opening_stock;
                    baseRow[`${d} (Incoming)`] = cell.incoming;
                    baseRow[`${d} (Planned)`] = cell.planned;
                    baseRow[`${d} (Closing)`] = cell.closing;
                    baseRow[`${d} (Net Req)`] = cell.net_req;
                }
            });
            exportData.push(baseRow);
        });

        const wsData = XLSX.utils.json_to_sheet(exportData);

        // Create Workbook
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, wsMeta, "Info");
        XLSX.utils.book_append_sheet(wb, wsData, "Supply Plan");

        // Generate Filename
        const fname = `SupplyPlan_${selectedProfile}_${runDate}_${new Date().getTime()}.xlsx`;
        XLSX.writeFile(wb, fname);
    };

    const { toast } = useToast();

    // ...

    const handleImportOpenStock = async (file: File) => {
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append("file", file);
            const res = await axios.post(`${API_BASE_URL}/api/data/import/upload?type=opening_stock`, formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });
            if (res.status === 200) {
                toast({ title: "Import Success", description: res.data.message });
                fetchData();
            }
        } catch (e: any) {
            console.error(e);
            toast({ title: "Import Failed", description: e.response?.data?.detail || "Unknown Error", variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };


    const handleImportMatrix = async (file: File) => {
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("profile_id", selectedProfile);
            formData.append("warehouse_id", selectedWarehouse);

            const res = await axios.post(`${API_BASE_URL}/api/planning/rolling/import/matrix`, formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });

            if (res.data.status === "success") {
                toast({ title: "Import Success", description: res.data.message });
                if (res.data.errors && res.data.errors.length > 0) {
                    console.warn("Import Warnings:", res.data.errors);
                    toast({ title: "Import Warnings", description: "Imported with warnings. Check console.", variant: "warning" });
                }
                fetchData();
            }
        } catch (e: any) {
            console.error(e);
            toast({ title: "Import Failed", description: e.response?.data?.detail || e.message, variant: "destructive" });
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



                        <input
                            type="date"
                            className="border rounded p-2 text-sm"
                            value={runDate}
                            onChange={(e) => setRunDate(e.target.value)}
                            title="Start Date for Calculation"
                        />

                        <div className="flex gap-2">
                            <Button onClick={handleRunCalculation} disabled={calculating} className="bg-primary hover:bg-primary/90">
                                {calculating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                                Run
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
                        <Popover open={openGroupParam} onOpenChange={setOpenGroupParam}>
                            <PopoverTrigger asChild>
                                <Button
                                    variant="outline"
                                    role="combobox"
                                    aria-expanded={openGroupParam}
                                    className="w-[200px] justify-between"
                                >
                                    {selectedGroup
                                        ? groupOptions.find((group) => group.value === selectedGroup)?.label
                                        : "Select group..."}
                                    <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-[200px] p-0">
                                <Command>
                                    <CommandInput placeholder="Search group..." />
                                    <CommandEmpty>No group found.</CommandEmpty>
                                    <CommandGroup>
                                        <CommandItem
                                            value="ALL"
                                            onSelect={() => {
                                                setSelectedGroup("ALL")
                                                setOpenGroupParam(false)
                                            }}
                                        >
                                            <Check
                                                className={cn(
                                                    "mr-2 h-4 w-4",
                                                    selectedGroup === "ALL" ? "opacity-100" : "opacity-0"
                                                )}
                                            />
                                            All Groups
                                        </CommandItem>

                                        {groups.map((group) => {
                                            // Visibility Check
                                            let isVisible = true;
                                            if (group.level > 0) {
                                                if (group.parent && group.parent !== 'Main' && !expandedGroups.has(group.parent)) {
                                                    isVisible = false;
                                                }
                                                // Simple check for now.
                                            }

                                            // FIX: We need a reliable ancestry check.
                                            // Let's assume groups are small enough (<200) to just find parent.
                                            let curr = group;
                                            while (curr && curr.level > 0 && isVisible) {
                                                if (curr.parent && curr.parent !== 'Main') {
                                                    if (!expandedGroups.has(curr.parent)) {
                                                        isVisible = false;
                                                        break;
                                                    }
                                                    // Find parent object
                                                    curr = groups.find(g => g.id === curr.parent) || (null as any);
                                                } else {
                                                    break;
                                                }
                                            }

                                            if (!isVisible) return null;

                                            const hasChildren = groups.some(g => g.parent === group.id);

                                            return (
                                                <CommandItem
                                                    key={group.id}
                                                    value={group.name} // Search by name
                                                    onSelect={() => {
                                                        setSelectedGroup(group.id === selectedGroup ? "ALL" : group.id)
                                                        setOpenGroupParam(false)
                                                    }}
                                                >
                                                    <div className="flex items-center w-full">
                                                        <div style={{ width: `${(group.level || 0) * 16}px` }} className="shrink-0" />

                                                        {hasChildren ? (
                                                            <div
                                                                className="h-4 w-4 mr-1 shrink-0 cursor-pointer hover:bg-muted rounded flex items-center justify-center"
                                                                onClick={(e) => toggleGroup(e, group.id)}
                                                            >
                                                                {expandedGroups.has(group.id) ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                                                            </div>
                                                        ) : (
                                                            <div className="w-5 shrink-0" />
                                                        )}

                                                        <Check
                                                            className={cn(
                                                                "mr-2 h-4 w-4 shrink-0",
                                                                selectedGroup === group.id ? "opacity-100" : "opacity-0"
                                                            )}
                                                        />
                                                        <span className="truncate">{group.name}</span>
                                                    </div>
                                                </CommandItem>
                                            );
                                        })}
                                    </CommandGroup>
                                </Command>
                            </PopoverContent>
                        </Popover>

                        <div className="w-[180px]">
                            <Select value={selectedWarehouse} onValueChange={setSelectedWarehouse}>
                                <SelectTrigger>
                                    <SelectValue placeholder="All Warehouses" />
                                </SelectTrigger>
                                <SelectContent className="bg-white">
                                    <SelectItem value="ALL">All Warehouses</SelectItem>
                                    {warehouses.map((w: any) => (
                                        <SelectItem key={w.warehouse_id} value={w.warehouse_id}>{w.warehouse_name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* SKU Search */}
                        <div className="relative">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <input
                                placeholder="Search SKU/Product..."
                                className="pl-8 h-10 w-[200px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') fetchData();
                                }}
                            />
                        </div>

                        <div className="flex items-center space-x-2">
                            {/* Date Range Filters */}
                            <div className="flex items-center gap-1 border rounded px-2 bg-white h-8">
                                <span className="text-xs text-gray-500">From:</span>
                                <input
                                    type="date"
                                    className="text-xs border-none focus:ring-0 w-[110px] h-full"
                                    value={fromDate ? fromDate.toISOString().substr(0, 10) : ''}
                                    onChange={(e) => {
                                        const d = e.target.value ? new Date(e.target.value) : undefined;
                                        setFromDate(d);
                                    }}
                                />
                                <span className="text-xs text-gray-500">- To:</span>
                                <input
                                    type="date"
                                    className="text-xs border-none focus:ring-0 w-[110px] h-full"
                                    value={toDate ? toDate.toISOString().substr(0, 10) : ''}
                                    onChange={(e) => {
                                        const d = e.target.value ? new Date(e.target.value) : undefined;
                                        setToDate(d);
                                    }}
                                />
                                <Button variant="ghost" size="sm" onClick={() => fetchData()} title="Apply Filter" className="h-full px-2">
                                    <span className="text-xs font-bold text-blue-600">Apply</span>
                                </Button>
                            </div>

                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="outline" size="sm" className="h-8 gap-1">
                                        <Columns className="h-3.5 w-3.5" />
                                        <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                                            Columns
                                        </span>
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-[150px]">
                                    <DropdownMenuLabel>Toggle Months</DropdownMenuLabel>
                                    <DropdownMenuSeparator />
                                    {uniqueMonths.map((month) => {
                                        return (
                                            <DropdownMenuCheckboxItem
                                                key={month}
                                                checked={visibleMonths.has(month)}
                                                onSelect={(e) => e.preventDefault()}
                                                onCheckedChange={(checked) => {
                                                    const next = new Set(visibleMonths);
                                                    if (checked) next.add(month);
                                                    else next.delete(month);
                                                    setVisibleMonths(next);
                                                }}
                                            >
                                                {month}
                                            </DropdownMenuCheckboxItem>
                                        )
                                    })}
                                </DropdownMenuContent>
                            </DropdownMenu>
                            {/* Export Buttons */}
                            <Button size="sm" variant="outline" className="h-8 gap-1" onClick={handleExportExcel}>
                                <FileDown className="h-3.5 w-3.5" />
                                <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                                    Export
                                </span>
                            </Button>

                            <Button size="sm" variant="outline" className="h-8 gap-1" onClick={() => document.getElementById('import-matrix')?.click()}>
                                <Upload className="h-3.5 w-3.5" />
                                <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
                                    Import Plan
                                </span>
                            </Button>
                            <input
                                id="import-matrix"
                                type="file"
                                accept=".xlsx, .xls"
                                className="hidden"
                                onChange={(e) => {
                                    if (e.target.files && e.target.files[0]) handleImportMatrix(e.target.files[0]);
                                }}
                            />

                            {/* Full Screen Toggle */}
                            <Button size="sm" variant="ghost" onClick={() => setIsFullScreen(!isFullScreen)}>
                                {isFullScreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                            </Button>
                        </div>
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

            {/* Legend */}
            <div className="flex gap-4 text-xs text-muted-foreground bg-muted/20 p-2 rounded items-center">
                <div className="font-semibold">Legend:</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 bg-gray-500 rounded-full" /> <span className="font-medium">Fcst:</span> Forecast Demand</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 bg-gray-400 rounded-full" /> <span className="font-medium">Open:</span> Opening Stock</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 bg-blue-500 rounded-full" /> <span className="font-medium">In:</span> Incoming Supply (PO)</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 bg-yellow-600 rounded-full" /> <span className="font-medium">Plan:</span> Planned Supply (System/User)</div>
                <div className="flex items-center gap-1"><div className="w-2 h-2 bg-gray-800 rounded-full" /> <span className="font-medium">Close:</span> Closing Stock</div>
            </div>

            <Card className={cn(
                "flex flex-col transition-all duration-300",
                isFullScreen ? "fixed inset-0 z-[100] h-screen w-screen rounded-none m-0 border-0" : "overflow-hidden"
            )}>
                <CardHeader className="bg-muted/50 pb-4 flex flex-col gap-4">
                    {/* Header Row: Title + Top Controls */}
                    <div className="flex flex-row justify-between items-center">
                        <div>
                            <CardTitle>Supply Matrix Worksheet</CardTitle>
                            <CardDescription>Review projected inventory and adjust planned orders.</CardDescription>
                        </div>

                        <div className="flex items-center gap-2">
                            {/* Pagination */}
                            <span className="text-sm text-gray-500">
                                Page {page} of {Math.ceil(totalItems / pageSize)} ({totalItems} items)
                            </span>
                            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
                                <ChevronLeft className="h-4 w-4" />
                            </Button>
                            <Button variant="outline" size="sm" disabled={page >= Math.ceil(totalItems / pageSize)} onClick={() => setPage(p => p + 1)}>
                                <ChevronRight className="h-4 w-4" />
                            </Button>

                            {isFullScreen && (
                                <Button variant="outline" size="sm" onClick={() => setIsFullScreen(false)}>
                                    <Minimize2 className="mr-2 h-4 w-4" /> Close
                                </Button>
                            )}
                            {!isFullScreen && (
                                <Button variant="ghost" size="sm" onClick={() => setIsFullScreen(true)}>
                                    <Maximize2 className="h-4 w-4" />
                                </Button>
                            )}
                        </div>
                    </div>

                    {/* Filter Bar (Visible in Full Screen too) */}
                    <div className="flex flex-wrap items-center gap-2 bg-background p-2 rounded border">
                        {/* Group Filter */}
                        <Popover open={openGroupParam} onOpenChange={setOpenGroupParam}>
                            <PopoverTrigger asChild>
                                <Button variant="outline" role="combobox" aria-expanded={openGroupParam} className="w-[180px] justify-between h-9 text-xs">
                                    {selectedGroup === "ALL" ? "All Groups" : groups.find(g => g.id === selectedGroup)?.name || "Select Group"}
                                    <ChevronsUpDown className="ml-2 h-3 w-3 shrink-0 opacity-50" />
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-[300px] p-0" align="start">
                                <Command>
                                    <CommandInput placeholder="Search Group..." />
                                    <CommandEmpty>No group found.</CommandEmpty>
                                    <CommandGroup className="max-h-[300px] overflow-y-auto">
                                        <CommandItem value="ALL" onSelect={() => { setSelectedGroup("ALL"); setOpenGroupParam(false) }}>
                                            <Check className={cn("mr-2 h-4 w-4", selectedGroup === "ALL" ? "opacity-100" : "opacity-0")} />
                                            All Groups
                                        </CommandItem>
                                        {flattenGroupTree(buildGroupTree(groups)).map((group) => {
                                            let isVisible = true;
                                            let curr = group;
                                            while (curr && curr.level > 0 && isVisible) {
                                                if (curr.parent && curr.parent !== 'Main' && !expandedGroups.has(curr.parent)) {
                                                    isVisible = false; break;
                                                }
                                                curr = groups.find(g => g.id === curr.parent) || (null as any);
                                            }
                                            if (!isVisible) return null;
                                            const hasChildren = groups.some(g => g.parent === group.id);

                                            return (
                                                <CommandItem key={group.id} value={group.name} onSelect={() => { setSelectedGroup(group.id === selectedGroup ? "ALL" : group.id); setOpenGroupParam(false) }}>
                                                    <div className="flex items-center w-full">
                                                        <div style={{ width: `${(group.level || 0) * 16}px` }} className="shrink-0" />
                                                        {hasChildren ? (
                                                            <div className="h-4 w-4 mr-1 shrink-0 cursor-pointer hover:bg-muted rounded flex items-center justify-center" onClick={(e) => toggleGroup(e, group.id)}>
                                                                {expandedGroups.has(group.id) ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                                                            </div>
                                                        ) : <div className="w-5 shrink-0" />}
                                                        <Check className={cn("mr-2 h-4 w-4 shrink-0", selectedGroup === group.id ? "opacity-100" : "opacity-0")} />
                                                        <span className="truncate">{group.name}</span>
                                                    </div>
                                                </CommandItem>
                                            );
                                        })}
                                    </CommandGroup>
                                </Command>
                            </PopoverContent>
                        </Popover>

                        {/* Product Multi Select */}
                        <div className="w-[250px]">
                            <ProductMultiSelect value={selectedSkuList} onChange={setSelectedSkuList} />
                        </div>

                        {/* Warehouse Filter */}
                        <div className="w-[150px]">
                            <Select value={selectedWarehouse} onValueChange={setSelectedWarehouse}>
                                <SelectTrigger className="h-9 text-xs">
                                    <SelectValue placeholder="All Warehouses" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="ALL">All Warehouses</SelectItem>
                                    {warehouses.map((w: any) => (
                                        <SelectItem key={w.warehouse_id} value={w.warehouse_id}>{w.warehouse_name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Text Search */}
                        <div className="relative">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <input
                                placeholder="Search SKU/Name..."
                                className="pl-8 h-9 w-[150px] rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                onKeyDown={(e) => { if (e.key === 'Enter') fetchData(); }}
                            />
                        </div>


                        <Button size="sm" onClick={fetchData}>Apply</Button>

                        <div className="flex-1" />

                        {/* Tools */}
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="outline" size="sm" className="h-9"><Columns className="mr-2 h-3.5 w-3.5" /> Cols</Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-[150px] max-h-[300px] overflow-y-auto">
                                <DropdownMenuLabel>Toggle Months</DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                {uniqueMonths.map(m => (
                                    <DropdownMenuCheckboxItem key={m} checked={visibleMonths.has(m)} onCheckedChange={(checked) => {
                                        const next = new Set(visibleMonths);
                                        if (checked) next.add(m); else next.delete(m);
                                        setVisibleMonths(next);
                                    }}>{m}</DropdownMenuCheckboxItem>
                                ))}
                            </DropdownMenuContent>
                        </DropdownMenu>

                        <Button size="sm" variant="outline" className="h-9 gap-1" onClick={handleExportExcel}>
                            <FileDown className="h-3.5 w-3.5" /> Export
                        </Button>
                        <Button size="sm" variant="outline" className="h-9 gap-1" onClick={() => document.getElementById('import-matrix')?.click()}>
                            <Upload className="h-3.5 w-3.5" /> Import Plan
                        </Button>
                    </div>

                </CardHeader>
                <div className="overflow-x-auto flex-1">
                    <Table className="border-collapse h-full">
                        <TableHeader>
                            <TableRow>
                                <TableHead rowSpan={3} className="w-[100px] sticky left-0 bg-background z-20 border-r text-center align-middle h-auto">SKU</TableHead>
                                <TableHead rowSpan={3} className="w-[200px] sticky left-[100px] bg-background z-20 border-r text-center align-middle h-auto">Product</TableHead>
                                {uniqueMonths.filter(m => visibleMonths.has(m)).map(m => {
                                    const mWeeks = uniqueDates.filter(d => d.startsWith(m));
                                    const isCollapsed = collapsedMonths.has(m);
                                    // Collapsed = 5 cols (Summary), Expanded = weeks * 5
                                    const colSpan = isCollapsed ? 5 : mWeeks.length * 5;

                                    return (
                                        <TableHead key={m} colSpan={colSpan} className={`text-center border-l border-r ${isCollapsed ? 'bg-orange-100 font-bold' : 'bg-muted/20'}`}>
                                            <div className="flex items-center justify-center gap-2 cursor-pointer select-none" onClick={() => toggleMonth(m)}>
                                                {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                                                {safeFormat(m + "-01", "MMMM yyyy")}
                                            </div>
                                        </TableHead>
                                    );
                                })}
                            </TableRow>

                            {/* Row 2: Weeks */}
                            <TableRow>
                                {uniqueMonths.filter(m => visibleMonths.has(m)).flatMap(m => {
                                    const isCollapsed = collapsedMonths.has(m);
                                    if (isCollapsed) return <TableHead key={`${m}-sum-head`} colSpan={5} className="text-center font-bold text-xs bg-orange-50 border-r text-orange-700">Summary</TableHead>;

                                    const mWeeks = uniqueDates.filter(d => d.startsWith(m));
                                    return mWeeks.map(d => (
                                        <TableHead key={d} colSpan={5} className="text-center bg-muted/10 border-r text-xs">
                                            {safeFormat(d, 'dd/MM')} (W)
                                        </TableHead>
                                    ));
                                })}
                            </TableRow>

                            {/* Row 3: Measures */}
                            <TableRow>
                                {uniqueMonths.filter(m => visibleMonths.has(m)).flatMap(m => {
                                    const isCollapsed = collapsedMonths.has(m);
                                    if (isCollapsed) {
                                        return [
                                            <TableHead key={`${m}-fc`} className="w-[80px] text-xs text-center border-r font-normal text-gray-500" title="Forecast Demand">Fcst</TableHead>,
                                            <TableHead key={`${m}-op`} className="w-[80px] text-xs text-center border-r font-normal text-gray-400" title="Opening Stock">Open</TableHead>,
                                            <TableHead key={`${m}-in`} className="w-[80px] text-xs text-center border-r font-normal text-blue-500" title="Incoming Supply (PO)">In</TableHead>,
                                            <TableHead key={`${m}-pl`} className="w-[80px] text-xs text-center border-r font-bold text-yellow-600" title="Planned Supply (Order)">Plan</TableHead>,
                                            <TableHead key={`${m}-cl`} className="w-[80px] text-xs text-center border-r font-bold text-gray-800" title="Closing Stock">Close</TableHead>
                                        ];
                                    }
                                    const mWeeks = uniqueDates.filter(d => d.startsWith(m));
                                    return mWeeks.flatMap(d => [
                                        <TableHead key={`${d}-fc`} className="w-[60px] text-[10px] text-center border-l font-normal text-gray-500 p-1" title="Forecast">Fcst</TableHead>,
                                        <TableHead key={`${d}-op`} className="w-[60px] text-[10px] text-center border-l font-normal text-gray-400 p-1" title="Opening">Open</TableHead>,
                                        <TableHead key={`${d}-in`} className="w-[60px] text-[10px] text-center border-l font-normal text-blue-500 p-1" title="Incoming">In</TableHead>,
                                        <TableHead key={`${d}-pl`} className="w-[60px] text-[10px] text-center border-l font-bold text-yellow-600 p-1 bg-yellow-50/50" title="Plan">Plan</TableHead>,
                                        <TableHead key={`${d}-cl`} className="w-[60px] text-[10px] text-center border-r font-bold text-gray-800 p-1" title="Close">Close</TableHead>
                                    ]);
                                })}
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={20} className="text-center h-24">
                                        <Loader2 className="h-8 w-8 animate-spin mx-auto" />
                                    </TableCell>
                                </TableRow>
                            ) : (data
                                .filter(row => selectedGroup === "ALL" || row.category === selectedGroup || row.group_name === selectedGroup) // Client-side filter might be redundant with Search but safe to keep
                                .map(row => {
                                    return (
                                        <TableRow key={row.sku_id} className="hover:bg-muted/30 odd:bg-white even:bg-gray-50/30">
                                            {/* Fixed Columns */}
                                            <TableCell className="font-medium sticky left-0 bg-background z-10 border-r align-top py-2 w-[100px] text-xs">
                                                <div>{row.sku_id}</div>
                                                <div className="text-[10px] text-muted-foreground mt-1 truncate max-w-[90px]" title={row.category}>{row.category}</div>
                                            </TableCell>
                                            <TableCell className="sticky left-[100px] bg-background z-10 border-r truncate max-w-[200px] align-top py-2 w-[200px] text-xs" title={row.product_name}>
                                                {row.product_name}
                                            </TableCell>

                                            {/* Dynamic Columns */}
                                            {uniqueMonths.filter(m => visibleMonths.has(m)).flatMap(m => {
                                                const isCollapsed = collapsedMonths.has(m);

                                                if (isCollapsed) {
                                                    // Summary - 5 Cols
                                                    const agg = row.months[m] || { forecast: 0, opening: 0, incoming: 0, planned: 0, closing: 0, net_req: 0 };
                                                    return [
                                                        <TableCell key={`${m}-fc`} className="text-center border-r text-xs p-1">{Math.round(agg.forecast).toLocaleString()}</TableCell>,
                                                        <TableCell key={`${m}-op`} className="text-center border-r text-xs p-1 text-gray-400">-</TableCell>, // Opening Summary ambiguous?
                                                        <TableCell key={`${m}-in`} className="text-center border-r text-xs p-1">{Math.round(agg.incoming).toLocaleString()}</TableCell>,
                                                        <TableCell key={`${m}-pl`} className="text-center border-r text-xs p-1 font-bold text-yellow-700">{Math.round(agg.planned).toLocaleString()}</TableCell>,
                                                        <TableCell key={`${m}-cl`} className="text-center border-r text-xs p-1 font-bold">{Math.round(agg.closing || 0).toLocaleString()}</TableCell>
                                                    ];
                                                }

                                                const mWeeks = uniqueDates.filter(d => d.startsWith(m));
                                                return mWeeks.flatMap(d => {
                                                    const cell = row.weeks[d];
                                                    if (!cell) {
                                                        return Array(5).fill(null).map((_, i) => <TableCell key={`${d}-${i}`} className="border-l bg-gray-50">-</TableCell>);
                                                    }

                                                    // Planned Input
                                                    const editKey = `${row.sku_id}|${d}`;
                                                    const editedVal = edits[editKey];
                                                    const displayPlan = editedVal !== undefined ? editedVal : cell.planned;
                                                    const isEdited = editedVal !== undefined;

                                                    return [
                                                        <TableCell key={`${d}-fc`} className="text-center border-l text-xs p-1 text-gray-500">{Math.round(cell.forecast).toLocaleString()}</TableCell>,
                                                        <TableCell key={`${d}-op`} className="text-center border-l text-xs p-1 text-gray-400">{Math.round(cell.opening_stock).toLocaleString()}</TableCell>,
                                                        <TableCell key={`${d}-in`} className="text-center border-l text-xs p-1 text-blue-600">{Math.round(cell.incoming).toLocaleString()}</TableCell>,
                                                        <TableCell key={`${d}-pl`} className="text-center border-l p-0 bg-yellow-50/30">
                                                            <input
                                                                className={`w-full h-full text-center bg-transparent focus:bg-white text-xs font-bold p-1 ${isEdited ? 'text-yellow-700' : ''}`}
                                                                value={displayPlan}
                                                                onChange={(e) => handleEdit(row.sku_id, d, e.target.value)}
                                                            />
                                                        </TableCell>,
                                                        <TableCell key={`${d}-cl`} className="text-center border-r text-xs p-1 font-bold border-l">{Math.round(cell.closing).toLocaleString()}</TableCell>
                                                    ];
                                                });
                                            })}
                                        </TableRow>
                                    );
                                })
                            )}
                        </TableBody>
                    </Table>
                </div>
            </Card >
        </div >
    );
}
