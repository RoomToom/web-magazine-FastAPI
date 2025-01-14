document.addEventListener("DOMContentLoaded", () => {
    const authButton = document.getElementById("authButton");

    const token = localStorage.getItem("token");

    if (token) {
        authButton.textContent = "Logout";
        authButton.addEventListener("click", () => {
            localStorage.removeItem("token");
            alert("You have logged out!");
            window.location.href = "index.html";
        });
    } else {
        authButton.textContent = "Login";
        authButton.addEventListener("click", () => {
            window.location.href = "login.html";
        });
    }
});
