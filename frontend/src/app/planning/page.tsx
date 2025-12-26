"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function PlanningRootPage() {
    const router = useRouter()

    useEffect(() => {
        router.push("/dashboard/planning")
    }, [])

    return (
        <div className="flex h-[200px] items-center justify-center">
            <p className="text-muted-foreground">Redirecting to Planning Dashboard...</p>
        </div>
    )
}
