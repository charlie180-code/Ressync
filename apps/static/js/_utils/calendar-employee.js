import UtilApiURLs from "../_globals/general/Calendar.js";

document.addEventListener('DOMContentLoaded', function() {
  const CompanyIdInput = document.querySelector('#company-id');
  const companyId = CompanyIdInput ? CompanyIdInput.value : null;

  if (!companyId) {
    console.error('Company ID is missing!');
    return;
  }

  var calendarEl = document.getElementById('calendar');
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    locale: 'fr',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    selectable: true,
    editable: true,
    events: UtilApiURLs.GetEventsApiURL + `/${companyId}`
  });
  
  calendar.render();
});
