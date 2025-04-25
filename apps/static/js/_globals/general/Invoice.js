import domain from "../domain.js"

const BaseURL = `${domain}/invoice/v1/`

const UtilApiURLs = {
    EditInvoiceRequestURL: `${BaseURL}edit_invoice/`,
    DeleteInvoiceRequestURL: `${BaseURL}delete_invoice/`,
}

export default UtilApiURLs