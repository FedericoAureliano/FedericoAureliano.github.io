const btn = document.querySelector(".switch-mode");
const theme = document.querySelector("#theme-link");

if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    theme.href = "dark.css";
    document.getElementById("mode").checked = true;
}

btn.addEventListener("change", function() {
  // Swap out the URL for the different stylesheets
  if (document.getElementById("mode").checked) {
    theme.href = "dark.css";
  } else {
    theme.href = "light.css";
  }
});