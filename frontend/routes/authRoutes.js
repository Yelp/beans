
const passport = require('passport');

module.exports = (app) => {
  app.get(
    '/auth/google',
    (req, res, next) => {
      if (req.query.return) {
        req.session.oauth2return = req.query.return;
      }
      next();
    },
    passport.authenticate('google', { scope: ['email'] }),
  );

  app.get(
    '/auth/google/callback',
    passport.authenticate('google'),
    (req, res) => {
      const redirect = req.session.oauth2return || '/';
      delete req.session.oauth2return;
      res.redirect(redirect);
    },
  );

  app.get('/auth/logout', (req, res) => {
    req.logout();
    res.redirect('/');
  });
};
