module.exports = {
    "extends": "airbnb",
    "parser": "babel-eslint",
    "rules": {
      "react/jsx-filename-extension": ["warn", { "extensions": [".js"] } ],
      "react/destructuring-assignment": ["warn", "always"],
    },
    "env": {
        "browser": true
    },
};
