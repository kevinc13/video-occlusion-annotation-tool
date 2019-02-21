'use strict'
const path = require('path')
let BundleTracker = require('webpack-bundle-tracker')

function resolve (dir) {
  return path.join(__dirname, '..', dir)
}

module.exports = {
  outputDir: 'dist',
  publicPath: process.env.NODE_ENV === 'production'
    ? '/static/'
    : 'http://localhost:8080',
  configureWebpack: {
    plugins: [
      new BundleTracker({ filename: './webpack-stats.json' })
    ],
    resolve: {
      alias: {
        '__SHARED_STATIC__': resolve('shared_static'),
      }
    }
  },
  devServer: {
    headers: {
      'Access-Control-Allow-Origin': '\*'
    }
  }
}
