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

    const tabs = [
        { name: "Products", href: "/dashboard/data/products" },
        { name: "Units", href: "/dashboard/data/units" },
        { name: "Product Groups", href: "/dashboard/data/groups" },
        { name: "Warehouses", href: "/dashboard/data/warehouses" },
        { name: "Inventory Snapshots", href: "/dashboard/data/inventory" },
        { name: "Vendors", href: "/dashboard/data/partners" },
        { name: "Customers", href: "/dashboard/data/customers" },
        { name: "Customer Groups", href: "/dashboard/data/partner-groups" },
    ]

    return (
        <div className="container py-8 space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-text-heading">Data Management</h1>
                <p className="text-text-muted">Centralized Master Data Management</p>
            </div>

            <div className="flex space-x-2 border-b border-border pb-2">
                {tabs.map((tab) => (
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
