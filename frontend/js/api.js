import { CONFIG } from './config.js';

export const API = {
    async checkHealth() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/health`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            return response;
        } catch (error) {
            console.error('Health check failed:', error);
            return { ok: false };
        }
    },

    async runPipeline(file) {
        // If MOCK is on, return fake data immediately
        if (CONFIG.USE_MOCK) {
            return await this.getMockResponse();
        }

        // Otherwise, fetch from the real Python server
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/pipeline`, {
                method: 'POST',
                body: formData
            });
            return response;
        } catch (error) {
            console.error('Pipeline request failed:', error);
            return { ok: false };
        }
    },

    async getMockResponse() {
        await new Promise(r => setTimeout(r, CONFIG.SCAN_DELAY));
        
        return {
            ok: true,
            json: async () => ({
                enhancedFrames: null, // Will use extracted frames
                detections: [
                    { label: 'Wagon Axle', confidence: 94, x: 120, y: 180, w: 200, h: 150 },
                    { label: 'Wheel Bearing', confidence: 89, x: 450, y: 220, w: 180, h: 140 },
                    { label: 'Coupling', confidence: 92, x: 280, y: 90, w: 150, h: 120 },
                    { label: 'Brake System', confidence: 87, x: 350, y: 300, w: 160, h: 130 }
                ],
                metrics: {
                    psnr: 32.4 + Math.random() * 5,
                    confidence: 91.7,
                    inferenceTime: 2.3
                }
            })
        };
    }
};