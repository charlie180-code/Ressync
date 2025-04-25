import domain from "../domain.js"

const BaseURL = `${domain}/career/v1/`

const UtilApiURLs = {
    JobCreationSuccessURL: `${BaseURL}careers/previous_created_jobs`,
    EmployeeEditInfoSuccess: `${BaseURL}careers/employees_table`,
    DeleteEmployeeURL: `${BaseURL}careers/employees/delete_employee/`,
    ApplyJobURL: `${BaseURL}job-openings/apply/`,
    ApplyJobSuccessRedirectURL: `${BaseURL}my-previous-applications`,

}

export default UtilApiURLs