"use client"

import * as React from "react"
import { Check, ChevronsUpDown, X } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { Badge } from "@/components/ui/badge"
import { API_BASE_URL } from "@/config"

export interface ProductMultiSelectProps {
    value: string[];
    onChange: (val: string[]) => void;
}

export function ProductMultiSelect({ value, onChange }: ProductMultiSelectProps) {
    const [open, setOpen] = React.useState(false)
    const [query, setQuery] = React.useState("")
    const [options, setOptions] = React.useState<{ sku_id: string, product_name: string }[]>([])
    const [loading, setLoading] = React.useState(false)

    // Fetch Logic
    React.useEffect(() => {
        const fetchProducts = async () => {
            if (!query) {
                setOptions([])
                return
            }
            setLoading(true)
            try {
                const res = await fetch(`${API_BASE_URL}/api/planning/rolling/products/search?q=${encodeURIComponent(query)}&limit=20`)
                if (res.ok) {
                    setOptions(await res.json())
                }
            } catch (e) {
                console.error(e)
            } finally {
                setLoading(false)
            }
        }

        const timeoutId = setTimeout(fetchProducts, 300)
        return () => clearTimeout(timeoutId)
    }, [query])

    const handleSelect = (sku: string) => {
        const newVal = value.includes(sku)
            ? value.filter(v => v !== sku)
            : [...value, sku]
        onChange(newVal)
    }

    const handleRemove = (sku: string) => {
        onChange(value.filter(v => v !== sku))
    }

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    className="w-full justify-between min-w-[250px] h-auto min-h-[40px]"
                >
                    <div className="flex flex-wrap gap-1 items-center bg-transparent">
                        {value.length === 0 && <span className="text-muted-foreground font-normal">Select Products...</span>}
                        {value.length > 0 && (
                            <>
                                <span className="text-sm font-medium mr-1">{value.length} selected</span>
                            </>
                        )}
                    </div>
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[300px] p-0" align="start">
                <Command shouldFilter={false}>
                    <CommandInput placeholder="Search SKU or Name..." value={query} onValueChange={setQuery} />
                    <CommandList>
                        {loading && <div className="p-2 text-sm text-center text-muted-foreground">Loading...</div>}
                        {!loading && options.length === 0 && <CommandEmpty>No products found.</CommandEmpty>}
                        <CommandGroup>
                            {options.map((opt) => (
                                <CommandItem
                                    key={opt.sku_id}
                                    value={opt.sku_id}
                                    onSelect={() => handleSelect(opt.sku_id)}
                                >
                                    <Check
                                        className={cn(
                                            "mr-2 h-4 w-4",
                                            value.includes(opt.sku_id) ? "opacity-100" : "opacity-0"
                                        )}
                                    />
                                    <div className="flex flex-col">
                                        <span className="font-medium">{opt.sku_id}</span>
                                        <span className="text-xs text-muted-foreground truncate max-w-[200px]">{opt.product_name}</span>
                                    </div>
                                </CommandItem>
                            ))}
                        </CommandGroup>
                    </CommandList>
                </Command>
            </PopoverContent>
            {value.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                    {value.map(sku => (
                        <Badge key={sku} variant="secondary" className="pr-1">
                            {sku}
                            <button
                                className="ml-1 ring-offset-background rounded-full outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                                onMouseDown={(e) => {
                                    e.preventDefault()
                                    e.stopPropagation()
                                }}
                                onClick={() => handleRemove(sku)}
                            >
                                <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                            </button>
                        </Badge>
                    ))}
                </div>
            )}
        </Popover>
    )
}
