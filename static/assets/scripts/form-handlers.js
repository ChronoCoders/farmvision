/**
 * Form handlers for detection forms
 * Extracted from inline scripts for CSP compliance
 */

(function() {
    'use strict';

    // Constants for file validation
    var MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    var ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/tiff'];

    /**
     * Handle file input change event for image preview and validation
     * @param {Event} event - The change event
     */
    function loadFile(event) {
        if (!event.target.files || !event.target.files[0]) return;

        var file = event.target.files[0];

        // Validate file type
        if (ALLOWED_TYPES.indexOf(file.type) === -1) {
            alert('Geçersiz dosya formatı. Sadece JPEG, PNG ve TIFF formatları kabul edilir.');
            event.target.value = ''; // Clear the input
            return;
        }

        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            alert('Dosya boyutu çok büyük. Maksimum 10MB yüklenebilir.');
            event.target.value = ''; // Clear the input
            return;
        }

        var reader = new FileReader();

        reader.onload = function() {
            var output = document.getElementById('output');
            if (output) output.src = reader.result;
        };

        reader.onerror = function(error) {
            console.error('Dosya okuma hatası:', error);
            alert('Dosya yüklenirken bir hata oluştu. Lütfen tekrar deneyin.');
            event.target.value = ''; // Clear the input
        };

        reader.readAsDataURL(file);
    }

    /**
     * Handle form submission - disable button and show loading state
     * @param {Event} event - The submit event
     */
    function handleFormSubmit(event) {
        var submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Yükleniyor...';
        }
        // Form will submit normally
        return true;
    }

    /**
     * Handle form submission for form2 - disable button and show loading state
     * @param {Event} event - The submit event
     */
    function handleFormSubmit2(event) {
        var submitBtn = document.getElementById('submitBtn2');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Yükleniyor...';
        }
        // Form will submit normally
        return true;
    }

    /**
     * Refresh the current page
     */
    function refreshPage() {
        location.reload();
    }

    // Attach event listeners when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // File input handlers
        var fileInputs = document.querySelectorAll('input[type="file"][data-preview="true"]');
        fileInputs.forEach(function(input) {
            input.addEventListener('change', loadFile);
        });

        // Form submit handlers
        var uploadForm = document.getElementById('upload-file');
        if (uploadForm) {
            uploadForm.addEventListener('submit', handleFormSubmit);
        }

        // Multi-detection form handler
        var multiForm = document.querySelector('form[data-form="multi-detection"]');
        if (multiForm) {
            multiForm.addEventListener('submit', handleFormSubmit2);
        }

        // Refresh button handlers
        var refreshButtons = document.querySelectorAll('[data-action="refresh"]');
        refreshButtons.forEach(function(button) {
            button.addEventListener('click', refreshPage);
        });
    });

    // Expose functions globally for backwards compatibility during transition
    window.loadFile = loadFile;
    window.handleFormSubmit = handleFormSubmit;
    window.handleFormSubmit2 = handleFormSubmit2;
})();
