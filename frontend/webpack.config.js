const ESLintPlugin = require('eslint-webpack-plugin');

module.exports = {
  entry: {
    app: './index.js',
  },
  output: {
    publicPath: __dirname,
    path: __dirname,
    filename: 'dist/bundle/app.bundle.js',
  },
  module: {
    rules: [
      {
        use: 'babel-loader',
        test: /\.js$/,
        exclude: /node_modules/,
      },
    ],
  },
  devtool: 'source-map',
  resolve: {
    extensions: ['.js'],
  },
  plugins: [
    new ESLintPlugin(),
  ],
};
