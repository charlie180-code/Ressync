import domain from "../domain.js";

const BaseURL = `${domain}/order/v1/`

const UtilApiURLs = {
    AddStoreURL: `${BaseURL}add_store`,
    EditStoreURL: `${BaseURL}edit_store/`,
    DeleteStoreURL: `${BaseURL}delete_store/`,
    DeleteStoreURL : `${domain}/stores`,
    EditStoreURL : `${domain}/stores`,
    GetStoreDetailsURL : `${BaseURL}get-store_details/`,
    ManageProductURL: `${domain}/products`,
    GetProductBarCodeURL : `${BaseURL}download_barcode/`,
}

export default UtilApiURLs