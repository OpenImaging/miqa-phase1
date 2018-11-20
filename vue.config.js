const CopyPlugin = require('copy-webpack-plugin');
const path = require('path');

module.exports = {
  baseUrl: process.env.NODE_ENV === 'production'
    ? '/'
    : '/',
  configureWebpack: {
    module: {
      rules: [
        {
          test: /\.worker\.js$/,
          include: /node_modules(\/|\\)vtk\.js(\/|\\)/,
          use: [
            {
              loader: 'worker-loader',
              options: { inline: true, fallback: false },
            },
          ],
        }
      ]
    },
    plugins: [
      new CopyPlugin([
        {
          from: path.join(__dirname, 'node_modules', 'itk'),
          to: 'itk',
        }
      ])
    ]
  },
  chainWebpack: config => {
    config.module
      .rule('glsl')
      .test(/\.glsl$/)
      .include
      .add(/vtk\.js(\/|\\)/)
      .end()
      .use()
      .loader('shader-loader')
  }
}
