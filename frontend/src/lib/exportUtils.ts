
export function exportToCSV(data: any[], headers: string[], filenamePrefix: string) {
    if (!data || !data.length) {
        alert("No data to export");
        return;
    }

    // 1. Create CSV Content with BOM for Excel UTF-8 compatibility
    const BOM = "\uFEFF";
    const headerRow = headers.join(",");

    // Map data to match header order assuming data objects have keys matching headers OR we just dump values if passed simplified
    // IMPORTANT: The caller usually passes objects. We need to know which keys correspond to which headers?
    // Simplified specific implementation:
    // Actually, calling pages construct the ROW arrays themselves currently.
    // Let's modify the signature to accept PRE-FORMATTED ROWS to keep logic in pages flexible (for mapping names), 
    // OR allow passing a mapper.
    // Sticking to "Pre-formatted rows" is safer for existing logic refactor, but standardizing means doing the "blob" part commonly.

    // Better signature: exportToCSV(csvContent: string, filename: string)
    // No, let's keep it helpful. 
    // exportToCSV(data: any[], columns: { header: string, accessor: (item:any) => string }[], filename: string)

    // Let's stick to the simplest "Blob" creator first, as pages have complex mapping logic (Units Map, Groups Map).
    // Moving that mapping logic to a generic util is hard without passing the maps.
    // So pages will generate the CSV String, and this util handles BOM + Download.
}

export function downloadCSV(csvContent: string, filenamePrefix: string) {
    const BOM = "\uFEFF";
    const blob = new Blob([BOM + csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);

    const dateStr = new Date().toISOString().slice(0, 10);
    link.setAttribute("download", `${filenamePrefix}_${dateStr}.csv`);

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
