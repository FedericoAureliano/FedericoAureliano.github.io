window.onscroll = function() {scroller()};
function scroller() {
  var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
  var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  var scrolled = (winScroll / height) * 100;
  // scrolled should be between 0 and 100
  scrolled = Math.min(100, Math.max(0, scrolled));
  document.getElementById("scroller").style.width = scrolled + "%";
}