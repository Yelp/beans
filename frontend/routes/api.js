const { createProxyMiddleware } = require('http-proxy-middleware');
const config = require('../lib/config');

module.exports = (app) => {
  app.use(createProxyMiddleware('/v1/**', { target: config.get('PROXY') }));
  app.use(createProxyMiddleware('/tasks/**', { target: config.get('PROXY') }));
};
