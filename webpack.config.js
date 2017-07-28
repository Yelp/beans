const webpack = require('webpack');
const WebpackVisualizer = require('webpack-visualizer-plugin');

const VENDOR = [
  'axios',
  'moment-timezone',
  'react',
  'react-dom',
  'react-redux',
  'react-router',
  'redux',
  'redux-promise',
];

module.exports = {
  entry: {
    app: './js/index.js',
    vendor: VENDOR,
  },
  output: {
    publicPath: __dirname,
    path: __dirname,
    filename: 'dist/bundle/[name].bundle.js',
  },
  module: {
    rules: [
      {
        use: 'eslint-loader?{fix: true}',
        test: /\.js?$/,
        exclude: /node_modules/,
        enforce: 'pre',
      },
      {
        use: 'babel-loader',
        test: /\.js?$/,
        exclude: /node_modules/,
      },
    ],
  },
  devtool: 'source-map',
  devServer: {
    contentBase: './',
  },
  resolve: {
    extensions: ['.js'],
  },
  plugins: [
    new webpack.optimize.CommonsChunkPlugin({
      name: 'vendor',
      minChunks: Infinity,
    }),
    new WebpackVisualizer({
      filename: './dist/webpack.stats.html',
    }),
  ],
};
