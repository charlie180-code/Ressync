import UtilApiURLs from "../../../../_globals/general/Mail.js";

document.addEventListener('DOMContentLoaded', function() {
    fetchContacts();

    async function fetchContacts() {
      try {
        let receiverOptions = document.getElementById('receiver-options');
        let ccOptions = document.getElementById('cc-options');
        let companyId = receiverOptions.dataset.companyId
        let response = await fetch(`${UtilApiURLs.PopulateUserContacts}/${companyId}`);
        let contacts = await response.json();

        contacts.forEach(contact => {
          let option = document.createElement('option');
          option.value = contact.email;
          option.text = contact.name || contact.email;
          receiverOptions.appendChild(option);

          let ccOption = document.createElement('option');
          ccOption.value = contact.email;
          ccOption.text = contact.name || contact.email;
          ccOptions.appendChild(ccOption);
        });
      } catch (error) {
        console.error('Error fetching contacts:', error);
      }
    }
  });