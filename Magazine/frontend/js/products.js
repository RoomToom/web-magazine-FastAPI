document.addEventListener("DOMContentLoaded", () => {
    fetch("http://127.0.0.1:8000/products", {
        method: "GET",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to fetch products");
        return response.json();
    })
    .then(products => {
        const productsContainer = document.getElementById("products");
        products.forEach(product => {
            const imageUrl = `http://127.0.0.1:8000/static/images/products/prod${product.id}.webp`;
            const productCard = `
                <div class="wrapper">
                    <div class="container">
                        <div class="top" style="background-image: url('${imageUrl}');"></div>
                        <div class="bottom">
                            <div class="details">
                                <h1>${product.name}</h1>
                                <p>$${product.price}</p>
                            </div>
                            <button class="buy" onclick="addToCart(${product.id})">Add to Cart</button>
                        </div>
                    </div>
                </div>
            `;
            productsContainer.innerHTML += productCard;
        });
    })
    .catch(error => console.error("Error loading products:", error));
});

function addToCart(productId) {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Please log in to add items to your cart.");
        return;
    }

    fetch("http://127.0.0.1:8000/cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 })
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to add to cart");
        alert("Item added to cart!");
    })
    .catch(error => console.error("Error adding to cart:", error));
}
