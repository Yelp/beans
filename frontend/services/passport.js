const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const config = require('../lib/config');

passport.use(
  new GoogleStrategy(
    {
      clientID: config.get('OAUTH2_CLIENT_ID'),
      clientSecret: config.get('OAUTH2_CLIENT_SECRET'),
      callbackURL: '/auth/google/callback',
      accessType: 'offline',
    },
    (request, accessToken, refreshToken, profile, done) => {
      const { email } = profile._json; // eslint-disable-line no-underscore-dangle
      done(null, email);
    },
  ),
);

passport.serializeUser((email, done) => {
  done(null, email);
});

passport.deserializeUser((email, done) => {
  done(null, email);
});
