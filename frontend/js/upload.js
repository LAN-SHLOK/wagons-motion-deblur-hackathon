/**
 * Handles Drag and Drop and File Input logic
 */
export const initUpload = (dropZoneId, fileInputId, fileNameId) => {
    const dropZone = document.getElementById(dropZoneId);
    const fileInput = document.getElementById(fileInputId);
    const fileNameDisplay = document.getElementById(fileNameId);

    // Prevent default behaviors for drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    // Visual feedback when dragging over the zone
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('highlight'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('highlight'), false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            updateFileName(files[0].name);
            // Trigger change event so app.js detects it
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });

    // Handle file selection via button
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            updateFileName(e.target.files[0].name);
        }
    });

    function updateFileName(name) {
        if (fileNameDisplay) {
            fileNameDisplay.innerText = `Selected: ${name}`;
            fileNameDisplay.classList.remove('hidden');
        }
    }
};
