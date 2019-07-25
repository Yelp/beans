const express = require('express');
const session = require('express-session');
const cors = require('cors');
const passport = require('passport');
// const { Datastore } = require('@google-cloud/datastore');
const authRoutes = require('./routes/authRoutes');
const config = require('./lib/config');
// const DatastoreStore = require('@google-cloud/connect-datastore')(session);

const app = express();

const corsOptions = {
  origin: `${config.get('PROJECT')}.appspot.com`,
  allowedHeaders: ['Content-Type'],
  optionsSuccessStatus: 200,
};

app.use(cors(corsOptions));

app.set('trust proxy', true);
const sessionConfig = {
  resave: false,
  saveUninitialized: false,
  secret: config.get('SECRET'),
  signed: true,
};

app.use(session(sessionConfig));

// OAuth2
/* eslint-disable consistent-return */
const authRequired = function authRequired(req, res, next) {
  if (!req.user) {
    req.session.oauth2return = req.originalUrl;
    return res.redirect('/auth/google');
  }
  next();
};

app.use(passport.initialize());
app.use(passport.session());
require('./services/passport');

authRoutes(app);
app.use(authRequired);

app.use(express.static(`${__dirname}/static/`));
app.use(express.static(`${__dirname}/dist`));


app.get('/', (req, res) => {
  res.sendFile(`${__dirname}/index.html`);
});

app.get('/user/:email', (req, res) => {
  res.sendFile(`${__dirname}/index.html`);
});

app.get('/meeting_request/:id', (req, res) => {
  res.sendFile(`${__dirname}/index.html`);
});

app.get('/email', (req, res) => {
  res.send({ email: req.user });
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}...`);
});
