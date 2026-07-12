const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

config.resolver.alias = {
  '@': './src',
  '@components': './src/components',
  '@screens': './src/screens',
  '@navigation': './src/navigation',
  '@store': './src/store',
  '@services': './src/services',
  '@utils': './src/utils',
  '@types': './src/types',
};

module.exports = config;
