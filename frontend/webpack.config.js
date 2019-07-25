const WebpackVisualizer = require('webpack-visualizer-plugin');


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
        use: 'eslint-loader?{fix: true}',
        test: /\.js$/,
        exclude: /node_modules/,
        enforce: 'pre',
      },
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
    new WebpackVisualizer({
      filename: './dist/webpack.stats.html',
    }),
  ],
};
