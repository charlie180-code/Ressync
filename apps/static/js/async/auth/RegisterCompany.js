import UtilApiURLs from '../../_globals/general/Auth.js'
import ApiURLs from '../../_globals/general/Api.js';

const CompanyTitle = document.querySelector("#Title");
const Description = document.querySelector("#Description");
const CompanyEmail = document.querySelector("#Email");
const LogoFile = document.querySelector("#LogoFile");
const Location = document.querySelector("#Location");
const Category = document.querySelector("#Category");
const Nature = document.querySelector("#Nature");
const PhoneNumber = document.querySelector("#PhoneNumber");
const WebsiteUrl = document.querySelector("#WebsiteUrl");
const LinkedinUrl = document.querySelector("#LinkedinUrl");
const TwitterUrl = document.querySelector("#TwitterUrl");
const FacebookUrl = document.querySelector("#FacebookUrl");
const NumberOfEmployees = document.querySelector("#NumberOfEmployees");
const YearEstablished = document.querySelector("#YearEstablished");
const AnnualRevenue = document.querySelector("#AnnualRevenue");
const addressInput = document.querySelector("#Location");
const suggestionsContainer = document.querySelector("#suggestions");
const privacyCheck = document.getElementById('privacyCheck');

// Error Elements
const privacyCheckError = document.getElementById('PrivacyCheckError');
const CompanyTitleEmptyError = document.querySelector("#EmptyNameError");
const LogoEmptyError = document.querySelector("#LogoEmptyError");
const LogoTypeError = document.querySelector("#LogoTypeError");
const LogoSizeError = document.querySelector("#LogoSizeError");
const InvalidEmailAddress = document.querySelector("#InvalidEmailAddress");
const AddressEmptyError = document.querySelector("#AddressEmptyError");
const CategoryEmptyError = document.querySelector("#CategoryEmptyError");
const CompanySizeEmptyError = document.querySelector("#CompanySizeEmptyError");

const CreateCompanyButton = document.querySelector("#CreateCompanyButton");
const Spinner = document.querySelector("#Spinner");

export default function validateForm() {
  let valid = true;

  if (CompanyTitle.value.trim() === '') {
    CompanyTitleEmptyError.classList.remove('hidden');
    valid = false;
  } else {
    CompanyTitleEmptyError.classList.add('hidden');
  }

  if (!LogoFile.files[0]) {
    LogoEmptyError.classList.remove('hidden');
    valid = false;
  } else {
    LogoEmptyError.classList.add('hidden');
  }

  if (!validateLogoFile()) {
    valid = false;
  }

  if (Location.value.trim() === '') {
    AddressEmptyError.classList.remove('hidden');
    valid = false;
  } else {
    AddressEmptyError.classList.add('hidden');
  }

  if (!validateCategory()) {
    valid = false;
  }

  if (CompanyEmail.value.trim() === '' || !validateEmail()) valid = false;

  if (NumberOfEmployees.value === '') {
    CompanySizeEmptyError.classList.remove('hidden');
    valid = false;
  } else {
    CompanySizeEmptyError.classList.add('hidden');
  }

  CreateCompanyButton.disabled = !valid;
  return valid;
}

function validateCompanyTitle() {
  if (CompanyTitle.value.trim() === '') {
    CompanyTitleEmptyError.classList.remove('hidden');
  } else {
    CompanyTitleEmptyError.classList.add('hidden');
  }
  validateForm();
}

function showSuccessModal(email) {
  const modal = document.getElementById('successModal');
  const AdminEmail = modal.querySelector('#AdminEmail');

  AdminEmail.textContent = email;

  modal.classList.remove('hidden');
  modal.classList.add('flex');
}


function validateLogoFile() {
  const file = LogoFile.files[0];
  let isValid = true;

  if (!file) {
    LogoEmptyError.classList.remove('hidden');
    isValid = false;
  } else {
    LogoEmptyError.classList.add('hidden');
  }

  const allowedTypes = ['image/svg+xml', 'image/png', 'image/jpeg', 'image/gif'];
  if (file && !allowedTypes.includes(file.type)) {
    LogoTypeError.classList.remove('hidden');
    isValid = false;
  } else {
    LogoTypeError.classList.add('hidden');
  }

  if (file && file.size > 5 * 1024 * 1024) {
    LogoSizeError.classList.remove('hidden');
    isValid = false;
  } else {
    LogoSizeError.classList.add('hidden');
  }

  return isValid;
}



function checkPrivacyPolicy() {
  if (!privacyCheck.checked) {
    privacyCheckError.classList.remove('hidden');
    CreateCompanyButton.disabled = true;
  } else {
    privacyCheckError.classList.add('hidden');
    CreateCompanyButton.disabled = false;
  }
}


function validateLocation() {
  if (Location.value.trim() === '') {
    AddressEmptyError.classList.remove('hidden');
  } else {
    AddressEmptyError.classList.add('hidden');
  }
  validateForm();
}

function validateCategory() {
  const selectedCategory = document.querySelector('input[name="category"]:checked');
  
  if (!selectedCategory) {
    CategoryEmptyError.classList.remove('hidden');
    return false;
  } else {
    CategoryEmptyError.classList.add('hidden');
    return true;
  }
}


function validateEmail() {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (CompanyEmail.value.trim() === '') {
    InvalidEmailAddress.classList.add('hidden');
    return false;
  } else if (!emailPattern.test(CompanyEmail.value.trim())) {
    InvalidEmailAddress.classList.remove('hidden');
    return false;
  } else {
    InvalidEmailAddress.classList.add('hidden');
    return true;
  }
}

