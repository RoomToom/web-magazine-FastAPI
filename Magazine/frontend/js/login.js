document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const registerButton = document.getElementById("registerButton");

    // Функція для показу повідомлень про помилки
    const showError = (message) => {
        alert(message);
    };

    // Функція для валідації пошти
    const isValidEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    // Обробка логіну
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        if (!email || !password) {
            showError("Please enter both email and password.");
            return;
        }

        if (!isValidEmail(email)) {
            showError("Invalid email format.");
            return;
        }

        fetch("http://127.0.0.1:8000/auth/token", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ username: email, password: password }),
        })
            .then((response) => {
                if (!response.ok) {
                    if (response.status === 400) {
                        throw new Error("Invalid email or password.");
                    }
                    throw new Error("Invalid email or password.");
                }
                return response.json();
            })
            .then((data) => {
                alert("Login successful!");
                localStorage.setItem("token", data.access_token);
                window.location.href = "index.html";
            })
            .catch((error) => showError(error.message));
    });

    // Реєстрація адміністратора
    registerButton.addEventListener("click", (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        if (!email || !password) {
            showError("Please enter both email and password to register.");
            return;
        }

        if (!isValidEmail(email)) {
            showError("Invalid email format.");
            return;
        }

        fetch("http://127.0.0.1:8000/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email, password: password }),
        })
            .then((response) => {
                if (!response.ok) {
                    if (response.status === 400) {
                        throw new Error("Email already registered.");
                    }
                    throw new Error("An error occurred during registration.");
                }
                return response.json();
            })
            .then(() => {
                alert("Account created successfully!");
            })
            .catch((error) => showError(error.message));
    });
});
