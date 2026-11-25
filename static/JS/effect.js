/* effects.js - small browser effects.                              [OWNER: Zhi Hui]
   W3 version: only hides the pop-up message. Sound and fireworks are added in W5.
   Nothing here changes your data. */

(function () {
  // Pop-up messages (flash() in Python, <div class="toast"> in base.html) disappear after 2 seconds.
  document.querySelectorAll('.toast').forEach(function (box) {
    setTimeout(function () {
      box.remove();                       // take the message off the page
    }, 2000);                             // 2000 ms = 2 seconds
  });
})();
