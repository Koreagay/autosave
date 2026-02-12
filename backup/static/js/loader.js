/**
 * Premium Showcase - JS 로더
 * main.js를 로드합니다. (CSS는 base.html에서 main.css로 한 번에 로드)
 */
(function () {
  var script = document.createElement('script');
  script.src = '/static/js/main.js';
  document.body.appendChild(script);
})();
