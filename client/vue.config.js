const webpack = require("webpack");
const CopyPlugin = require("copy-webpack-plugin");
const path = require("path");

module.exports = {
  devServer: {
    port: 8081,
    public: process.env.PUBLIC_ADDRESS
  },
  publicPath: process.env.VUE_APP_STATIC_PATH,
  configureWebpack: {
    module: {
      rules: [
        {
          test: /\.worker\.js$/,
          include: /node_modules(\/|\\)vtk\.js(\/|\\)/,
          use: [
            {
              loader: "worker-loader",
              options: { inline: true, fallback: false }
            }
          ]
        }
      ]
    },
    plugins: [
      new CopyPlugin([
        {
          from: path.join(__dirname, "node_modules", "itk"),
          to: "itk"
        }
      ]),
      new webpack.DefinePlugin({
        "process.env": {
          VERSION: JSON.stringify(require("./package.json").version)
        }
      }),
      new webpack.EnvironmentPlugin(["MIQA_SESSION_TIMEOUT"])
    ]
  },
  chainWebpack: config => {
    config.module
      .rule("glsl")
      .test(/\.glsl$/)
      .include.add(/vtk\.js(\/|\\)/)
      .end()
      .use()
      .loader("shader-loader");
  }
};
