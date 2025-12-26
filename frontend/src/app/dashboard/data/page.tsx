"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function DataManagementPage() {
    const router = useRouter()

    useEffect(() => {
        router.push("/dashboard/data/products")
    }, []) // eslint-disable-line react-hooks/exhaustive-deps

    return (
        <div className="flex h-[200px] items-center justify-center">
            <p className="text-muted-foreground">Redirecting to Products...</p>
        </div>
    )
}
