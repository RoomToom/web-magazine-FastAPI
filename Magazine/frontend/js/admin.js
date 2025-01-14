document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Access denied. Please log in as admin.");
        window.location.href = "login.html";
        return;
    }

    // Load products for management
    fetch("/products", {
        headers: { "Authorization": `Bearer ${token}` }
    })
        .then(response => {
            if (!response.ok) throw new Error("Failed to fetch products");
            return response.json();
        })
        .then(products => {
            const productsDiv = document.getElementById("products");
            products.forEach(product => {
                const productDiv = document.createElement("div");
                productDiv.innerHTML = `
                    <h3>${product.name}</h3>
                    <p>Price: $${product.price}</p>
                    <p>Category: ${product.category}</p>
                    <button onclick="deleteProduct(${product.id})">Delete</button>
                `;
                productsDiv.appendChild(productDiv);
            });
        })
        .catch(error => console.error(error));

    // Add new product
    document.getElementById("addProductForm").addEventListener("submit", (event) => {
        event.preventDefault();

        const name = document.getElementById("name").value;
        const price = document.getElementById("price").value;
        const category = document.getElementById("category").value;
        const imageUrl = document.getElementById("image_url").value;

        fetch("/products", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ name, price, category, image_url: imageUrl })
        })
            .then(response => {
                if (!response.ok) throw new Error("Failed to add product");
                alert("Product added successfully!");
                window.location.reload();
            })
            .catch(error => console.error(error));
    });

    // Load orders for management
    fetch("/orders", {
        headers: { "Authorization": `Bearer ${token}` }
    })
        .then(response => {
            if (!response.ok) throw new Error("Failed to fetch orders");
            return response.json();
        })
        .then(orders => {
            const ordersDiv = document.getElementById("orders");
            orders.forEach(order => {
                const orderDiv = document.createElement("div");
                orderDiv.innerHTML = `
                    <p>Order ID: ${order.id}</p>
                    <p>Status: ${order.status}</p>
                    <button onclick="updateOrderStatus(${order.id}, 'Processing')">Set to Processing</button>
                    <button onclick="updateOrderStatus(${order.id}, 'Completed')">Set to Completed</button>
                `;
                ordersDiv.appendChild(orderDiv);
            });
        })
        .catch(error => console.error(error));
});

function deleteProduct(productId) {
    const token = localStorage.getItem("token");

    fetch(`/products/${productId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    })
        .then(response => {
            if (!response.ok) throw new Error("Failed to delete product");
            alert("Product deleted successfully!");
            window.location.reload();
        })
        .catch(error => console.error(error));
}

function updateOrderStatus(orderId, status) {
    const token = localStorage.getItem("token");

    fetch(`/orders/${orderId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ status })
    })
        .then(response => {
            if (!response.ok) throw new Error("Failed to update order status");
            alert("Order status updated!");
            window.location.reload();
        })
        .catch(error => console.error(error));
}
