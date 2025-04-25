module.exports = {
  content: [
    "apps/templates/includes/inc_top.html",
    "./templates/auth/login.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
