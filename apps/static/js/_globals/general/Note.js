import domain from "../domain.js"

const BaseURL = `${domain}/note/v1/`

const UtilApiURLs = {
    ManageNoteURL: `${BaseURL}manage/note/`,
    NoteCreationSuccessURL: `${BaseURL}notes/previous_notes`
}

export default UtilApiURLs