/**
 * WagonAI Global Configuration
 * Centralized settings for the Integration Lead.
 */
export const CONFIG = {
    // TOGGLE: 
    // Set to 'true' to show the UI using fake data (best for offline testing).
    // Set to 'false' once your Render API is live.
    USE_MOCK: false, 

    // BACKEND URL:
    // Replace this with your actual Render service URL
    API_BASE_URL: "https://wagonai-api-service.onrender.com/api/v1",
    
    // UI SETTINGS:
    SCAN_DELAY: 2000,   // Delay in ms for the simulated processing
    PRIMARY_COLOR: "#22d3ee", // Neon Cyan for charts and highlights
    
    // ENDPOINTS:
    ENDPOINTS: {
        PIPELINE: "/pipeline",
        HEALTH: "/health"
    }
};