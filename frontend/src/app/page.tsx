'use client';

import Link from "next/link";
import { useEffect, useState } from "react";
import { DashboardService, ActivityItem, DashboardKPI } from "../services/api";

export default function Home() {
  const [kpi, setKpi] = useState<DashboardKPI | null>(null);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        // Fetch KPI and Activity in parallel
        const [kpiRes, activityRes] = await Promise.allSettled([
          DashboardService.getSpendingAnalytics(),
          DashboardService.getRecentActivity()
        ]);

        if (kpiRes.status === 'fulfilled') {
          setKpi(kpiRes.value.data.kpi);
        }

        if (activityRes.status === 'fulfilled') {
          setActivities(activityRes.value.data);
        }

      } catch (err) {
        console.error("Failed to load dashboard data", err);
        setError("Failed to load data.");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-bg-subtle">
      {/* Header / Nav */}
      <header className="border-b border-border-subtle sticky top-0 bg-bg-elevated z-10 shadow-sm">
        <div className="container flex h-16 items-center justify-between">
          <div className="font-bold text-xl text-primary">PlanningPurchase</div>
          <nav className="hidden md:flex gap-6">
            <Link href="/" className="text-text-main hover:text-primary transition-colors font-medium">Dashboard</Link>
            <Link href="/planning" className="text-text-muted hover:text-primary transition-colors">Planning</Link>
            <Link href="/reports" className="text-text-muted hover:text-primary transition-colors">Reports</Link>
          </nav>
          <div className="flex items-center gap-4">
            {/* Simple User Avatar Placeholder */}
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-xs">
              AD
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 py-12">
        <div className="container">
          {/* Hero Section */}
          <section className="mb-10 text-center md:text-left">
            <h1 className="text-4xl text-text-heading font-bold mb-4">Dashboard Overview</h1>
            <p className="text-text-muted text-lg max-w-2xl">
              Welcome back. Here is your daily procurement and sales update.
            </p>
          </section>

          {/* Grid Layout */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Sidebar / Stats */}
            <div className="md:col-span-3 space-y-6">
              <div className="p-6 border border-border-subtle rounded-lg bg-bg-elevated shadow-sm hover:shadow-md transition-shadow">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-2">Total Spend</h3>
                {loading ? (
                  <div className="h-8 w-24 bg-bg-subtle rounded animate-pulse"></div>
                ) : (
                  <>
                    <p className="text-3xl font-bold text-text-main">
                      {kpi ? new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(kpi.total_spend) : '0 ₫'}
                    </p>
                    <p className="text-sm text-text-muted mt-1">{kpi?.total_plans || 0} active plans</p>
                  </>
                )}
              </div>
              <div className="p-6 border border-border-subtle rounded-lg bg-bg-elevated shadow-sm hover:shadow-md transition-shadow">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-2">Pending Approval</h3>
                {/* TODO: Fetch real Pending count */}
                <p className="text-3xl font-bold text-warning">0</p>
                <p className="text-sm text-text-muted mt-1">Requires attention</p>
              </div>
            </div>

            {/* Main Content Area */}
            <div className="md:col-span-9">
              <div className="p-6 border border-border-subtle rounded-lg bg-bg-elevated min-h-[400px] shadow-sm">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-text-heading">Recent Activity</h2>
                  <Link href="/planning">
                    <button className="px-4 py-2 bg-primary text-white rounded hover:bg-primary-hover transition-colors text-sm font-medium">
                      New Plan
                    </button>
                  </Link>
                </div>

                <div className="space-y-4">
                  {/* Table Header */}
                  <div className="grid grid-cols-12 gap-4 pb-2 border-b border-border-subtle text-sm font-semibold text-text-muted">
                    <div className="col-span-6 md:col-span-4">Plan / Order ID</div>
                    <div className="col-span-3 md:col-span-4">Status</div>
                    <div className="col-span-3 md:col-span-4 text-right">Amount</div>
                  </div>

                  {loading ? (
                    // Skeleton Loading
                    [1, 2, 3].map((i) => (
                      <div key={i} className="grid grid-cols-12 gap-4 py-3 items-center border-b border-border-subtle/50 last:border-0">
                        <div className="col-span-6 md:col-span-4 flex items-center gap-3">
                          <div className="w-8 h-8 rounded bg-bg-subtle animate-pulse"></div>
                          <div className="h-4 w-24 bg-bg-subtle rounded animate-pulse"></div>
                        </div>
                        <div className="col-span-3 md:col-span-4">
                          <div className="h-6 w-20 bg-bg-subtle rounded-full animate-pulse"></div>
                        </div>
                        <div className="col-span-3 md:col-span-4 text-right">
                          <div className="h-4 w-16 bg-bg-subtle rounded ml-auto animate-pulse"></div>
                        </div>
                      </div>
                    ))
                  ) : activities.length > 0 ? (
                    activities.map((item) => (
                      <div key={item.id} className="grid grid-cols-12 gap-4 py-3 items-center border-b border-border-subtle/50 last:border-0 hover:bg-bg-subtle/30 transition-colors">
                        <div className="col-span-6 md:col-span-4 flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary text-xs font-bold">
                            P
                          </div>
                          <div>
                            <p className="font-medium text-text-main">{item.order_id}</p>
                            <p className="text-xs text-text-muted">{item.sku_id}</p>
                          </div>
                        </div>
                        <div className="col-span-3 md:col-span-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium 
                                    ${item.status === 'APPROVED' ? 'bg-success/10 text-success' :
                              item.status === 'DRAFT' ? 'bg-warning/10 text-warning' : 'bg-bg-subtle text-text-muted'}`}>
                            {item.status}
                          </span>
                        </div>
                        <div className="col-span-3 md:col-span-4 text-right">
                          <p className="font-medium text-text-main">
                            {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: item.currency || 'VND' }).format(item.amount)}
                          </p>
                          <p className="text-xs text-text-muted">{item.date}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="py-8 text-center text-text-muted">
                      No recent activity found.
                    </div>
                  )}
                </div>

              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border-subtle py-8 mt-auto bg-bg-elevated">
        <div className="container text-center text-text-muted text-sm">
          &copy; 2025 Planning Purchase System. Internal Use Only.
        </div>
      </footer>
    </div>
  );
}
