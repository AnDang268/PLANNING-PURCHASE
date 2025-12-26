"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function PlanningIndexPage() {
    const router = useRouter()

    useEffect(() => {
        router.push("/dashboard/planning/purchase-plans")
    }, [])

    return (
        <div className="flex h-[200px] items-center justify-center">
            <p className="text-muted-foreground">Redirecting to Purchase Plans...</p>
        </div>
    )
}
