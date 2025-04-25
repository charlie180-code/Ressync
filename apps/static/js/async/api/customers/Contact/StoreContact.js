document.getElementById('addContactButton').addEventListener('click', async () => {
  const spinner = document.getElementById('spinner');
  const buttonText = document.getElementById('buttonText');
  const firstName = document.getElementById('first_name').value;
  const lastName = document.getElementById('last_name').value;
  const email = document.getElementById('email').value;
  const phone = document.getElementById('phone').value;
  const gender = document.getElementById('gender').value;
  const CreateContactForm = document.getElementById('CreateContactForm')
  const duplicateEmailError = document.getElementById('DuplicateEmailContact')
  const duplicatePhoneError = document.getElementById('DuplicatePhoneError')

  spinner.classList.remove('d-none');
  document.getElementById('addContactButton').disabled = true;

  try {
    const response = await fetch(CreateContactForm.action, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        email: email,
        phone: phone,
        gender: gender
        }),
    });

    const data = await response.json();

    if (response.ok) {
        Swal.fire({
            icon: 'success',
            title: data.title,
            text: data.message,
        }).then(() => {
            window.location.reload();
        });

    } else if(data.errorType == 'DuplicatePhone'){
        duplicatePhoneError.classList.remove('d-none')
    }
    else if(data.errorType == 'DuplicateEmail'){
        duplicateEmailError.classList.remove('d-none')
    }
  } catch (error) {
      Swal.fire({
          icon: 'error',
          title: 'Erreur',
          text: 'Une erreur s\'est produite. Veuillez réessayer plus tard.',
      });
  } finally {
    spinner.classList.add('d-none');
    document.getElementById('addContactButton').disabled = false;
  }
});
