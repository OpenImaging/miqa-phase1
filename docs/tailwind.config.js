// This is a minimal config.
// If you need the full config, get it from here:
// https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
const colors = require('tailwindcss/colors')

module.exports = {
  purge: [
    // If source HTML files are ever added to this project in another directory, include them here
    './_includes/**/*.html',
    './_layouts/**/*.html',
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    fontFamily: {
      'sans': '"Manrope", sans-serif'
    },
    extend: {
      colors: {
        'accent': {
            '50': '#f8fcf3',
            '100': '#f1f8e7',
            '200': '#dbeec3',
            '300': '#c5e49f',
            '400': '#9ad058',
            '500': '#6fbc10',
            '600': '#64a90e',
            '700': '#538d0c',
            '800': '#43710a',
            '900': '#365c08'
        },'secondary': {
            '50': '#fafafa',
            '100': '#f4f4f5',
            '200': '#e4e5e5',
            '300': '#d3d5d6',
            '400': '#b3b5b7',
            '500': '#929598',
            '600': '#838689',
            '700': '#6e7072',
            '800': '#58595b',
            '900': '#48494a'
        },'primary': {
            '50': '#f3f6f9',
            '100': '#e6edf3',
            '200': '#c1d3e2',
            '300': '#9bb9d1',
            '400': '#5184ae',
            '500': '#064F8B',
            '600': '#05477d',
            '700': '#053b68',
            '800': '#042f53',
            '900': '#032744'
        }
      },
      fontSize: {
        '2xs': '.7rem',
        '3xs': '.63rem',
      },
      maxWidth: {
        '2xs': '16rem',
        '3xs': '12rem',
      },
      minWidth: {
        '2xs': '16rem',
        '3xs': '12rem',
      },
      textShadow: {
        '2xl': '0 2px 6px rgba(0, 0, 0, .38), 0 2px 20px rgba(0, 0, 0, .22)',
      },
    },
  },
  variants: {
    extend: {
      borderWidth: ['hover', 'focus', 'group-hover', 'group-focus', 'last'],
      display: ['hover', 'focus', 'group-hover', 'group-focus'],
    },
  },
  plugins: [
    require('tailwindcss-textshadow')
  ],
}
