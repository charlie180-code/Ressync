document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const profileImageInput = document.getElementById('profileImageInput');
    const profileImagePreview = document.getElementById('profileImagePreview');
    const submitButton = document.querySelector('button[type="submit"]');
    const loadingText = document.getElementById('LoadingText');
    const spinner = document.querySelector('.spinner-border');
    const ButtonText = document.querySelector('#ButtonText');
    const arrivalDate = document.getElementById("arrival_date");
    const leavingDate = document.getElementById("leaving_date");
  
    const dropdownButton = document.getElementById('EmailProviderDropdown');
    const providerLogo = document.getElementById('providerLogo');
    const emailProviderInput = document.getElementById('EmailProviderInput');
    const dropdownItems = document.querySelectorAll('.dropdown-item');


    document.getElementById('toggleOldPassword').addEventListener('click', function () {
        const oldPasswordInput = document.getElementById('OldPassword');
        const eyeIconOld = document.getElementById('eyeIconOld');
        if (oldPasswordInput.type === "password") {
            oldPasswordInput.type = "text";
            eyeIconOld.setAttribute("fill", "green");
        } else {
            oldPasswordInput.type = "password";
            eyeIconOld.setAttribute("fill", "gray");
        }
    });



    document.getElementById('toggleNewPassword').addEventListener('click', function () {
        const newPasswordInput = document.getElementById('NewPassword');
        const eyeIconNew = document.getElementById('eyeIconNew');
        if (newPasswordInput.type === "password") {
            newPasswordInput.type = "text";
            eyeIconNew.setAttribute("fill", "green");
        } else {
            newPasswordInput.type = "password";
            eyeIconNew.setAttribute("fill", "gray");
        }
    });

    arrivalDate.addEventListener("change", function () {
        leavingDate.min = arrivalDate.value;
      });
    
      leavingDate.addEventListener("change", function () {
        arrivalDate.max = leavingDate.value;
      });



    document.getElementById('toggleConfirmPassword').addEventListener('click', function () {
        const confirmPasswordInput = document.getElementById('ConfirmPassword');
        const eyeIconConfirm = document.getElementById('eyeIconConfirm');
        if (confirmPasswordInput.type === "password") {
            confirmPasswordInput.type = "text";
            eyeIconConfirm.setAttribute("fill", "green");
        } else {
            confirmPasswordInput.type = "password";
            eyeIconConfirm.setAttribute("fill", "gray");
        }
    });

    document.getElementById('toggleEmailPassword').addEventListener('click', function () {
        const emailPasswordInput = document.getElementById('EmailPassword');
        const eyeIconEmail = document.getElementById('eyeIconEmail');
        if (emailPasswordInput.type === "password") {
            emailPasswordInput.type = "text";
            eyeIconEmail.setAttribute("fill", "green");
        } else {
            emailPasswordInput.type = "password";
            eyeIconEmail.setAttribute("fill", "gray"); 
        }
    });


    
    profileImageInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file.size > 5 * 1024 * 1024) { // 5 MB
            alert('La taille de l\'image ne doit pas dépasser 5 Mo.');
            profileImageInput.value = '';
            profileImagePreview.src = "{{ url_for('static', filename='default-profile.png') }}";
            return;
        }
  
        const reader = new FileReader();
        reader.onload = function() {
            profileImagePreview.src = reader.result;
        };
        reader.readAsDataURL(file);
    });
  
    dropdownItems.forEach(item => {
      item.addEventListener('click', function() {
        const selectedValue = this.getAttribute('data-value');
        const selectedLogo = this.getAttribute('data-logo');
        const selectedText = this.textContent.trim();
        dropdownButton.querySelector('#providerName').textContent = selectedText;
        emailProviderInput.value = selectedValue;
        providerLogo.src = selectedLogo;
        providerLogo.style.display = 'inline';
      });
    });
  
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        submitButton.disabled = true;
        ButtonText.style.display = 'none';
        loadingText.style.display = 'inline';
        spinner.style.display = 'inline-block';
  
        const formData = new FormData(form);
        if (profileImageInput.files.length > 0) {
            formData.append('profile_image', profileImageInput.files[0]);
        }

        if (emailProviderInput === 'custom') {
            formData.append('smtp_server', smtpServer);
            formData.append('smtp_port', smtpPort);
            formData.append('imap_server', smtpServer);
            formData.append('imap_port', smtpPort);
        }
            
  
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });
  
            if (response.redirected) {
                window.location.href = response.url;
                return;
            }
  
            const result = await response.json();
            if (response.ok) {
                alert('Profil mis à jour avec succès.');
                window.location.reload();
            } else {
                alert(result.error || 'Une erreur est survenue. Veuillez réessayer.');
            }
        } catch (error) {
            alert('Une erreur est survenue. Veuillez réessayer.');
        } finally {
            submitButton.disabled = false;
            loadingText.style.display = 'none';
            spinner.style.display = 'none';
            ButtonText.style.display = 'inline';
        }
    });
  });
  