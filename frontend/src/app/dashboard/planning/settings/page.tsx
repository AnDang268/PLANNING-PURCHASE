"use client";

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '@/config';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Save, Loader2, ArrowLeft, Trash2 } from 'lucide-react';
import Link from 'next/link';

interface Policy {
    policy_id: number;
    policy_name: string;
    safety_stock_days: number;
    service_level_target: number;
    is_default: boolean;
}

export default function PlanningSettingsPage() {
    const [policies, setPolicies] = useState<Policy[]>([]);
    const [loading, setLoading] = useState(false);
    const [savingId, setSavingId] = useState<number | null>(null);

    const fetchPolicies = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE_URL}/api/planning/rolling/policies`);
            setPolicies(res.data);
        } catch (error) {
            console.error(error);
            alert("Failed to load policies");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPolicies();
    }, []);

    const handleUpdate = async (policy: Policy) => {
        setSavingId(policy.policy_id);
        try {
            await axios.put(`${API_BASE_URL}/api/planning/rolling/policies/${policy.policy_id}`, {
                safety_stock_days: policy.safety_stock_days,
                service_level_target: policy.service_level_target
            });
            alert("Policy updated successfully!");
        } catch (error) {
            console.error(error);
            alert("Failed to update policy");
        } finally {
            setSavingId(null);
        }
    };

    const handleResetData = async () => {
        if (!confirm("DANGER: Are you sure you want to RESET ALL TRANSACTION DATA?\n\nThis will delete all Sales, Purchases, Inventory, and Plans.\nThis cannot be undone.")) return;
        if (!confirm("Double Check: Do you really want to proceed? Log records will also be truncated.")) return;

        setSavingId(-1); // Use -1 as indicator for Reset Button Loading
        setLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/api/data/reset-transactions`);
            alert("System Reset Successfully. All transaction data has been cleared.");
        } catch (error) {
            console.error(error);
            alert("Reset Failed: " + (error as any).response?.data?.detail || "Unknown error");
        } finally {
            setLoading(false);
            setSavingId(null);
        }
    };

    const handleChange = (id: number, field: keyof Policy, val: string) => {
        setPolicies(prev => prev.map(p => {
            if (p.policy_id !== id) return p;
            return { ...p, [field]: parseFloat(val) || 0 };
        }));
    };

    return (
        <div className="container mx-auto p-4 space-y-6">
            <div className="flex items-center gap-4">
                <Link href="/dashboard/planning/rolling">
                    <Button variant="ghost" size="sm">
                        <ArrowLeft className="w-4 h-4 mr-1" /> Back to Matrix
                    </Button>
                </Link>
                <h1 className="text-2xl font-bold">Planning Configuration</h1>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Safety Stock Policies</CardTitle>
                    <p className="text-sm text-gray-500">
                        Define target inventory levels (Days of Supply) for each policy.
                        The "Standard" policy is applied by default.
                    </p>
                </CardHeader>
                <CardContent>
                    {loading ? <div className="p-4 text-center">Loading...</div> : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Policy Name</TableHead>
                                    <TableHead>Safety Stock (Days)</TableHead>
                                    <TableHead>Service Level (0.0 - 1.0)</TableHead>
                                    <TableHead className="w-[100px]">Action</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {policies.map(p => (
                                    <TableRow key={p.policy_id} className={p.is_default ? "bg-blue-50" : ""}>
                                        <TableCell className="font-medium">
                                            {p.policy_name}
                                            {p.is_default && <span className="ml-2 text-xs bg-blue-200 text-blue-800 px-1 rounded">Default</span>}
                                        </TableCell>
                                        <TableCell>
                                            <Input
                                                type="number"
                                                className="w-24"
                                                value={p.safety_stock_days}
                                                onChange={(e) => handleChange(p.policy_id, 'safety_stock_days', e.target.value)}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Input
                                                type="number"
                                                step="0.01"
                                                className="w-24"
                                                value={p.service_level_target}
                                                onChange={(e) => handleChange(p.policy_id, 'service_level_target', e.target.value)}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Button
                                                size="sm"
                                                disabled={savingId === p.policy_id}
                                                onClick={() => handleUpdate(p)}
                                            >
                                                {savingId === p.policy_id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            <Card className="border-red-200 bg-red-50">
                <CardHeader>
                    <CardTitle className="text-red-800 flex items-center gap-2">
                        <Trash2 className="w-5 h-5" />
                        System Maintenance (Danger Zone)
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-sm text-red-600">
                        <strong>Warning:</strong> Resetting transaction data will verify delete <strong>ALL</strong> Sales, Purchases, Opening Stock, and Planning history.
                        <br />
                        Master Data (Products, Customers, Settings) will be preserved.
                        <br />
                        Use this only if you want to start with a fresh slate (e.g., after testing).
                        <br />
                        <strong>This action cannot be undone. System Logs will also be truncated.</strong>
                    </p>
                    <Button
                        variant="destructive"
                        onClick={handleResetData}
                        disabled={loading}
                    >
                        {loading && savingId == -1 ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                        Reset All Transaction Data
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}
