import UtilApiURLs from "../../../../_globals/general/Mail.js";

document.getElementById('sendMessageButton').addEventListener('click', async () => {
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('buttonText');
    const form = document.getElementById('messageForm');
    const formData = new FormData(form);
    const companyId = form.dataset.companyId
  
    spinner.classList.remove('d-none');
    buttonText.classList.add('d-none');
  
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: JSON.stringify(Object.fromEntries(formData)),
        headers: {
          'Content-Type': 'application/json'
        }
      });
  
      if (response.ok) {
        Swal.fire({
          icon: 'success',
          title: 'Message envoyé!',
          text: 'Votre message a été envoyé avec succès.',
        });
        window.location.href = `${UtilApiURLs.MessageSentSuccessURL}/${companyId}`
      } else {
        const errorData = await response.json();
        Swal.fire({
          icon: 'error',
          title: 'Erreur!',
          text: `Erreur: ${errorData.message}`,
        });
      }
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Erreur!',
        text: 'Erreur lors de l\'envoi du message.',
      });
    } finally {
      spinner.classList.add('d-none');
      buttonText.classList.remove('d-none');
    }
  });
  