const express = require('express');
const { Client } = require('pg');
const app = express();

const client = new Client({
  user: 'admin',
  password: 'mysecretpassword',
  database: 'users'
});

client.connect();

app.get('/hello', (req, res) => {
  const name = req.query.name;
  res.send(`Hello, ${name}`);
});

app.get('/user/:id', async (req, res) => {
  const id = req.params.id;
  const result = await client.query(`SELECT * FROM users WHERE id = ${id}`);
  res.json(result.rows);
});

console.log('Connect string includes password:', client.connectionParameters.password);

app.listen(8080, () => console.log('Listening on 8080'));
