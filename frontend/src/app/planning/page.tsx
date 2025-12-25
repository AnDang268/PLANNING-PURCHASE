'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { PlanningService, PurchasePlan } from '../../services/api';

export default function PlanningPage() {
    const [plans, setPlans] = useState<PurchasePlan[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    const fetchPlans = async () => {
        setLoading(true);
        const result = await PlanningService.getPlans();
        if (result && result.data) {
            setPlans(result.data);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchPlans();
    }, []);

    const handleGeneratePlans = async () => {
        setGenerating(true);
        try {
            await PlanningService.generatePlans();
            // Refresh list
            await fetchPlans();
        } catch (e) {
            alert("Failed to generate plans");
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col bg-bg-subtle">
            <header className="border-b border-border-subtle sticky top-0 bg-bg-elevated z-10 shadow-sm">
                <div className="container flex h-16 items-center justify-between">
                    <div className="font-bold text-xl text-primary">PlanningPurchase</div>
                    <nav className="hidden md:flex gap-6">
                        <Link href="/" className="text-text-muted hover:text-primary transition-colors">Dashboard</Link>
                        <Link href="/planning" className="text-text-main hover:text-primary transition-colors font-medium">Planning</Link>
                        <Link href="/reports" className="text-text-muted hover:text-primary transition-colors">Reports</Link>
                    </nav>
                    <div className="flex items-center gap-4">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-xs">
                            AD
                        </div>
                    </div>
                </div>
            </header>

            <main className="flex-1 py-12">
                <div className="container">
                    <div className="flex items-center justify-between mb-8">
                        <h1 className="text-3xl font-bold text-text-heading">Purchase Planning</h1>
                        <div className="flex gap-4">
                            <button
                                onClick={handleGeneratePlans}
                                disabled={generating}
                                className="px-4 py-2 bg-secondary text-secondary-foreground rounded hover:bg-secondary/80 transition-colors text-sm font-medium disabled:opacity-50">
                                {generating ? 'Generating...' : 'Run Planning Engine'}
                            </button>
                            <button className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-hover transition-colors text-sm font-medium">
                                Create Manual Plan
                            </button>
                        </div>
                    </div>

                    <div className="bg-bg-elevated border border-border-subtle rounded-lg shadow-sm overflow-hidden">
                        {loading ? (
                            <div className="p-8 text-center text-text-muted">Loading plans...</div>
                        ) : plans.length === 0 ? (
                            <div className="p-12 text-center flex flex-col items-center justify-center">
                                <p className="text-text-muted mb-4">No purchase plans found.</p>
                                <button onClick={handleGeneratePlans} className="text-primary hover:underline text-sm">
                                    Generate suggestions based on demand
                                </button>
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left">
                                    <thead className="bg-bg-subtle text-text-muted font-semibold border-b border-border-subtle">
                                        <tr>
                                            <th className="px-6 py-3">Plan ID</th>
                                            <th className="px-6 py-3">Date</th>
                                            <th className="px-6 py-3">SKU</th>
                                            <th className="px-6 py-3">Vendor</th>
                                            <th className="px-6 py-3 text-right">Qty</th>
                                            <th className="px-6 py-3 text-right">Amount</th>
                                            <th className="px-6 py-3">Status</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-border-subtle">
                                        {plans.map((plan) => (
                                            <tr key={plan.id} className="hover:bg-bg-subtle/50 transition-colors">
                                                <td className="px-6 py-3 font-medium text-text-main">
                                                    #{plan.id}
                                                </td>
                                                <td className="px-6 py-3 text-text-muted">{plan.plan_date}</td>
                                                <td className="px-6 py-3 text-text-main font-medium">{plan.sku_id}</td>
                                                <td className="px-6 py-3 text-text-muted">{plan.vendor_id || '-'}</td>
                                                <td className="px-6 py-3 text-right font-mono text-text-main">
                                                    {plan.final_quantity ? plan.final_quantity.toLocaleString() : plan.suggested_quantity?.toLocaleString()}
                                                </td>
                                                <td className="px-6 py-3 text-right font-mono text-text-main">
                                                    {plan.total_amount?.toLocaleString()} ₫
                                                </td>
                                                <td className="px-6 py-3">
                                                    <span className={`px-2 py-1 rounded text-xs font-medium 
                                            ${plan.status === 'APPROVED' ? 'bg-success/10 text-success' :
                                                            plan.status === 'DRAFT' ? 'bg-warning/10 text-warning' : 'bg-bg-subtle text-text-muted'}`}>
                                                        {plan.status}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
