document.addEventListener('DOMContentLoaded', function () {
    var loginButton = document.getElementById('loginButton');
    if (loginButton) {
        loginButton.addEventListener('click', function() {
            var hostedUIURL = loginButton.getAttribute('data-hostedUI-url');
            window.location.href = hostedUIURL;
        });
    }
});
