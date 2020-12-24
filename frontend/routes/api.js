const proxy = require('http-proxy-middleware');
const config = require('../lib/config');

module.exports = (app) => {
  app.use(proxy('/v1/**',
    { target: config.get('PROXY') }));
  app.use(proxy('/tasks/**',
    { target: config.get('PROXY') }));
};
