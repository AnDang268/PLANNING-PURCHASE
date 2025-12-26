"use client"

import { useState, useEffect, useRef } from "react"
import { StandardDataTable, ColumnDef } from "@/components/StandardDataTable"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { API_BASE_URL } from "@/config"
import { useToast } from "@/components/ui/use-toast"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { CheckCircle2, Edit, Download, FileSpreadsheet, Upload, Check, ChevronsUpDown } from "lucide-react"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from "@/components/ui/command"
import { cn } from "@/lib/utils"

interface PurchasePlan {
    id: number
    plan_date: string
    sku_id: string
    vendor_id: string | null
    suggested_quantity: number
    final_quantity: number
    total_amount: number
    status: string
    notes: string
}

export default function PurchasePlansPage() {
    const [data, setData] = useState<PurchasePlan[]>([])
    const [loading, setLoading] = useState(true)
    const { toast } = useToast()

    // Filters
    const [groups, setGroups] = useState<{ group_id: string, group_name: string }[]>([])
    const [selectedGroup, setSelectedGroup] = useState<string>("ALL")
    const [search, setSearch] = useState("")

    // Edit State
    const [editingPlan, setEditingPlan] = useState<PurchasePlan | null>(null)
    const [newQty, setNewQty] = useState<number>(0)
    const [newNotes, setNewNotes] = useState<string>("")
    const [isSaving, setIsSaving] = useState(false)

    // Import Ref
    const fileInputRef = useRef<HTMLInputElement>(null)

    // Load Groups on Mount
    useEffect(() => {
        fetch(`${API_BASE_URL}/api/data/groups`)
            .then(res => res.json())
            .then(data => setGroups(Array.isArray(data) ? data : []))
            .catch(err => console.error(err))
    }, [])

    const fetchPlans = async () => {
        setLoading(true)
        try {
            let url = `${API_BASE_URL}/api/planning/plans?limit=100`
            if (search) url += `&search=${encodeURIComponent(search)}`
            if (selectedGroup && selectedGroup !== 'ALL') url += `&group_id=${selectedGroup}`

            const res = await fetch(url)
            const json = await res.json()
            setData(json.data || [])
        } catch (e) {
            console.error(e)
            toast({
                title: "Error",
                description: "Failed to fetch plans",
                variant: "destructive"
            })
        } finally {
            setLoading(false)
        }
    }

    // De-bounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchPlans()
        }, 500)
        return () => clearTimeout(timer)
    }, [search, selectedGroup])

    const generatePlans = async () => {
        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/planning/generate-plans`, { method: "POST" })
            if (res.ok) {
                toast({ title: "Success", description: "Purchase plans generated successfully" })
                fetchPlans()
            } else {
                throw new Error("Failed")
            }
        } catch (e) {
            toast({ title: "Error", description: "Transformation failed", variant: "destructive" })
            setLoading(false)
        }
    }

    const handleApprove = async (plan: PurchasePlan) => {
        if (!confirm(`Approve plan for ${plan.sku_id}? This will lock the plan.`)) return

        try {
            const res = await fetch(`${API_BASE_URL}/api/planning/plans/approve`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ plan_id: plan.id })
            })
            if (res.ok) {
                toast({ title: "Approved", description: `Plan #${plan.id} approved.` })
                fetchPlans()
            }
        } catch (e) {
            toast({ title: "Error", description: "Failed to approve", variant: "destructive" })
        }
    }

    const startEdit = (plan: PurchasePlan) => {
        setEditingPlan(plan)
        setNewQty(plan.final_quantity)
        setNewNotes(plan.notes || "")
    }

    const saveEdit = async () => {
        if (!editingPlan) return
        setIsSaving(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/planning/plans/update`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    plan_id: editingPlan.id,
                    final_quantity: newQty,
                    notes: newNotes
                })
            })
            if (res.ok) {
                toast({ title: "Updated", description: "Plan updated successfully." })
                setEditingPlan(null)
                fetchPlans()
            } else {
                throw new Error("Failed")
            }
        } catch (e) {
            toast({ title: "Error", description: "Failed to update plan", variant: "destructive" })
        } finally {
            setIsSaving(false)
        }
    }

    const handleExport = () => {
        let url = `${API_BASE_URL}/api/planning/plans/export?pending_only=false`
        if (search) url += `&search=${encodeURIComponent(search)}`
        if (selectedGroup && selectedGroup !== 'ALL') url += `&group_id=${selectedGroup}`
        window.open(url, '_blank')
    }

    const handleImportClick = () => {
        fileInputRef.current?.click()
    }

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        const formData = new FormData()
        formData.append("file", file)

        setLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/planning/plans/import`, {
                method: "POST",
                body: formData
            })
            if (res.ok) {
                const json = await res.json()
                toast({ title: "Success", description: `Imported ${json.imported_count} plans.` })
                fetchPlans()
            } else {
                toast({ title: "Error", description: "Import failed", variant: "destructive" })
            }
        } catch (error) {
            toast({ title: "Error", description: "Upload error", variant: "destructive" })
        } finally {
            setLoading(false)
            if (fileInputRef.current) fileInputRef.current.value = ""
        }
    }

    const columns: ColumnDef<PurchasePlan>[] = [
        { header: "Date", accessorKey: "plan_date" },
        { header: "SKU", accessorKey: "sku_id", className: "font-medium" },
        { header: "Suggested", accessorKey: "suggested_quantity", cell: (item) => Math.round(item.suggested_quantity).toLocaleString() },
        {
            header: "Final Qty",
            accessorKey: "final_quantity",
            cell: (item) => (
                <span className={item.final_quantity !== item.suggested_quantity ? "text-primary font-bold" : ""}>
                    {Math.round(item.final_quantity).toLocaleString()}
                </span>
            )
        },
        {
            header: "Status",
            accessorKey: "status",
            cell: (item) => (
                <Badge variant={item.status === 'APPROVED' ? "default" : "secondary"}>
                    {item.status}
                </Badge>
            )
        },
        { header: "Notes", accessorKey: "notes", className: "max-w-[200px] truncate" },
        {
            header: "Actions",
            cell: (item) => (
                <div className="flex gap-2">
                    {item.status !== 'APPROVED' && (
                        <>
                            <Button size="sm" variant="outline" onClick={() => startEdit(item)}>
                                <Edit className="w-4 h-4 mr-1" /> Edit
                            </Button>
                            <Button size="sm" onClick={() => handleApprove(item)}>
                                <CheckCircle2 className="w-4 h-4 mr-1" /> Approve
                            </Button>
                        </>
                    )}
                </div>
            )
        }
    ]

    return (
        <div className="space-y-4 py-6 container">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-text-heading">Purchase Recommendation Plans</h1>
                    <p className="text-text-muted">Review and approve system-generated purchase orders.</p>
                </div>
                <div className="flex gap-2">
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        className="hidden"
                        accept=".xlsx, .xls, .csv"
                    />
                    <Button variant="outline" onClick={handleImportClick}>
                        <Upload className="mr-2 h-4 w-4" />
                        Import Excel
                    </Button>
                    <Button variant="outline" onClick={handleExport}>
                        <FileSpreadsheet className="mr-2 h-4 w-4 text-green-600" />
                        Export Excel
                    </Button>
                    <Button onClick={generatePlans}>
                        Sync Plans
                    </Button>
                </div>
            </div>

            <div className="flex gap-4 items-center">
                <div className="w-[300px]">
                    <Label className="mb-1 block text-xs">Product Group</Label>
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button
                                variant="outline"
                                role="combobox"
                                className={cn(
                                    "w-full justify-between",
                                    !selectedGroup && "text-muted-foreground"
                                )}
                            >
                                {selectedGroup !== "ALL"
                                    ? groups.find((g) => g.group_id === selectedGroup)?.group_name
                                    : "All Groups"}
                                <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-[300px] p-0">
                            <Command>
                                <CommandInput placeholder="Search group..." />
                                <CommandEmpty>No group found.</CommandEmpty>
                                <CommandGroup className="max-h-[300px] overflow-auto">
                                    <CommandItem
                                        value="ALL"
                                        onSelect={() => {
                                            setSelectedGroup("ALL")
                                        }}
                                    >
                                        <Check
                                            className={cn(
                                                "mr-2 h-4 w-4",
                                                selectedGroup === "ALL" ? "opacity-100" : "opacity-0"
                                            )}
                                        />
                                        All Groups
                                    </CommandItem>
                                    {groups.map((g) => (
                                        <CommandItem
                                            key={g.group_id}
                                            value={g.group_name}
                                            onSelect={() => {
                                                setSelectedGroup(g.group_id)
                                            }}
                                        >
                                            <Check
                                                className={cn(
                                                    "mr-2 h-4 w-4",
                                                    selectedGroup === g.group_id ? "opacity-100" : "opacity-0"
                                                )}
                                            />
                                            {g.group_name}
                                        </CommandItem>
                                    ))}
                                </CommandGroup>
                            </Command>
                        </PopoverContent>
                    </Popover>
                </div>
                <div className="w-[300px]">
                    <Label className="mb-1 block text-xs">Search SKU</Label>
                    <Input
                        placeholder="Search SKU..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
            </div>

            <StandardDataTable
                title=""
                description=""
                data={data}
                columns={columns}
                searchKey="sku_id"
                onSync={undefined}
            />

            <Dialog open={!!editingPlan} onOpenChange={(open) => !open && setEditingPlan(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Edit Plan for {editingPlan?.sku_id}</DialogTitle>
                        <DialogDescription>Adjust quantity or add notes before approval.</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-2">
                        <div className="space-y-2">
                            <Label>Suggested Quantity</Label>
                            <Input disabled value={Math.round(editingPlan?.suggested_quantity || 0)} />
                        </div>
                        <div className="space-y-2">
                            <Label>Final Quantity</Label>
                            <Input
                                type="number"
                                value={newQty}
                                onChange={(e) => setNewQty(parseFloat(e.target.value))}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Notes</Label>
                            <Textarea
                                value={newNotes}
                                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNewNotes(e.target.value)}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setEditingPlan(null)}>Cancel</Button>
                        <Button onClick={saveEdit} disabled={isSaving}>
                            {isSaving ? "Saving..." : "Save Changes"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
