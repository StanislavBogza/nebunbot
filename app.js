// Replace the database URL with your PostgreSQL URL
const databaseURL = "postgres://jjqnnppq:RrTvXMnxnjIlkFQGKHPlp276viZB567x@snuffleupagus.db.elephantsql.com/jjqnnppq";

const dataTable = document.getElementById("data-table").getElementsByTagName("tbody")[0];

async function fetchData() {
    try {
        const response = await fetch(`/api/data`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Clear the existing table rows
        dataTable.innerHTML = '';

        // Populate the table with data
        data.forEach(row => {
            const newRow = dataTable.insertRow();
            Object.values(row).forEach(value => {
                const cell = newRow.insertCell();
                cell.textContent = value;
            });
        });
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

fetchData();
