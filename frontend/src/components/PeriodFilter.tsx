"use client"

import * as React from "react"
import { Check, ChevronsUpDown, CalendarIcon, X } from "lucide-react"
import { format, startOfMonth, endOfMonth, setDate, addDays, getYear, getMonth, lastDayOfMonth } from "date-fns"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"

export interface DateRange {
    from: Date | undefined
    to: Date | undefined
}

interface PeriodFilterProps {
    onFilterChange: (range: DateRange) => void
    className?: string
}

export function PeriodFilter({ onFilterChange, className }: PeriodFilterProps) {
    const currentYear = new Date().getFullYear()
    const [year, setYear] = React.useState<string>("ALL")
    const [month, setMonth] = React.useState<string>("ALL")
    const [week, setWeek] = React.useState<string>("ALL")
    const [specificDate, setSpecificDate] = React.useState<Date | undefined>(undefined)

    // Reset Specific Date when Period changes
    // Reset Period when Specific Date changes -> handled in handlers

    const triggerChange = (y: string, m: string, w: string) => {
        // Calculate Range

        let start: Date | undefined
        let end: Date | undefined

        if (y === "ALL") {
            // All Time
            start = undefined
            end = undefined
        } else {
            const yInt = parseInt(y)
            if (!yInt) return // Invalid

            if (m === "ALL") {
                // Full Year
                start = new Date(yInt, 0, 1)
                end = new Date(yInt, 11, 31)
            } else {
                const mInt = parseInt(m)
                if (w === "ALL") {
                    // Full Month
                    start = new Date(yInt, mInt, 1)
                    end = lastDayOfMonth(start)
                } else {
                    // Specific Week (1-7, 8-14, 15-21, 22-End)
                    const wInt = parseInt(w) // 1, 2, 3, 4
                    const ranges = [
                        [1, 7],
                        [8, 14],
                        [15, 21],
                        [22, 31] // 31 will be clamped
                    ]

                    const [dStart, dEnd] = ranges[wInt - 1]
                    start = new Date(yInt, mInt, dStart)

                    // For end date, handle end of month
                    const lastDay = lastDayOfMonth(new Date(yInt, mInt, 1)).getDate()
                    const finalDay = Math.min(dEnd, lastDay)
                    end = new Date(yInt, mInt, finalDay)
                }
            }
        }

        onFilterChange({ from: start, to: end })
        setSpecificDate(undefined) // Clear specific date
    }

    const handleYearChange = (val: string) => {
        setYear(val)
        triggerChange(val, month, week)
    }

    const handleMonthChange = (val: string) => {
        setMonth(val)
        // If switching to ALL month, reset Week to ALL
        const newWeek = val === "ALL" ? "ALL" : week
        setWeek(newWeek)
        triggerChange(year, val, newWeek)
    }

    const handleWeekChange = (val: string) => {
        setWeek(val)
        triggerChange(year, month, val)
    }

    const handleSpecificDateSelect = (date: Date | undefined) => {
        setSpecificDate(date)
        if (date) {
            onFilterChange({ from: date, to: date })
            // Visual reset of dropdowns could be nice but might be annoying.
            // Let's keep dropdowns but maybe highlight that 'Specific Date' is active?
        } else {
            // Revert to dropdowns
            triggerChange(year, month, week)
        }
    }

    // Generate Year Options (Current +/- 2)
    const years = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i)

    // Months
    const months = [
        { val: "0", label: "January" }, { val: "1", label: "February" }, { val: "2", label: "March" },
        { val: "3", label: "April" }, { val: "4", label: "May" }, { val: "5", label: "June" },
        { val: "6", label: "July" }, { val: "7", label: "August" }, { val: "8", label: "September" },
        { val: "9", label: "October" }, { val: "10", label: "November" }, { val: "11", label: "December" },
    ]

    return (
        <div className={cn("flex flex-wrap items-center gap-2 p-2 bg-muted/50 rounded-md border", className)}>
            <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-muted-foreground">Period:</span>

                {/* YEAR */}
                <Select value={year} onValueChange={handleYearChange}>
                    <SelectTrigger className="w-[100px] h-8 bg-background">
                        <SelectValue placeholder="Year" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="ALL">All Years</SelectItem>
                        {years.map(y => <SelectItem key={y} value={y.toString()}>{y}</SelectItem>)}
                    </SelectContent>
                </Select>

                {/* MONTH */}
                <Select value={month} onValueChange={handleMonthChange}>
                    <SelectTrigger className="w-[130px] h-8 bg-background">
                        <SelectValue placeholder="Month" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="ALL">All Months</SelectItem>
                        {months.map(m => <SelectItem key={m.val} value={m.val}>{m.label}</SelectItem>)}
                    </SelectContent>
                </Select>

                {/* WEEK */}
                <Select value={week} onValueChange={handleWeekChange} disabled={month === "ALL"}>
                    <SelectTrigger className="w-[120px] h-8 bg-background">
                        <SelectValue placeholder="Week" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="ALL">All Weeks</SelectItem>
                        <SelectItem value="1">Week 1 (1-7)</SelectItem>
                        <SelectItem value="2">Week 2 (8-14)</SelectItem>
                        <SelectItem value="3">Week 3 (15-21)</SelectItem>
                        <SelectItem value="4">Week 4 (22-End)</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <div className="h-4 w-px bg-border mx-2" />

            {/* SPECIFIC DATE */}
            <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-muted-foreground">Or Date:</span>
                <Popover>
                    <PopoverTrigger asChild>
                        <Button
                            variant={"outline"}
                            className={cn(
                                "h-8 w-[150px] justify-start text-left font-normal bg-background",
                                !specificDate && "text-muted-foreground"
                            )}
                        >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {specificDate ? format(specificDate, "PPP") : <span>Pick a date</span>}
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                            mode="single"
                            selected={specificDate}
                            onSelect={handleSpecificDateSelect}
                            initialFocus
                        />
                    </PopoverContent>
                </Popover>
                {specificDate && (
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => handleSpecificDateSelect(undefined)}>
                        <X className="h-4 w-4" />
                    </Button>
                )}
            </div>
        </div>
    )
}
