import Link from "next/link";

export default function ReportsPage() {
    return (
        <div className="min-h-screen flex flex-col bg-bg-subtle">
            <header className="border-b border-border-subtle sticky top-0 bg-bg-elevated z-10 shadow-sm">
                <div className="container flex h-16 items-center justify-between">
                    <div className="font-bold text-xl text-primary">PlanningPurchase</div>
                    <nav className="hidden md:flex gap-6">
                        <Link href="/" className="text-text-muted hover:text-primary transition-colors">Dashboard</Link>
                        <Link href="/planning" className="text-text-muted hover:text-primary transition-colors">Planning</Link>
                        <Link href="/reports" className="text-text-main hover:text-primary transition-colors font-medium">Reports</Link>
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
                    <h1 className="text-3xl font-bold text-text-heading mb-8">Reports & Analytics</h1>
                    <div className="p-6 border border-border-subtle rounded-lg bg-bg-elevated shadow-sm">
                        <p className="text-text-muted">Reporting module coming soon.</p>
                    </div>
                </div>
            </main>
        </div>
    );
}
