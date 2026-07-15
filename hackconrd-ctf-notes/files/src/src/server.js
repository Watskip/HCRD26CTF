// src/server.js
const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5015;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.get('/', (req, res) => {
  res.render('index', {});
});

app.get('/note', (req, res) => {
  res.render('note', {
    title: req.query.title,
    content: req.query.content,
    run: req.query.run
  });
});

app.listen(PORT, () => {
  console.log(`HackConRD EJS Notes listening on port ${PORT}`);
});
