import domain from "../domain.js"

const BaseURL = `${domain}/msg/v1/`

const UtilApiURLs = {
    SendQuoteRequestURL : `${BaseURL}send-message`,
    SendWhatsappMassageURL : `${BaseURL}send-whatsapp-message`,
    StoreSubscriberBasicURL: `${BaseURL}store_a_subscriber`,
    ContactAddedSuccessURL: `${BaseURL}view_contacts`,
    PopulateUserContacts: `${BaseURL}mailbox/contacts/`,
    MessageSentSuccessURL: `${BaseURL}messages/recent/`

}

export default UtilApiURLs