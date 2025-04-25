document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.delete-invoice-btn').forEach(button => {
        button.addEventListener('click', async (event) => {
            const invoiceId = event.target.dataset.invoiceId;

            if (confirm("Êtes-vous sûr de vouloir supprimer cette facture ?")) {
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
                            title: 'Error!',
                            text: result.message
                        });
                    }
                } catch (error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: error.message
                    });
                }
            }
        });
    });
});