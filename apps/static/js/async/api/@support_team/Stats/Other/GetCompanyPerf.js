import domain from "../../../../../_globals/domain.js";

const companyId = document.getElementById('company-id').value;

document.addEventListener('DOMContentLoaded', function() {
    fetch(`${domain}/api/dashboard/company/other/stats/${companyId}`)
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          document.getElementById('employee-count').textContent = data.data.employees.total_employees;
          const employeeChange = document.getElementById('employee-change');
          const employeeChangeValue = data.data.employees.percentage_change;
          employeeChange.innerHTML = `<span class="${employeeChangeValue >= 0 ? 'text-success' : 'text-danger'} font-weight-bolder">${employeeChangeValue >= 0 ? '+' : ''}${employeeChangeValue}% </span>than last month`;
          
          document.getElementById('expense-total').textContent = '$' + data.data.expenses.total_expenses.toLocaleString();
          const expenseChange = document.getElementById('expense-change');
          const expenseChangeValue = data.data.expenses.percentage_change;
          expenseChange.innerHTML = `<span class="${expenseChangeValue >= 0 ? 'text-danger' : 'text-success'} font-weight-bolder">${expenseChangeValue >= 0 ? '+' : ''}${expenseChangeValue}% </span>than last month`;
          
          document.getElementById('project-count').textContent = data.data.projects.total_projects;
          document.getElementById('max-budget-amount').textContent = '$' + data.data.projects.max_budget.toLocaleString();
          document.getElementById('max-budget').textContent = `Max: $${data.data.projects.max_budget.toLocaleString()}`;
        }
      })
      .catch(error => {
        console.error('Error fetching dashboard data:', error);
        document.querySelectorAll('.spinner-border').forEach(spinner => {
          spinner.parentElement.textContent = 'Error loading data';
        });
      });
});