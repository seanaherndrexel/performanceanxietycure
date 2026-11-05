(function(){
  var now = Date.now();
  function ls(k, v){ try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch(e){ return null; } }
  function two(n){ return (n < 10 ? '0' : '') + n; }

  // 15% popup: appears after 5 minutes on the site, once per visitor, and truly expires after 10 minutes.
  var pop = document.getElementById('pop');
  if (!pop || ls('pac_pop_done') || /\/(get|thanks)\//.test(location.pathname)) return;
  var first = parseInt(ls('pac_first_seen') || '0', 10);
  if (!first) { first = now; ls('pac_first_seen', String(now)); }
  var shownAt = parseInt(ls('pac_pop_at') || '0', 10);
  var LIMIT = 10 * 60 * 1000;
  function close(){ pop.hidden = true; ls('pac_pop_done', '1'); }
  function open(){
    if (!shownAt) { shownAt = Date.now(); ls('pac_pop_at', String(shownAt)); }
    var left = shownAt + LIMIT - Date.now();
    if (left <= 0) { close(); return; }
    pop.hidden = false;
    var t = setInterval(function(){
      var r = Math.max(0, Math.floor((shownAt + LIMIT - Date.now()) / 1000));
      pop.querySelector('.js-pop-cd').textContent = Math.floor(r / 60) + ':' + two(r % 60);
      if (r === 0) { clearInterval(t); close(); }
    }, 1000);
  }
  pop.querySelector('.pop-x').onclick = close;
  pop.querySelector('.pop-no').onclick = close;
  pop.addEventListener('click', function(e){ if (e.target === pop) close(); });
  if (shownAt) { open(); return; }
  var wait = Math.max(0, first + 5 * 60 * 1000 - now);
  setTimeout(open, wait);
})();
