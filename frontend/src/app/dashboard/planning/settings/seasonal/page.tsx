"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "@/config";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Save, Loader2, ArrowLeft } from "lucide-react";
import Link from "next/link";

interface SeasonalFactor {
    month: number;
    demand_multiplier: number;
    supplier_delay_days: number;
    shipping_delay_days: number;
    description: string;
}

const MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
];

export default function SeasonalSettingsPage() {
    const [factors, setFactors] = useState<SeasonalFactor[]>([]);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [edits, setEdits] = useState<{ [key: number]: SeasonalFactor }>({});

    useEffect(() => {
        fetchFactors();
    }, []);

    const fetchFactors = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE_URL}/api/planning/settings/seasonal`);
            setFactors(res.data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (month: number, field: keyof SeasonalFactor, value: any) => {
        const current = edits[month] || factors.find(f => f.month === month) || {
            month,
            demand_multiplier: 1,
            supplier_delay_days: 0,
            shipping_delay_days: 0,
            description: ''
        };

        let processedValue = value;
        if (field === 'demand_multiplier') processedValue = parseFloat(value) || 0;
        if (field === 'supplier_delay_days' || field === 'shipping_delay_days') processedValue = parseInt(value) || 0;

        setEdits(prev => ({
            ...prev,
            [month]: { ...current, [field]: processedValue }
        }));
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            await axios.put(`${API_BASE_URL}/api/planning/settings/seasonal/update`, Object.values(edits));
            setEdits({});
            fetchFactors();
            alert("Changes saved!");
        } catch (e) {
            alert("Failed to save changes.");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="container mx-auto p-4 space-y-6">
            <div className="flex items-center gap-4">
                <Link href="/dashboard/planning/settings">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h1 className="text-2xl font-bold">Seasonal Factors Configuration</h1>
                    <p className="text-muted-foreground">Adjust demand multipliers and lead time delays by month.</p>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex justify-between items-center">
                        <CardTitle>Monthly Adjustments</CardTitle>
                        {Object.keys(edits).length > 0 && (
                            <Button onClick={handleSave} disabled={saving}>
                                {saving && <Loader2 className="animate-spin mr-2 h-4 w-4" />}
                                <Save className="mr-2 h-4 w-4" />
                                Save Changes
                            </Button>
                        )}
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="w-[100px]">Month</TableHead>
                                <TableHead>Demand Multiplier</TableHead>
                                <TableHead>Supplier Delay (Days)</TableHead>
                                <TableHead>Shipping Delay (Days)</TableHead>
                                <TableHead className="w-[300px]">Description</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center py-8">Loading...</TableCell>
                                </TableRow>
                            ) : factors.map(f => {
                                const active = edits[f.month] || f;
                                return (
                                    <TableRow key={f.month}>
                                        <TableCell className="font-medium">
                                            {f.month} - {MONTH_NAMES[f.month]}
                                        </TableCell>
                                        <TableCell>
                                            <Input
                                                type="number"
                                                step="0.05"
                                                className="w-[100px]"
                                                value={active.demand_multiplier}
                                                onChange={(e) => handleEdit(f.month, 'demand_multiplier', e.target.value)}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Input
                                                type="number"
                                                className="w-[100px]"
                                                value={active.supplier_delay_days}
                                                onChange={(e) => handleEdit(f.month, 'supplier_delay_days', e.target.value)}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Input
                                                type="number"
                                                className="w-[100px]"
                                                value={active.shipping_delay_days}
                                                onChange={(e) => handleEdit(f.month, 'shipping_delay_days', e.target.value)}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Input
                                                value={active.description || ''}
                                                onChange={(e) => handleEdit(f.month, 'description', e.target.value)}
                                            />
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
