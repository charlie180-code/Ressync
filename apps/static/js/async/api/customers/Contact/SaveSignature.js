import { sendDataToAPI } from "../../../../UI/AsyncHelpers.js";
import domain from '../../../../_globals/domain.js'

const CreateSignatureForm = 'signature-form';
const CreateSignatureButton = 'CreateSignatureButton';
const Spinner = 'Spinner';
const LoadingText = 'LoadingText';
const ButtonText = 'ButtonText';
const UserId = document.querySelector('#UserId').value;
const EndPoint = `${domain}/msg/v1/email-signature/${UserId}`;


const validateFields = () =>{
    return true
}

document.querySelector('#CreateSignatureButton').addEventListener('click', async ()=>{
    const response = await sendDataToAPI(
        CreateSignatureForm,
        EndPoint,
        CreateSignatureButton,
        Spinner,
        LoadingText,
        ButtonText,
        validateFields(),
        {'method': 'POST'}
    );
    
    if (response.success && window.signaturePreview) {
        window.signaturePreview.updateBadgeUrls(response.badges || []);
    }
});