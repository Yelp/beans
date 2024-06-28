const { createProxyMiddleware } = require("http-proxy-middleware");
const config = require("../lib/config");

module.exports = (app) => {
  app.use(
    createProxyMiddleware({
      target: config.get("PROXY"),
      pathFilter: "/v1/**",
    }),
  );
  app.use(
    createProxyMiddleware({
      target: config.get("PROXY"),
      pathFilter: "/tasks/**",
    }),
  );
};
