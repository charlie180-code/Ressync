import domain from "../domain.js"

const BaseURL = `${domain}/order/v1/`

const UtilApiURLs = {
    DeletePurchaseRequestURL: `${BaseURL}my_purchases/delete/`,
    PopulatePurchaseDataListURL: `${BaseURL}my_purchases/track_my_product/user`,
    DeletePurchaseRequestURLSales: `${BaseURL}delete_purchase/`,
    DeleteAuthorizationRequestURL: `${BaseURL}delete_request/`,
    PurchaseRequestSendSuccess: `${BaseURL}my_purchases/previous_purchase_requests`,
    AuthorizationSuccessRedirectURL: `${BaseURL}quotes/previouses`,
    checkValidityQuoteURL: `${BaseURL}quote/edit/`,
    DeleteQuoteRequestURL: `${BaseURL}quote/delete/`,
}

export default UtilApiURLs