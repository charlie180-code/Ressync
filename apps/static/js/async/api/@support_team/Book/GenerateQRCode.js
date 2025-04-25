document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.generate-qr').forEach(function (element) {
        element.addEventListener('click', function (event) {
            event.preventDefault();
            const bookId = this.getAttribute('data-book-id');

            // Generate QR code and display in modal
            QRCode.toDataURL(bookId, { errorCorrectionLevel: 'H' }, function (err, url) {
                if (err) {
                    console.error('Error generating QR code:', err);
                    return;
                }
                // Set the QR code image source
                const qrCodeImage = document.getElementById('qrCodeImage');
                qrCodeImage.src = url;

                // Set the download link
                const downloadLink = document.getElementById('downloadQrCode');
                downloadLink.href = url;

                // Show the modal
                const qrModal = new bootstrap.Modal(document.getElementById('qrCodeModal'));
                qrModal.show();
            });
        });
    });
});