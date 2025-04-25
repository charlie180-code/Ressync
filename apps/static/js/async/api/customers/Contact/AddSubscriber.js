import UtilApiURLs from "../../../../_globals/UtilApiUrls.js";

document.addEventListener('DOMContentLoaded', function() {
  const successModal = document.getElementById('success-modal');
  const errorModal = document.getElementById('error-modal');
  const closeSuccessModalBtn = document.getElementById('close-success-modal');
  const closeErrorModalBtn = document.getElementById('close-error-modal');
  const retryBtn = document.getElementById('retry-button');
  const submitBtn = document.getElementById('submit-btn');
  const spinner = document.getElementById('spinner');
  const submitText = document.getElementById('submit-text');
  const emailInput = document.getElementById('email-address');
  const emailEmptyError = document.getElementById('EmailEmptyError');
  const emailError = document.getElementById('EmailError');

  function showSuccessModal() {
    successModal.classList.remove('hidden');
  }

  function showErrorModal() {
    errorModal.classList.remove('hidden');
  }

  closeSuccessModalBtn.addEventListener('click', function() {
    successModal.classList.add('hidden');
  });

  closeErrorModalBtn.addEventListener('click', function() {
    errorModal.classList.add('hidden');
  });

  retryBtn.addEventListener('click', function() {
    console.log('Retry operation...');
    errorModal.classList.add('hidden');
  });

  function toggleButtonSpinner(isLoading) {
    if (isLoading) {
      spinner.classList.remove('hidden');
      submitText.classList.add('hidden');
    } else {
      spinner.classList.add('hidden');
      submitText.classList.remove('hidden');
    }
  }

  function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  submitBtn.addEventListener('click', function() {
    const email = emailInput.value.trim();

    // Validate email
    if (email === '') {
      emailEmptyError.classList.remove('hidden');
      emailError.classList.add('hidden');
      return;
    } else {
      emailEmptyError.classList.add('hidden');
    }

    if (!validateEmail(email)) {
      emailError.classList.remove('hidden');
      return;
    } else {
      emailError.classList.add('hidden');
    }

    toggleButtonSpinner(true);

    fetch(UtilApiURLs.StoreSubscriberBasicURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email: email })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('Success:', data);
      showSuccessModal();
    })
    .catch(error => {
      console.error('Error:', error);
      showErrorModal();
    })
    .finally(() => {
      toggleButtonSpinner(false);
    });
  });
});
