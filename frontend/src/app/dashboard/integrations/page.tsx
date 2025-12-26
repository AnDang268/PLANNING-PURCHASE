"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { API_BASE_URL } from "@/config"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Loader2, RefreshCw, Save, CheckCircle, AlertTriangle, Eye, EyeOff } from "lucide-react"

export default function CrmSyncPage() {
    const [loading, setLoading] = useState(false)
    const [syncing, setSyncing] = useState(false)

    // CRM Config State
    const [clientId, setClientId] = useState("")
    const [showClientId, setShowClientId] = useState(false)
    const [clientSecret, setClientSecret] = useState("")
    const [showClientSecret, setShowClientSecret] = useState(false)
    const [companyCode, setCompanyCode] = useState("") // New

    // Accounting Config State
    const [actAppId, setActAppId] = useState("")
    const [actAccessCode, setActAccessCode] = useState("")
    const [showAccessCode, setShowAccessCode] = useState(false)
    const [actBaseUrl, setActBaseUrl] = useState("")

    const [configSaved, setConfigSaved] = useState(false)

    // Load initial config
    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/data/crm/config`)
                if (res.ok) {
                    const data = await res.json()
                    // CRM
                    if (data.MISA_CRM_CLIENT_ID) setClientId(data.MISA_CRM_CLIENT_ID)
                    if (data.MISA_CRM_CLIENT_SECRET) setClientSecret(data.MISA_CRM_CLIENT_SECRET)
                    if (data.company_code) setCompanyCode(data.company_code) // Load company code

                    // Accounting
                    if (data.MISA_AMIS_ACT_APP_ID) setActAppId(data.MISA_AMIS_ACT_APP_ID)
                    if (data.MISA_AMIS_ACT_ACCESS_CODE) setActAccessCode(data.MISA_AMIS_ACT_ACCESS_CODE)
                    if (data.MISA_AMIS_ACT_BASE_URL) setActBaseUrl(data.MISA_AMIS_ACT_BASE_URL)
                }
            } catch (e) {
                console.error("Failed to load config", e)
            }
        }
        fetchConfig()
    }, [])

    const handleSaveConfig = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/crm/config`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    "MISA_CRM_CLIENT_ID": clientId,
                    "MISA_CRM_CLIENT_SECRET": clientSecret,
                    "company_code": companyCode, // Save company code
                    "MISA_AMIS_ACT_APP_ID": actAppId,
                    "MISA_AMIS_ACT_ACCESS_CODE": actAccessCode,
                    "MISA_AMIS_ACT_BASE_URL": actBaseUrl
                })
            })
            if (res.ok) {
                setConfigSaved(true)
                setTimeout(() => setConfigSaved(false), 3000)
            } else {
                alert("Failed to save configuration")
            }
        } catch (e) {
            alert("Network Error saving config")
        } finally {
            setLoading(false)
        }
    }

    const handleSync = async () => {
        if (!confirm("Start syncing Inventory from MISA CRM? This may take a few minutes.")) return

        setSyncing(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/sync/crm`, { method: "POST" })
            if (res.ok) {
                alert("Sync Started in Background")
            } else {
                alert("Failed to start sync")
            }
        } catch (e) {
            alert("Network Error starting sync")
        } finally {
            setSyncing(false)
        }
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">MISA Integrations</h2>
                <p className="text-muted-foreground">Manage connections to MISA AMIS CRM (V2) and Accounting (V1).</p>
            </div>

            <Separator />

            <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-6">
                    {/* CRM V2 CARD */}
                    <Card>
                        <CardHeader>
                            <CardTitle>MISA CRM V2 (Inventory)</CardTitle>
                            <CardDescription>
                                Required for fetching <strong>Product Ledger</strong> and Stocks.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label>Client ID</Label>
                                <div className="relative">
                                    <Input
                                        value={clientId}
                                        onChange={e => setClientId(e.target.value)}
                                        placeholder="Enter Client ID"
                                        type={showClientId ? "text" : "password"}
                                        className="pr-10"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowClientId(!showClientId)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-primary transition-colors"
                                    >
                                        {showClientId ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                    </button>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label>Client Secret</Label>
                                <div className="relative">
                                    <Input
                                        value={clientSecret}
                                        onChange={e => setClientSecret(e.target.value)}
                                        placeholder="Enter Client Secret"
                                        type={showClientSecret ? "text" : "password"}
                                        className="pr-10"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowClientSecret(!showClientSecret)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-primary transition-colors"
                                    >
                                        {showClientSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                    </button>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label>Company Code (Tenant ID)</Label>
                                <Input
                                    value={companyCode}
                                    onChange={e => setCompanyCode(e.target.value)}
                                    placeholder="e.g. kiethanhtin or x-tenantid"
                                />
                                <p className="text-xs text-muted-foreground">Required by MISA CRM V2 API.</p>
                            </div>
                        </CardContent>
                    </Card>

                    {/* ACCOUNTING V1 CARD */}
                    <Card>
                        <CardHeader>
                            <CardTitle>MISA Accounting (Master Data)</CardTitle>
                            <CardDescription>
                                Required for syncing Partners, Products, and Units.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label>App ID (Accounting)</Label>
                                <Input
                                    value={actAppId}
                                    onChange={e => setActAppId(e.target.value)}
                                    placeholder="e.g. 04991a48..."
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Access Code</Label>
                                <div className="relative">
                                    <Input
                                        value={actAccessCode}
                                        onChange={e => setActAccessCode(e.target.value)}
                                        placeholder="Long secret string..."
                                        type={showAccessCode ? "text" : "password"}
                                        className="pr-10"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowAccessCode(!showAccessCode)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-primary transition-colors"
                                    >
                                        {showAccessCode ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                    </button>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label>Base URL</Label>
                                <Input
                                    value={actBaseUrl}
                                    onChange={e => setActBaseUrl(e.target.value)}
                                    placeholder="https://actapp.misa.vn"
                                />
                            </div>
                        </CardContent>
                    </Card>

                    <Button onClick={handleSaveConfig} disabled={loading} className="w-full">
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {configSaved ? <CheckCircle className="mr-2 h-4 w-4 text-green-500" /> : <Save className="mr-2 h-4 w-4" />}
                        {configSaved ? "All Settings Saved!" : "Save All Configurations"}
                    </Button>
                </div>

                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Sync Operations</CardTitle>
                            <CardDescription>
                                Trigger manual synchronization.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="rounded-md border p-4 bg-blue-50 text-blue-900 border-blue-200">
                                <div className="flex items-center gap-2 font-semibold">
                                    <AlertTriangle className="h-4 w-4" />
                                    CRM Inventory Sync
                                </div>
                                <div className="text-sm mt-1">
                                    Syncs <strong>Product Ledger</strong> into <code>Fact_Inventory_Snapshots</code>.
                                </div>
                            </div>

                            <Button
                                className="w-full"
                                size="lg"
                                onClick={handleSync}
                                disabled={syncing || (!clientId && !clientSecret)}
                            >
                                {syncing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                                Sync CRM Inventory Now
                            </Button>

                            <Separator className="my-4" />

                            <div className="text-sm text-muted-foreground">
                                * To sync Accounting Data (Products, Partners), go to
                                <a href="/dashboard/data" className="text-blue-600 hover:underline ml-1">Data Management</a>.
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
