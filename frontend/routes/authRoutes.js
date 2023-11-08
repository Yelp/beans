const crypto = require("crypto");
const passport = require("passport");

module.exports = (app) => {
  app.get("/auth/google", (req, res, next) => {
    crypto.randomBytes(128, (err, buff) => {
      if (err) {
        throw err;
      }
      const state = buff.toString("hex");
      app.locals.stateStore.set(state, { returnUrl: req.query.return || "/" });
      const authenticator = passport.authenticate("google", {
        scope: ["email"],
        state,
      });
      authenticator(req, res, next);
    });
  });

  app.get(
    "/auth/google/callback",
    passport.authenticate("google"),
    (req, res) => {
      const { state } = req.query;
      if (app.locals.stateStore.has(state)) {
        const redirectUrl = app.locals.stateStore.get(state).returnUrl;
        app.locals.stateStore.delete(state);
        res.redirect(redirectUrl);
      } else {
        // If we don't have anything in the state store then treat
        // the login as invalid
        res.sendStatus(403);
      }
    },
  );

  app.get("/auth/logout", (req, res) => {
    req.logout();
    res.redirect("/");
  });
};
