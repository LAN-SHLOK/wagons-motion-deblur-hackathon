/**
 * WagonAI Utility Library
 */

export const Utils = {
    // Format large numbers with commas
    formatNumber: (num) => {
        return new Intl.NumberFormat().format(num);
    },

    // Save a log of scans to LocalStorage (Bonus feature for judges)
    saveToHistory: (data) => {
        const history = JSON.parse(localStorage.getItem('wagon_history') || '[]');
        history.push({
            timestamp: new Date().toISOString(),
            detections: data.detections,
            confidence: data.confidence
        });
        localStorage.setItem('wagon_history', JSON.stringify(history.slice(-10)));
    },

    // Smooth loading transition
    fadeIn: (element) => {
        element.classList.remove('hidden');
        element.style.opacity = 0;
        element.style.transition = "opacity 0.5s ease";
        setTimeout(() => element.style.opacity = 1, 10);
    }
};