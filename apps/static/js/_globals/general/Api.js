import domain from "../domain.js";

const BaseURL = `${domain}/api/v1/`;

const ApiURLs = {
    AddressAutoCompleteURL: `${BaseURL}autocomplete-address`,
    GetAirFreightRatesURL : `${BaseURL}get-air-freight-rate`,
    CheckDuplicateCompanyNameURL:`${BaseURL}company/check_duplicate_name`,
    CheckDuplicateEmailURL:`${BaseURL}company/check_duplicate_email`,
    GetRealTimeWeatherURL : `${BaseURL}get-weather/realtime`
}

export default ApiURLs