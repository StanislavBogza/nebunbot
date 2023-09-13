const express = require('express');
const { Pool } = require('pg');

const app = express();

// Configure your PostgreSQL connection here
const pool = new Pool({
  connectionString: "postgres://jjqnnppq:RrTvXMnxnjIlkFQGKHPlp276viZB567x@snuffleupagus.db.elephantsql.com/jjqnnppq",
});

app.get('/', async (req, res) => {
  try {
    // Connect to the PostgreSQL database
    const client = await pool.connect();

    // Execute a SQL query to retrieve data (replace 'mytable' with your table name)
    const result = await client.query("SELECT * FROM cont_curent WHERE user_id != 666 ORDER BY balanta DESC");
    const records = result.rows;

    // Execute a separate query to calculate the sum of balanta
    const sumResult = await client.query("SELECT ROUND(SUM(balanta)) FROM cont_curent");
    const sumab = sumResult.rows[0].round + " 𝖓𝖊𝖑𝖊𝖎";

    // Release the database connection
    client.release();

    // Send the data as JSON response
    res.json({ records, sumab });
  } catch (err) {
    console.error('Error executing SQL queries:', err);
    res.status(500).send('Internal Server Error');
  }
});


app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
