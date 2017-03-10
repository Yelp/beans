const VENDOR = [
  'axios',
  'react',
  'react-router',
  'react-dom',
  'redux-form',
  'redux-promise',
];

module.exports = {
  entry: {
    app: './js/index.jsx',
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
        test: /\.jsx?$/,
        loader: 'eslint-loader?{fix: true}',
        exclude: /node_modules/,
        enforce: 'pre',
      },
      {
        use: 'babel-loader',
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
      },
    ],
  },
  devtool: 'source-map',
  devServer: {
    contentBase: './',
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};
