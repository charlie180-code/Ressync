document.querySelectorAll('.generate-barcode').forEach(function (element) {
    element.addEventListener('click', function (event) {
        event.preventDefault();
        const bookId = this.getAttribute('data-book-id');

        // Generate Barcode and display in modal
        const barcodeImage = document.getElementById('barcodeImage');
        JsBarcode(barcodeImage, bookId, {
            format: 'CODE128',
            displayValue: true,
        });

        // Convert the barcode SVG to PNG and set the download link
        const svgString = new XMLSerializer().serializeToString(barcodeImage);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.src = 'data:image/svg+xml;base64,' + btoa(svgString);

        img.onload = function () {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);

            // Set the download link
            const downloadLink = document.getElementById('downloadBarcode');
            downloadLink.href = canvas.toDataURL('image/png');
        };

        // Show the modal
        const barcodeModal = new bootstrap.Modal(document.getElementById('barcodeModal'));
        barcodeModal.show();
    });
});
