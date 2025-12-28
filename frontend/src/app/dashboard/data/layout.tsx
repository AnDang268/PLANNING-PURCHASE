"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"

export default function DataLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const pathname = usePathname()

    const masterDataTabs = [
        { name: "Products", href: "/dashboard/data/products" },
        { name: "Units", href: "/dashboard/data/units" },
        { name: "Product Groups", href: "/dashboard/data/groups" },
        { name: "Warehouses", href: "/dashboard/data/warehouses" },
        { name: "Vendors", href: "/dashboard/data/partners" },
        { name: "Customers", href: "/dashboard/data/customers" },
        { name: "Customer Groups", href: "/dashboard/data/partner-groups" },
    ]

    const transactionTabs = [
        { name: "Sales Details", href: "/dashboard/data/sales" },
        { name: "Purchase Details", href: "/dashboard/data/purchases" },
        { name: "Opening Stock", href: "/dashboard/data/inventory" },
        { name: "Realtime Snapshots", href: "/dashboard/data/snapshots" },
    ]

    // Determine which set of tabs to show
    const isTransactionPage = transactionTabs.some(t => pathname.startsWith(t.href))
    const isMasterDataPage = masterDataTabs.some(t => pathname.startsWith(t.href))

    // Default to Master Data only if explicitly matched or fallback (but careful with fallback)
    // If we are on a route that is neither (e.g. root /dashboard/data), defaulting to Master Data is safe-ish.

    let currentTabs = masterDataTabs
    let sectionTitle = "Master Data"

    if (isTransactionPage) {
        currentTabs = transactionTabs
        sectionTitle = "Data Management"
    } else if (isMasterDataPage) {
        currentTabs = masterDataTabs
        sectionTitle = "Master Data"
    } else {
        // Fallback or specific logic for root /dashboard/data?
        // Let's assume Master Data as default for /dashboard/data root if needed, 
        // but typically user navigates to a subpage.
        currentTabs = masterDataTabs
    }

    return (
        <div className="container py-8 space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-text-heading">{sectionTitle}</h1>
                <p className="text-text-muted">Centralized Master Data Management</p>
            </div>

            <div className="flex space-x-2 border-b border-border pb-2 overflow-x-auto whitespace-nowrap scrollbar-hide">
                {currentTabs.map((tab) => (
                    <Link
                        key={tab.href}
                        href={tab.href}
                        className={cn(
                            buttonVariants({ variant: pathname.startsWith(tab.href) ? "secondary" : "ghost" }),
                            "dark:text-white"
                        )}
                    >
                        {tab.name}
                    </Link>
                ))}
            </div>

            <div className="min-h-[400px]">
                {children}
            </div>
        </div>
    )
}
