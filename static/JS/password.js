/* password.js - the Show / Hide button in every password box.     [OWNER: Zhi Hui]
   Works on any <input> inside <span class="pw">. Only changes the look, sends nothing. */
document.querySelectorAll('.pw').forEach(function (box) {
  var input = box.querySelector('input');
  var button = document.createElement('button');
  button.type = 'button';                     // "button" so it does not submit the form
  button.className = 'pw-toggle';
  button.textContent = 'Show';

  button.addEventListener('click', function () {
    var hidden = input.type === 'password';
    input.type = hidden ? 'text' : 'password';  // text = letters visible, password = dots
    button.textContent = hidden ? 'Hide' : 'Show';
  });

  box.appendChild(button);
});
