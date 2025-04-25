import domain from '../../../_globals/domain.js'
const companyIdInput = document.getElementById('company-id');

async function fetchData(endpoint, params) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`${domain}/insights/v1/${endpoint}?${query}`);
    return response.json();
  }
  
  async function initializeCharts() {
    // Fetching data
    const companyId = companyIdInput.value;
  
    // Fetch student count data
    const studentCountData = await fetchData('student-count', { company_id: companyId });
    const studentCount = studentCountData.student_count || [30, 50, 80, 120, 150, 180, 200]; // Default data if API fails
  
    // Fetch data size data
    const dataSizeData = await fetchData('data-size', { company_id: companyId });
    const dataSize = dataSizeData.data_size || [100, 120, 140, 160, 180, 200, 220]; // Default data if API fails
  
    // Fetch task completion data
    const taskCompletionData = await fetchData('session-count', { company_id: companyId });
    const taskCompletion = taskCompletionData.session_count || [30, 50, 80, 120, 150, 180, 200]; // Default data if API fails
  
    // Initialize charts with fetched data
  
    // Student Count Chart
    const ctx1 = document.getElementById("chart-student-count").getContext("2d");
    new Chart(ctx1, {
      type: "bar",
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"], // Replace with actual labels if different
        datasets: [{
          label: "Students",
          backgroundColor: "rgba(255, 255, 255, .8)",
          data: studentCount, // Use the fetched student count data
          maxBarThickness: 6
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          }
        },
        interaction: {
          intersect: false,
          mode: 'index',
        },
        scales: {
          y: {
            grid: {
              drawBorder: false,
              display: true,
              color: 'rgba(255, 255, 255, .2)'
            },
            ticks: {
              beginAtZero: true,
              color: "#fff"
            },
          },
          x: {
            grid: {
              drawBorder: false,
              display: true,
              color: 'rgba(255, 255, 255, .2)'
            },
            ticks: {
              color: '#f8f9fa',
            }
          },
        },
      },
    });
  
    // Data Size Chart
    const ctx2 = document.getElementById("chart-data-size").getContext("2d");
    new Chart(ctx2, {
      type: "line",
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"], // Replace with actual labels if different
        datasets: [{
          label: "Data Size (MB)",
          backgroundColor: "transparent",
          borderColor: "rgba(255, 255, 255, .8)",
          data: dataSize, // Use the fetched data size data
          borderWidth: 4,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          }
        },
        interaction: {
          intersect: false,
          mode: 'index',
        },
        scales: {
          y: {
            grid: {
              drawBorder: false,
              display: true,
              color: 'rgba(255, 255, 255, .2)'
            },
            ticks: {
              color: '#f8f9fa',
            },
          },
          x: {
            grid: {
              drawBorder: false,
              display: false,
            },
            ticks: {
              color: '#f8f9fa',
            }
          },
        },
      },
    });
  
    // Task Completion Chart
    const ctx3 = document.getElementById("chart-task-completion").getContext("2d");
    new Chart(ctx3, {
      type: "line",
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"], // Replace with actual labels if different
        datasets: [{
          label: "Tasks Completed",
          backgroundColor: "transparent",
          borderColor: "rgba(255, 255, 255, .8)",
          data: taskCompletion, // Use the fetched task completion data
          borderWidth: 4,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          }
        },
        interaction: {
          intersect: false,
          mode: 'index',
        },
        scales: {
          y: {
            grid: {
              drawBorder: false,
              display: true,
              color: 'rgba(255, 255, 255, .2)'
            },
            ticks: {
              color: '#f8f9fa',
            },
          },
          x: {
            grid: {
              drawBorder: false,
              display: false,
            },
            ticks: {
              color: '#f8f9fa',
            }
          },
        },
      },
    });
  }
  
  document.addEventListener('DOMContentLoaded', initializeCharts);
  