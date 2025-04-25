import domain from "../domain.js"

const BaseURL = `${domain}/`
const ThirdBaseURL = `${domain}/auth/`

const UtilApiURLs = {
    LoginSuccessRedirectURL: `${BaseURL}user_home`,
    SignupSuccessRedirectURL: `${BaseURL}auth/login`,
    CreateCompanyURL:`${ThirdBaseURL}company/register`,
    CheckDuplicateEmailURL:`${BaseURL}check_duplicate_email`,
    CompanyCreationSuccessURL: `${ThirdBaseURL}company/register_success`,
    SignupNewUser: `${ThirdBaseURL}signup`,
}

export default UtilApiURLs