const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5014;

const LIBRARY_ROOT = path.join(__dirname, '..', 'library');

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

/**
 * Flawed sanitizer: deletes every literal "../" substring once against the raw input.
 * That is not the same as normalizing a path; surplus dots/slashes can leave a
 * working "../" after the filter runs.
 */
function sanitizeLibraryFilename(raw) {
  if (typeof raw !== 'string' || raw.length === 0) {
    return { error: 'Missing or invalid file parameter' };
  }
  if (raw.length > 512) {
    return { error: 'File parameter too long' };
  }
  if (raw.includes('\0')) {
    return { error: 'Invalid file parameter' };
  }
  if (raw.startsWith('/') || raw.startsWith('\\')) {
    return { error: 'Path must be relative to the library' };
  }
  if (!/\.txt$/i.test(raw)) {
    return { error: 'Only .txt documents can be read' };
  }
  const stripped = raw.split('../').join('');
  return { filename: stripped };
}

app.get('/', (req, res) => {
  const books = ['lordrdna.txt', 'lich.txt', 'G4l1l30.txt'];
  res.render('index', { books });
});

app.get('/book', (req, res) => {
  const rawParam = req.query.file;
  const { error, filename } = sanitizeLibraryFilename(rawParam);

  if (error) {
    return res.status(400).send(error);
  }

  const filePath = path.join(LIBRARY_ROOT, filename);

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error('Error reading file:', err.message);
      return res.status(404).render('book', {
        filename: rawParam,
        content: '[!] Error: el libro no existe o no se puede leer.'
      });
    }

    res.render('book', {
      filename: rawParam,
      content: data
    });
  });
});

app.listen(PORT, () => {
  console.log(`HackConRD Library listening on port ${PORT}`);
});
