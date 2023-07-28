module.exports = {
  extends: 'airbnb',
  parser: '@babel/eslint-parser',
  rules: {
    'react/jsx-filename-extension': ['warn', { extensions: ['.js'] }],
    'react/destructuring-assignment': ['warn', 'always'],
  },
  env: {
    browser: true,
  },
};
