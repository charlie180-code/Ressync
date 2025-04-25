import domain from "../../../../_globals/domain.js";

document.addEventListener('DOMContentLoaded', function() {

    const toInput = document.getElementById('to-input');
    const ccInput = document.getElementById('cc-input');
    const toContainer = document.getElementById('to-container');
    const ccContainer = document.getElementById('cc-container');
    const toSuggestions = document.getElementById('to-suggestions');
    const ccSuggestions = document.getElementById('cc-suggestions');
    const toRecipients = document.getElementById('to-recipients');
    const ccRecipients = document.getElementById('cc-recipients');
    const fileInput = document.getElementById('file-input');
    const attachmentsContainer = document.getElementById('file-attachments');
    const attachmentsData = document.getElementById('attachments-data');
    const emailForm = document.getElementById('emailForm');
    const submitButton = document.getElementById('submitButton');
    const LoadindText = document.getElementById('LoadindText')
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('buttonText');
    const companyId = document.querySelector('#company-id').value;

    let contacts = [];
    let selectedToContacts = [];
    let selectedCcContacts = [];
    let attachments = [];

    fetch(`${domain}/msg/v1/get-contacts/${companyId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            contacts = Array.isArray(data) ? data : [];
        })
        .catch(error => {
            console.error('Error fetching contacts:', error);
            contacts = [];
        });

    // Handle To input
    toInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.trim().toLowerCase();
        if (searchTerm.length < 2) {
            toSuggestions.style.display = 'none';
            return;
        }

        const filtered = contacts.filter(contact => 
            (contact.email && contact.email.toLowerCase().includes(searchTerm)) ||
            (contact.first_name && contact.first_name.toLowerCase().includes(searchTerm)) ||
            (contact.last_name && contact.last_name.toLowerCase().includes(searchTerm))
        );

        displaySuggestions(filtered, toSuggestions, 'to');
    });

    // Handle Cc input
    ccInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.trim().toLowerCase();
        if (searchTerm.length < 2) {
            ccSuggestions.style.display = 'none';
            return;
        }

        const filtered = contacts.filter(contact => 
            (contact.email && contact.email.toLowerCase().includes(searchTerm)) ||
            (contact.first_name && contact.first_name.toLowerCase().includes(searchTerm)) ||
            (contact.last_name && contact.last_name.toLowerCase().includes(searchTerm))
        );

        displaySuggestions(filtered, ccSuggestions, 'cc');
    });

    function displaySuggestions(filteredContacts, container, type) {
        container.innerHTML = '';
        if (!filteredContacts || filteredContacts.length === 0) {
            container.style.display = 'none';
            return;
        }

        filteredContacts.forEach(contact => {
            if (!contact.id || !contact.email) return;
            
            const div = document.createElement('div');
            div.className = 'contact-suggestion';
            div.textContent = `${contact.first_name || ''} ${contact.last_name || ''} <${contact.email}>`;
            div.addEventListener('click', () => {
                addContact(contact, type);
                container.style.display = 'none';
                if (type === 'to') toInput.value = '';
                else ccInput.value = '';
            });
            container.appendChild(div);
        });

        container.style.display = 'block';
    }

    function addContact(contact, type) {
        if (!contact || !contact.id || !contact.email) return;

        const isDuplicate = type === 'to' 
            ? selectedToContacts.some(c => c.id === contact.id)
            : selectedCcContacts.some(c => c.id === contact.id);

        if (isDuplicate) return;

        const tag = document.createElement('div');
        tag.className = 'contact-tag';
        tag.innerHTML = `
            ${contact.first_name || ''} ${contact.last_name || ''}
            <span class="contact-tag-remove" data-id="${contact.id}">&times;</span>
        `;

        const removeBtn = tag.querySelector('.contact-tag-remove');
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            removeContact(contact.id, type);
        });

        if (type === 'to') {
            selectedToContacts.push(contact);
            toContainer.insertBefore(tag, toInput);
            toRecipients.value = JSON.stringify(selectedToContacts.map(c => c.email));
        } else {
            selectedCcContacts.push(contact);
            ccContainer.insertBefore(tag, ccInput);
            ccRecipients.value = JSON.stringify(selectedCcContacts.map(c => c.email));
        }
    }

    function removeContact(id, type) {
        if (type === 'to') {
            selectedToContacts = selectedToContacts.filter(c => c.id !== id);
            toRecipients.value = JSON.stringify(selectedToContacts.map(c => c.email));
            toContainer.innerHTML = '';
            toContainer.appendChild(toInput);
            selectedToContacts.forEach(contact => {
                addContact(contact, 'to');
            });
        } else {
            selectedCcContacts = selectedCcContacts.filter(c => c.id !== id);
            ccRecipients.value = JSON.stringify(selectedCcContacts.map(c => c.email));
            ccContainer.innerHTML = '';
            ccContainer.appendChild(ccInput);
            selectedCcContacts.forEach(contact => {
                addContact(contact, 'cc');
            });
        }
    }

    // Handle file attachments
    fileInput.addEventListener('change', function() {
        if (!fileInput.files || fileInput.files.length === 0) return;

        Array.from(fileInput.files).forEach(file => {
            if (file.size > 10 * 1024 * 1024) { // 10MB limit
                alert(`File ${file.name} is too large (max 10MB)`);
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                const attachment = {
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    data: e.target.result.split(',')[1]
                };
                attachments.push(attachment);
                updateAttachmentsDisplay();
            };
            reader.onerror = function() {
                console.error('Error reading file');
            };
            reader.readAsDataURL(file);
        });
        fileInput.value = ''; // Reset input to allow adding same files again
    });

    function updateAttachmentsDisplay() {
        attachmentsContainer.innerHTML = '';
        attachments.forEach((attachment, index) => {
            const item = document.createElement('div');
            item.className = 'attachment-item';
            item.innerHTML = `
                <i class="bi bi-paperclip"></i>
                <span>${attachment.name} (${formatFileSize(attachment.size)})</span>
                <span class="attachment-remove" data-index="${index}">&times;</span>
            `;
            const removeBtn = item.querySelector('.attachment-remove');
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                attachments.splice(index, 1);
                updateAttachmentsDisplay();
            });
            attachmentsContainer.appendChild(item);
        });
        attachmentsData.value = JSON.stringify(attachments);
    }

    function formatFileSize(bytes) {
        if (typeof bytes !== 'number' || bytes < 0) return '0 Bytes';
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    emailForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        let isValid = true;
        
        // Validate recipients
        if (selectedToContacts.length === 0) {
            document.getElementById('to-error').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('to-error').style.display = 'none';
        }
        
        // Validate subject
        const subject = document.querySelector('input[name="subject"]').value;
        if (!subject || subject.trim() === '') {
            document.getElementById('subject-error').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('subject-error').style.display = 'none';
        }
        
        // Validate message
        const message = quill.root.innerHTML;
        if (!message || message === '<p><br></p>' || message.trim() === '<p></p>') {
            document.getElementById('message-error').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('message-error').style.display = 'none';
        }
        
        if (!isValid) {
            const firstError = document.querySelector('.text-danger[style="display: block;"]');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }
        
        document.getElementById('message-content').value = message;
        
        spinner.style.display = 'block';
        buttonText.classList.add('d-none');
        submitButton.disabled = true;
        LoadindText.classList.remove('d-none');
        
        const formData = new FormData(emailForm);
        
        fetch(emailForm.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: data.title,
                    text: data.message
                }).then(() => {
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    }
                });
            } else {
                throw new Error(data.message || 'Unknown error occurred');
            }
        })
        .catch(error => {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message || 'Error'
            });
        })
        .finally(() => {
            spinner.style.display = 'none';
            buttonText.classList.remove('d-none');
            submitButton.disabled = false;
            LoadindText.classList.add('d-none')
        });
    });
});