function validateCompanySize() {
  if (NumberOfEmployees.value === '') {
    CompanySizeEmptyError.classList.remove('hidden');
  } else {
    CompanySizeEmptyError.classList.add('hidden');
    enableSubmitButton();
  }
  validateForm();
}

function enableSubmitButton() {
  CreateCompanyButton.disabled = false;
}

function disableSubmitButton() {
  CreateCompanyButton.disabled = true;
}

function toggleUIState(isLoading) {
  if (isLoading) {
    Spinner.classList.remove('hidden');
    disableSubmitButton();
  } else {
    Spinner.classList.add('hidden');
    enableSubmitButton();
  }
}

if (LogoFile) {
  LogoFile.addEventListener('change', () => {
    const isLogoValid = validateLogoFile();
    if (isLogoValid) validateForm();
  });
}


if (CompanyEmail) {
  CompanyEmail.addEventListener('input', () => {
    validateEmail();
    enableSubmitButton();
  });
}


// Function to limit words in a textarea
function limitWords(textarea, maxWords) {
  const wordCountElem = document.getElementById('wordCount');
  let words = textarea.value.trim().split(/\s+/);

  if (words.length > maxWords) {
    words = words.slice(0, maxWords);
    textarea.value = words.join(' ');
  }

  wordCountElem.textContent = `${words.length} / ${maxWords}`;
}

// Debounce function to limit the rate of API calls
const debounce = (func, delay) => {
  let debounceTimer;
  return function(...args) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => func.apply(this, args), delay);
  };
};

// Fetch address suggestions based on user input
async function fetchAddressSuggestions(query) {
  if (query.length < 3) {
    suggestionsContainer.classList.add('hidden');
    return;
  }

  try {
    const response = await fetch(`${ApiURLs.AddressAutoCompleteURL}?query=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('Network response was not ok');
    const suggestions = await response.json();

    if (suggestions.length > 0) {
      displaySuggestions(suggestions);
    } else {
      suggestionsContainer.classList.add('hidden');
    }
  } catch (error) {
    console.error('Error fetching address suggestions:', error);
    suggestionsContainer.innerHTML = '<p class="p-2 text-red-500">Error fetching suggestions</p>';
  }
}

function displaySuggestions(suggestions) {
  suggestionsContainer.innerHTML = suggestions.map(suggestion =>
    `<div class="suggestion-item block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">${suggestion}</div>`
  ).join('');
  suggestionsContainer.classList.remove('hidden');

  document.querySelectorAll('.suggestion-item').forEach(item => {
    item.addEventListener('click', () => selectSuggestion(item.textContent));
  });
}

function selectSuggestion(suggestion) {
  addressInput.value = suggestion;
  suggestionsContainer.classList.add('hidden');
}

document.addEventListener('click', (event) => {
  if (!suggestionsContainer.contains(event.target) && event.target !== addressInput) {
    suggestionsContainer.classList.add('hidden');
  }
});

document.addEventListener('DOMContentLoaded', () => {
  if (Description) {
    Description.addEventListener('input', () => limitWords(Description, 250));
  }

  if (addressInput) {
    addressInput.addEventListener('input', debounce((event) => fetchAddressSuggestions(event.target.value), 300));
  }

  CompanyTitle.addEventListener('blur', validateCompanyTitle);
  LogoFile.addEventListener('change', validateLogoFile);
  Location.addEventListener('blur', validateLocation);
  CompanyEmail.addEventListener('input', validateEmail);
  NumberOfEmployees.addEventListener('blur', validateCompanySize);
  privacyCheck.addEventListener('change', checkPrivacyPolicy);
  document.querySelectorAll('input[name="category"]').forEach(radio => {
    radio.addEventListener('change', validateCategory);
  });
  

  // Handle form submission
  async function handleSubmit() {
    if (validateForm() && privacyCheck.checked) {
        const formData = new FormData();
        formData.append('title', CompanyTitle.value.trim());
        formData.append('description', Description.value.trim());
        formData.append('logo', LogoFile.files[0]);
        formData.append('location', Location.value.trim());
        formData.append('nature', Nature.value.trim());
        formData.append('email', CompanyEmail.value.trim());
        formData.append('phone_number', PhoneNumber.value.trim());
        formData.append('website_url', WebsiteUrl.value.trim());
        formData.append('linkedin_url', LinkedinUrl.value.trim());
        formData.append('twitter_url', TwitterUrl.value.trim());
        formData.append('facebook_url', FacebookUrl.value.trim());
        formData.append('number_of_employees', NumberOfEmployees.value.trim());
        formData.append('year_established', YearEstablished.value.trim());
        formData.append('annual_revenue', AnnualRevenue.value.trim());
        const selectedCategory = document.querySelector('input[name="category"]:checked');
        if (selectedCategory) {
          formData.append('category', selectedCategory.value);
        } else {
          console.error('Indicate your sector to continue')
        }


        try {
          toggleUIState(true);
          const response = await fetch(UtilApiURLs.CreateCompanyURL, {
            method: 'POST',
            body: formData
          });

          if (!response.ok) throw new Error('Network response was not ok');
            const result = await response.json();
            console.log('Success:', result);
            const email = CompanyEmail.value.trim();
            showSuccessModal(email);
          } catch (error) {
          console.error('Error:', error);
        } finally {
          toggleUIState(false);
        }
    } else {
        if (!privacyCheck.checked) {
          privacyCheckError.classList.remove('hidden');
        }
    }
  }

  CreateCompanyButton.addEventListener('click', handleSubmit);



});