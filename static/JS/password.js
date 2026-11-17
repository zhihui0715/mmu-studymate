/* password.js - the Show / Hide button inside every password box (<span class="pw">). */
document.querySelectorAll('.pw').forEach(function (box) {
  var input = box.querySelector('input');
  var button = document.createElement('button');
  button.type = 'button';                 // "button" so clicking it does not submit the form
  button.className = 'pw-toggle';
  button.textContent = 'Show';

  button.addEventListener('click', function () {
    var hidden = input.type === 'password';
    input.type = hidden ? 'text' : 'password';   // text = letters visible, password = dots
    button.textContent = hidden ? 'Hide' : 'Show';
  });

  box.appendChild(button);
});