module.exports = {
    entry: './js/main.js',
    output: {
        path: __dirname + '/planningpoker/static',
        filename: 'bundle.js'
    },
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                query: {
                    presets: ['es2015'],
                    plugins: ['transform-react-jsx', 'transform-object-rest-spread']
                }
            }
        ]
    }
};
