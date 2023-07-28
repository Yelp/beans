const path = require('path');
const nconf = require('nconf');

function checkConfig(setting) {
  if (!nconf.get(setting)) {
    throw new Error(
      `You must set ${setting} as an environment variable or in config.json!`,
    );
  }
}

nconf
  .argv()
  .env([
    'CLOUD_BUCKET',
    'NODE_ENV',
    'OAUTH2_CLIENT_ID',
    'OAUTH2_CLIENT_SECRET',
    'OAUTH2_CALLBACK',
    'PORT',
    'SECRET',
  ])
  .file({ file: path.join(__dirname, 'config.json') })
  .defaults({
    CLOUD_BUCKET: '',
    OAUTH2_CLIENT_ID: '',
    OAUTH2_CLIENT_SECRET: '',
    PORT: 8080,
    SECRET: '',
    PROXY: 'http://localhost:5000',
  });

checkConfig('PROJECT');
checkConfig('CLOUD_BUCKET');
checkConfig('OAUTH2_CLIENT_ID');
checkConfig('OAUTH2_CLIENT_SECRET');

module.exports = nconf;
