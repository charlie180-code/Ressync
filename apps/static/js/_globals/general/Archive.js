import domain from "../domain.js"

const BaseURL = `${domain}/archive/v1/`

const UtilApiURLs = {
    ManageFolderURL: `${BaseURL}folders`,
    ChangeFolderStatusURL : `${BaseURL}folders`,
    SaveFilesURL: `${BaseURL}save_folder_files`,
    GetFolderListURL: `${BaseURL}get_folders_list`,
    QueryBook: `${BaseURL}search_books`,
    QueryAudioBook: `${BaseURL}search_audio_books`
}

export default UtilApiURLs