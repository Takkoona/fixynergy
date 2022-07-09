const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");

const srcDir = "websrc";

module.exports = {
    mode: "development",
    entry: path.resolve(__dirname, srcDir, "index.js"),
    output: {
        path: path.resolve(__dirname, "docs"),
        filename: "bundle.js",
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                loader: "babel-loader",
                exclude: /node_modules/,
                options: {
                    presets: ["@babel/preset-react", "@babel/preset-env"]
                }
            }
        ]
    },
    devtool: "source-map",
    plugins: [
        new HtmlWebpackPlugin({
            template: path.resolve(__dirname, srcDir, "template.html")
        })
    ]
}
