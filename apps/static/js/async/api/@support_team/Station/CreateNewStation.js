import { sendDataToAPI } from '../../../../UI/AsyncHelpers.js'

const formId = 'pipelineForm';
const endpoint = window.location.pathname;
const buttonId = 'submitBtn';
const spinnerId = 'submitSpinner';
const loadingTextId = 'loadingText';

const validateFn = (value) => value.trim() !== '';


document.getElementById('submitBtn').addEventListener('click', (e) => {
    e.preventDefault();
    sendDataToAPI(
        formId, 
        endpoint, 
        buttonId, 
        spinnerId, 
        loadingTextId, 
        validateFn
    );
});