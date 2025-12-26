"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"

export default function PlanningLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const pathname = usePathname()

    const tabs = [
        { name: "Purchase Plans", href: "/dashboard/planning/purchase-plans" },
        { name: "Demand Forecast", href: "/dashboard/planning/forecast" },
        { name: "Rolling Forecast", href: "/dashboard/planning/rolling" },
    ]

    return (
        <div className="container py-8 space-y-8">
            {/* Header Removed */}

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
