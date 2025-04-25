import ApiURLs from '../../_globals/general/Api.js';
import validateForm from './RegisterCompany.js'

const CompanyTitle = document.querySelector("#Title");
const CompanyTitleEmptyError = document.querySelector("#EmptyNameError");
const CompanyEmail = document.querySelector("#Email");
const CreateCompanyButton = document.querySelector("#CreateCompanyButton");
const DuplicateEmailError = document.querySelector("#DuplicateEmailError");
const InvalidEmailAddress = document.querySelector("#InvalidEmailAddress");
const EmptyEmailAddress = document.querySelector("#EmptyEmailAddress");

async function checkDuplicateCompanyName(title) {
  try {
    const response = await fetch(`${ApiURLs.CheckDuplicateCompanyNameURL}?title=${encodeURIComponent(title)}`);
    if (!response.ok) throw new Error('Network response was not ok');
    const result = await response.json();

    if (result.exists) {
      document.querySelector("#DuplicateCompanyNameError").classList.remove('hidden');
      CreateCompanyButton.disabled = true;
    } else {
      document.querySelector("#DuplicateCompanyNameError").classList.add('hidden');
      CreateCompanyButton.disabled = false;
    }
  } catch (error) {
    console.error('Error checking duplicate company name:', error);
    document.querySelector("#DuplicateCompanyNameError").classList.add('hidden');
    CreateCompanyButton.disabled = true;
  }
}

async function checkDuplicateEmail(email) {
  try {
    const response = await fetch(`${ApiURLs.CheckDuplicateEmailURL}?email=${encodeURIComponent(email)}`);
    if (!response.ok) throw new Error('Network response was not ok');
    const result = await response.json();

    if (result.exists) {
      DuplicateEmailError.classList.remove('hidden');
      CreateCompanyButton.disabled = true;
    } else {
      DuplicateEmailError.classList.add('hidden');
      CreateCompanyButton.disabled = false;
    }
  } catch (error) {
    console.error('Error checking duplicate email:', error);
    DuplicateEmailError.classList.add('hidden');
    CreateCompanyButton.disabled = true;
  }
}

function validateCompanyTitle() {
  if (CompanyTitle.value.trim() === '') {
    CompanyTitleEmptyError.classList.remove('hidden');
  } else {
    CompanyTitleEmptyError.classList.add('hidden');
    checkDuplicateCompanyName(CompanyTitle.value.trim());
  }
  validateForm();
}

function validateEmail() {
  const emailPattern = /^[^\s@]+@[^\s@]+$/;
  if (CompanyEmail.value.trim() === '') {
    InvalidEmailAddress.classList.add('hidden');
    EmptyEmailAddress.classList.remove('hidden');
    return false;
  } else if (!emailPattern.test(CompanyEmail.value.trim())) {
    InvalidEmailAddress.classList.remove('hidden');
    EmptyEmailAddress.classList.add('hidden');
    return false;
  } else {
    InvalidEmailAddress.classList.add('hidden');
    EmptyEmailAddress.classList.add('hidden');
    checkDuplicateEmail(CompanyEmail.value.trim());
    return true;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  CompanyTitle.addEventListener('blur', validateCompanyTitle);
  CompanyEmail.addEventListener('input', validateEmail);
});
