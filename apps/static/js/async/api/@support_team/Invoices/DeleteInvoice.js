document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.delete-invoice-btn').forEach(button => {
        button.addEventListener('click', async (event) => {
            const invoiceId = event.target.dataset.invoiceId;

            const confirmResult = await Swal.fire({
                title: 'Êtes-vous sûr ?',
                text: "Cette action supprimera définitivement la facture.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Oui, supprimer',
                cancelButtonText: 'Annuler'
            });

            if (confirmResult.isConfirmed) {
                try {
                    const response = await fetch(window.location.pathname, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ invoice_id: invoiceId })
                    });

                    if (!response.ok) throw new Error('Network response was not ok');

                    const result = await response.json();

                    if (result.success) {
                        Swal.fire({
                            icon: 'success',
                            title: result.title,
                            text: result.message
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Erreur!',
                            text: result.message
                        });
                    }
                } catch (error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur!',
                        text: error.message
                    });
                }
            }
        });
    });
});
