const express = require("express");
const session = require("express-session");
const cors = require("cors");
const passport = require("passport");
const authRoutes = require("./routes/authRoutes");
const apiRoutes = require("./routes/api");
const config = require("./lib/config");

const app = express();

// Initialize the state store
app.locals.stateStore = new Map();

const corsOptions = {
  origin: [`${config.get("PROJECT")}.appspot.com`, "localhost:5000"],
  allowedHeaders: ["Content-Type"],
  optionsSuccessStatus: 200,
};

app.use(cors(corsOptions));

app.set("trust proxy", true);
const sessionConfig = {
  resave: false,
  saveUninitialized: false,
  secret: config.get("SECRET"),
  signed: true,
};

app.use(session(sessionConfig));

// OAuth2
/* eslint-disable consistent-return */
const authRequired = function authRequired(req, res, next) {
  if (!req.user) {
    const params = new URLSearchParams({ return: req.originalUrl });
    return res.redirect(`/auth/google?${params.toString()}`);
  }
  next();
};

app.use(passport.initialize());
app.use(passport.session());
require("./services/passport");

authRoutes(app);
app.use(authRequired);

app.use(express.static(`${__dirname}/static/`));
app.use(express.static(`${__dirname}/dist`));

app.get("/", (req, res) => {
  res.sendFile(`${__dirname}/index.html`);
});

app.get("/user/:email", (req, res) => {
  res.sendFile(`${__dirname}/index.html`);
});

app.get("/meeting_request/:id", (req, res) => {
  res.sendFile(`${__dirname}/index.html`);
});

app.get("/subscribe/:id", (req, res) => {
  res.sendFile(`${__dirname}/index.html`);
});

app.get("/admin/subscriptions", (req, res) => {
  res.sendFile(`${__dirname}/index.html`);
});

app.get("/admin/subscriptions/create", (req, res) => {
  res.sendFile(`${__dirname}/index.html`);
});

app.get("/admin/subscriptions/:id", (req, res) => {
  res.sendFile(`${__dirname}/index.html`);
});

app.get("/email", (req, res) => {
  res.send({ email: req.user });
});

apiRoutes(app);

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`Server listening on port ${PORT}...`);
});
