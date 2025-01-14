document.addEventListener("DOMContentLoaded", () => {
    const authButton = document.getElementById("authButton");

    // Перевіряємо, чи користувач авторизований
    const isLoggedIn = localStorage.getItem("isLoggedIn");

    if (isLoggedIn === "true") {
        authButton.textContent = "Logout";
    } else {
        authButton.textContent = "Login";
    }

    authButton.addEventListener("click", () => {
        if (authButton.textContent === "Logout") {
            // Якщо кнопка в стані Logout - виконуємо вихід
            localStorage.removeItem("isLoggedIn");
            authButton.textContent = "Login";
            alert("You have been logged out.");
        } else {
            // Якщо кнопка в стані Login - перенаправляємо на сторінку логіну
            window.location.href = "login.html";
        }
    });
});
