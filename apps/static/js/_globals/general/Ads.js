import domain from "../domain.js"

const BaseURL = `${domain}/ads/v1/`

const UtilApiURLs = {
    DeleteAdURL: `${BaseURL}ads/delete_ad/`,
    CreateAdSuccessURL: `${BaseURL}ads/`,
}

export default UtilApiURLs