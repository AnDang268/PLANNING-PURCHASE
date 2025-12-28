
// Application Configuration
// =========================
// This file centralizes all configuration settings for the Frontend.
// To deploy to Production:
// 1. Either update the defaults here directly,
// 2. OR use Environment Variables (Recommended): NEXT_PUBLIC_API_URL

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Add other global configs here if needed
export const APP_CONFIG = {
    MISA_SYNC_ENABLED: true,
    DEFAULT_CURRENCY: "VND",
    REFRESH_INTERVAL: 30000, // 30 seconds
};
