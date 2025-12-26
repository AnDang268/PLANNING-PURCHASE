"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"

export function Navigation() {
    const pathname = usePathname()

    const isActive = (path: string) => {
        if (path === "/" && pathname === "/") return true
        if (path !== "/" && pathname?.startsWith(path)) return true
        return false
    }

    const linkClass = (path: string) => `text-sm font-medium transition-colors hover:text-primary ${isActive(path) ? "text-primary" : "text-muted-foreground"
        }`

    return (
        <header className="border-b border-border-subtle sticky top-0 bg-background/95 backdrop-blur z-50 shadow-sm">
            <div className="container flex h-16 items-center justify-between">
                <div className="flex items-center gap-8">
                    <Link href="/" className="font-bold text-xl text-primary">
                        PlanningPurchase
                    </Link>
                    <nav className="hidden md:flex gap-6">
                        <Link href="/" className={linkClass("/")}>
                            Dashboard
                        </Link>
                        <Link href="/planning" className={linkClass("/planning")}>
                            Planning
                        </Link>
                        {/* Dropdown for Data Data Management */}
                        <div className="relative group">
                            <Link href="/dashboard/data" className={`${linkClass("/dashboard/data")} flex items-center gap-1`}>
                                Data Management
                            </Link>
                            <div className="absolute top-full left-0 hidden group-hover:block w-48 bg-white border shadow-lg rounded-md overflow-hidden pt-2">
                                <Link href="/dashboard/data/products" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Products</Link>
                                <Link href="/dashboard/data/sales" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Sales Details</Link>
                                <Link href="/dashboard/data/purchases" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Purchase Details</Link>
                                <div className="border-t my-1"></div>
                                <Link href="/dashboard/data/units" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Units</Link>
                                <Link href="/dashboard/data/groups" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Product Groups</Link>
                                <Link href="/dashboard/data/warehouses" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Warehouses</Link>
                                <Link href="/dashboard/data/inventory" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Inventory Snapshots</Link>
                                <Link href="/dashboard/data/rolling-inventory" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Rolling Data</Link>
                                <div className="border-t my-1"></div>
                                <Link href="/dashboard/data/partners" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Vendors</Link>
                                <Link href="/dashboard/data/customers" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Customers</Link>
                                <Link href="/dashboard/data/partner-groups" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Customer Groups</Link>
                            </div>
                        </div>
                        <Link href="/reports" className={linkClass("/reports")}>
                            Reports
                        </Link>
                    </nav>
                </div>

                <div className="flex items-center gap-4">
                    <div className="relative group">
                        <button className="text-sm font-medium text-muted-foreground hover:text-primary flex items-center gap-1">
                            Settings
                        </button>
                        <div className="absolute top-full right-0 hidden group-hover:block w-48 bg-white border shadow-lg rounded-md overflow-hidden pt-2 z-50">
                            <div className="flex flex-col">
                                <Link href="/dashboard/settings/database" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">Database Connection</Link>
                                <Link href="/dashboard/integrations" className="px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">MISA Integrations</Link>
                            </div>
                        </div>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-xs">
                        AD
                    </div>
                </div>
            </div>
        </header>
    )
}
