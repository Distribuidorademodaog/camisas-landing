// google-contacts.js
const fs = require('fs');
const readline = require('readline');
const { google } = require('googleapis');

const SCOPES = ['https://www.googleapis.com/auth/contacts'];
const TOKEN_PATH = 'token.json';

const credentials = require('./credenciales-oauth.json');

function authorize(callback) {
  const { client_secret, client_id, redirect_uris } = credentials.installed;
  const oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);

  fs.readFile(TOKEN_PATH, (err, token) => {
    if (err) return getAccessToken(oAuth2Client, callback);
    oAuth2Client.setCredentials(JSON.parse(token));
    callback(oAuth2Client);
  });
}

function getAccessToken(oAuth2Client, callback) {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });
  console.log('🔗 Abre este link en tu navegador para autorizar:\n', authUrl);
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  rl.question('\n📋 Pega aquí el código que aparece después de autorizar: ', (code) => {
    rl.close();
    oAuth2Client.getToken(code, (err, token) => {
      if (err) return console.error('❌ Error recuperando token', err);
      oAuth2Client.setCredentials(token);
      fs.writeFileSync(TOKEN_PATH, JSON.stringify(token));
      callback(oAuth2Client);
    });
  });
}

function agregarContacto(auth, nombre, telefono, correo) {
  const service = google.people({ version: 'v1', auth });
  service.people.createContact({
    requestBody: {
      names: [{ givenName: nombre }],
      phoneNumbers: [{ value: telefono }],
      emailAddresses: [{ value: correo }],
    },
  }, (err, res) => {
    if (err) return console.error('❌ Error al guardar contacto:', err);
    console.log('✅ Contacto guardado correctamente:', nombre);
  });
}

// Uso desde la terminal:
// node google-contacts.js "Juan Perez" "+573001234567" "correo@ejemplo.com"
const [,, nombre, telefono, correo] = process.argv;
authorize((auth) => agregarContacto(auth, nombre, telefono, correo));
