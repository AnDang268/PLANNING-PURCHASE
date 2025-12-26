
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Activity, Database, Server, RefreshCw, CheckCircle2, XCircle } from "lucide-react"
import { API_BASE_URL } from "@/config"

export default function DatabaseCheckPage() {
    const [status, setStatus] = useState<"loading" | "healthy" | "unhealthy">("loading")
    const [details, setDetails] = useState<any>(null)
    const [lastChecked, setLastChecked] = useState<string>("")
    const [isEditing, setIsEditing] = useState(false)
    const [configForm, setConfigForm] = useState({
        db_server: "",
        db_name: "",
        username: "",
        password: ""
    })
    const [saving, setSaving] = useState(false)

    // Sync Manager State
    const [isSyncing, setIsSyncing] = useState(false)
    const [syncSelection, setSyncSelection] = useState({
        units: false,
        groups: false,
        warehouses: false,
        partners: false, // Vendors
        customers: false,
        customer_groups: false,
        products: false
    })

    const handleMasterSync = async () => {
        setIsSyncing(true)
        try {
            const selectedTypes = Object.entries(syncSelection)
                .filter(([_, selected]) => selected)
                .map(([type]) => type)

            if (selectedTypes.length === 0) return

            alert(`Starting sync for: ${selectedTypes.join(", ")}`)

            // Process sequentially to be safe, or parallel
            // Deduplicate: partners, customers, customer_groups all map to 'partners' endpoint
            const endpointsToCall = new Set<string>()

            selectedTypes.forEach(type => {
                if (type === 'partners' || type === 'customers' || type === 'customer_groups') {
                    endpointsToCall.add('partners')
                } else {
                    endpointsToCall.add(type)
                }
            })

            // Process sequentially
            for (const endpoint of Array.from(endpointsToCall)) {
                await fetch(`${API_BASE_URL}/api/data/sync/${endpoint}`, { method: "POST" })
            }

            alert("Sync requests sent!")
        } catch (e) {
            alert("Sync failed to start")
        } finally {
            setIsSyncing(false)
        }
    }

    const checkHealth = async () => {
        setStatus("loading")
        try {
            const res = await fetch(`${API_BASE_URL}/api/system/health`)
            const data = await res.json()

            if (data.status === "healthy") {
                setStatus("healthy")
                setDetails(data.details.database)
                setConfigForm({
                    ...configForm,
                    db_name: data.details.database.name,
                    // Cannot retrieve password
                })
            } else {
                setStatus("unhealthy")
                setDetails(data.details.database)
            }
            setLastChecked(data.timestamp)
        } catch (error) {
            setStatus("unhealthy")
            setDetails({ error: "Failed to connect to backend API" })
            setLastChecked(new Date().toLocaleString())
        }
    }

    const handleSaveConfig = async () => {
        setSaving(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/system/config/database`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(configForm)
            })
            if (res.ok) {
                alert("Configuration Saved & Reloaded!")
                setIsEditing(false)
                checkHealth()
            } else {
                const err = await res.json()
                alert(`Failed: ${err.detail}`)
            }
        } catch (error) {
            alert("Failed: Network Error")
        } finally {
            setSaving(false)
        }
    }

    useEffect(() => {
        checkHealth()
    }, [])

    return (
        <div className="container py-8 space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-text-heading">Database Status</h1>
                    <p className="text-text-muted">Verify connection to SQL Server and system health.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setIsEditing(!isEditing)}>
                        {isEditing ? "Cancel" : "Edit Connection"}
                    </Button>
                    <Button onClick={checkHealth} disabled={status === "loading"}>
                        <RefreshCw className={`mr-2 h-4 w-4 ${status === "loading" ? "animate-spin" : ""}`} />
                        Test Connection
                    </Button>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Connection Status</CardTitle>
                        <Activity className="h-4 w-4 text-text-muted" />
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-2 mt-2">
                            {status === "loading" && <span className="text-xs border px-2 py-0.5 rounded-full">Checking...</span>}
                            {status === "healthy" && (
                                <>
                                    <CheckCircle2 className="h-5 w-5 text-success" />
                                    <span className="text-2xl font-bold text-success">Online</span>
                                </>
                            )}
                            {status === "unhealthy" && (
                                <>
                                    <XCircle className="h-5 w-5 text-danger" />
                                    <span className="text-2xl font-bold text-danger">Offline</span>
                                </>
                            )}
                        </div>
                        <p className="text-xs text-text-muted mt-2">
                            Last Checked: {lastChecked}
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Latency</CardTitle>
                        <Activity className="h-4 w-4 text-text-muted" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold mt-2">
                            {details?.latency_ms ? `${details.latency_ms} ms` : "--"}
                        </div>
                        <p className="text-xs text-text-muted mt-1">
                            Round-trip time to SQL Server
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Configuration</CardTitle>
                        <Database className="h-4 w-4 text-text-muted" />
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-1 mt-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-text-muted">Database:</span>
                                <span className="font-medium">{details?.name || "--"}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-text-muted">Server:</span>
                                <span className="font-medium">{details?.server || "--"}</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {isEditing && (
                <Card className="border-primary/50 bg-primary/5">
                    <CardHeader>
                        <CardTitle>Update Connection Details</CardTitle>
                        <CardDescription>
                            Enter new SQL Server credentials. These will be saved to your local .env file.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Server Address</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                    placeholder="localhost"
                                    value={configForm.db_server}
                                    onChange={(e) => setConfigForm({ ...configForm, db_server: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Database Name</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                    placeholder="PlanningPurchaseDB"
                                    value={configForm.db_name}
                                    onChange={(e) => setConfigForm({ ...configForm, db_name: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Username</label>
                                <input
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                    placeholder="sa"
                                    value={configForm.username}
                                    onChange={(e) => setConfigForm({ ...configForm, username: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Password</label>
                                <input
                                    type="password"
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                    placeholder="Enter new password"
                                    value={configForm.password}
                                    onChange={(e) => setConfigForm({ ...configForm, password: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="flex justify-end pt-4">
                            <Button onClick={handleSaveConfig} disabled={saving}>
                                {saving && <RefreshCw className="mr-2 h-4 w-4 animate-spin" />}
                                Save & Reconnect
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}


            {status === "unhealthy" && (
                <Card className="border-danger/50 bg-danger/10">
                    <CardHeader>
                        <CardTitle className="text-danger flex items-center gap-2">
                            <AlertCircle className="h-5 w-5" />
                            Connection Error
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="font-mono text-sm text-danger">
                            {details?.error || "Unknown Error"}
                        </p>
                    </CardContent>
                </Card>
            )}

            {/* Sync Manager Section */}
            <div className="grid gap-4 md:grid-cols-1">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <RefreshCw className="h-5 w-5" />
                            Sync Manager
                        </CardTitle>
                        <CardDescription>
                            Select specific data categories to synchronize from MISA AMIS.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                            {['units', 'groups', 'warehouses', 'partners', 'customers', 'customer_groups', 'products'].map((type) => (
                                <div key={type} className="flex items-center space-x-2 border p-4 rounded-md bg-muted/50">
                                    <input
                                        type="checkbox"
                                        id={type}
                                        className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                        checked={syncSelection[type as keyof typeof syncSelection]}
                                        onChange={(e) => setSyncSelection(prev => ({ ...prev, [type]: e.target.checked }))}
                                    />
                                    <Label htmlFor={type} className="capitalize cursor-pointer font-medium">
                                        {type}
                                    </Label>
                                </div>
                            ))}
                        </div>
                        <div className="flex justify-end gap-2">
                            <Button
                                variant="outline"
                                onClick={() => setSyncSelection({
                                    units: true, groups: true, warehouses: true, partners: true, customers: true, customer_groups: true, products: true
                                })}
                            >
                                Select All
                            </Button>
                            <Button
                                onClick={handleMasterSync}
                                disabled={isSyncing || !Object.values(syncSelection).some(Boolean)}
                            >
                                {isSyncing ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                                {isSyncing ? "Syncing..." : "Sync Selected"}
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card className="border-danger">
                <CardHeader>
                    <CardTitle className="text-danger flex items-center gap-2">
                        <Trash2 className="h-5 w-5" />
                        Maintenance Operations
                    </CardTitle>
                    <CardDescription>
                        Dangerous actions that affect system data.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-between p-4 border border-danger/20 rounded-lg bg-danger/5">
                        <div className="space-y-1">
                            <h4 className="text-sm font-medium text-danger">Reset System Data</h4>
                            <p className="text-xs text-text-muted">
                                Performs a hard delete of ALL Products, Vendors, and Plans. Settings are preserved.
                            </p>
                        </div>
                        <Button variant="destructive" onClick={async () => {
                            if (confirm("ARE YOU SURE? This will wipe all master data and plans. This action cannot be undone.")) {
                                try {
                                    const res = await fetch(`${API_BASE_URL}/api/data/reset`, { method: "DELETE" })
                                    if (res.ok) {
                                        alert("System Reset Complete. You can now re-sync data.")
                                    } else {
                                        const err = await res.json()
                                        alert(`Reset Failed: ${err.detail}`)
                                    }
                                } catch (e) { alert("Network Error") }
                            }
                        }}>
                            Purge Data
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

function AlertCircle({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
    )
}

function Trash2({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <path d="M3 6h18" />
            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
            <line x1="10" y1="11" x2="10" y2="17" />
            <line x1="14" y1="11" x2="14" y2="17" />
        </svg>
    )
}
