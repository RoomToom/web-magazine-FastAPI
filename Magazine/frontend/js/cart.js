document.addEventListener("DOMContentLoaded", () => {
    const cartButton = document.getElementById("cartButton");
    const cartModal = $('#cartModal'); // Використовуємо jQuery для модального вікна Bootstrap
    const cartItems = document.getElementById("cartItems");
    const checkoutButton = document.getElementById("checkoutButton");

    const DELIVERY_FEE = 50;
    const cart = [];

    const renderCartItems = () => {
    cartItems.innerHTML = "";

     if (cart.length === 0) {
            cartItems.innerHTML = `<p class="text-center text-muted">Your cart is empty.</p>`;
            totalAmountSpan.textContent = `$${DELIVERY_FEE.toFixed(2)}`; // Показуємо тільки доставку
    } else {
        let totalAmount = 0;
        cart.forEach(item => {
            const itemHTML = `
                <div class="cart-item row align-items-center mb-3">
                    <div class="col-3">
                        <img src="/static/images/products/prod${item.product_id}.webp" alt="${item.name}" class="img-fluid rounded">
                    </div>
                    <div class="col-6">
                        <h5>${item.name}</h5>
                        <p>Price: $${item.price.toFixed(2)}</p>
                        <div class="quantity-controls">
                            <button class="btn btn-sm btn-outline-primary decrement" data-id="${item.id}">-</button>
                            <span class="mx-2">${item.quantity}</span>
                            <button class="btn btn-sm btn-outline-primary increment" data-id="${item.id}">+</button>
                        </div>
                    </div>
                    <div class="col-2 text-right">
                        <p>$${(item.price * item.quantity).toFixed(2)}</p>
                    </div>
                    <div class="col-1 text-right">
                        <button class="btn btn-sm btn-outline-danger remove" data-id="${item.id}">&times;</button>
                    </div>
                </div>
            `;
            cartItems.innerHTML += itemHTML;
            totalAmount += (item.price * item.quantity)+50;
        });
        document.getElementById("totalAmount").textContent = `$${totalAmount.toFixed(2)}`;
    }
};

    const updateCart = () => {
        const token = localStorage.getItem("token");

        fetch("http://127.0.0.1:8000/cart", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(data => {
            cart.length = 0;
            data.forEach(item => {
                cart.push({
                    id: item.id,
                    product_id: item.product.id,
                    name: item.product.name,
                    price: item.product.price,
                    quantity: item.quantity
                });
            });
            renderCartItems();
        })
        .catch(error => console.error("Error fetching cart items:", error));
    };

    cartButton.addEventListener("click", () => {
        updateCart();
        cartModal.modal('show'); // Відкриття модального вікна
    });

    cartItems.addEventListener("click", (event) => {
        const target = event.target;
        const id = parseInt(target.getAttribute("data-id"), 10);

        if (target.classList.contains("increment")) {
            const item = cart.find(item => item.id === id);
            item.quantity += 1;

            fetch(`http://127.0.0.1:8000/cart/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({ quantity: item.quantity })
            })
            .then(() => updateCart())
            .catch(error => console.error("Error updating quantity:", error));
        } else if (target.classList.contains("decrement")) {
            const item = cart.find(item => item.id === id);
            if (item.quantity > 1) {
                item.quantity -= 1;

                fetch(`http://127.0.0.1:8000/cart/${id}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${localStorage.getItem("token")}`
                    },
                    body: JSON.stringify({ quantity: item.quantity })
                })
                .then(() => updateCart())
                .catch(error => console.error("Error updating quantity:", error));
            } else {
                fetch(`http://127.0.0.1:8000/cart/${id}`, {
                    method: "DELETE",
                    headers: {
                        "Authorization": `Bearer ${localStorage.getItem("token")}`
                    }
                })
                .then(() => updateCart())
                .catch(error => console.error("Error removing item:", error));
            }
        } else if (target.classList.contains("remove")) {
            fetch(`http://127.0.0.1:8000/cart/${id}`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                }
            })
            .then(() => updateCart())
            .catch(error => console.error("Error removing item:", error));
        }
    });

    checkoutButton.addEventListener("click", () => {
        const token = localStorage.getItem("token");
        if (!token) {
            alert("Please log in to proceed to checkout.");
            return;
        }

        fetch("http://127.0.0.1:8000/orders", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        })
        .then(response => {
            if (!response.ok) throw new Error("Failed to create order");
            return response.json();
        })
        .then(() => {
            alert("Order placed successfully!");
            cart.length = 0; // Очищуємо корзину
            renderCartItems();
            cartModal.modal('hide'); // Закриваємо модальне вікно
        })
        .catch(error => console.error("Error during checkout:", error));
    });

    updateCart();
});
