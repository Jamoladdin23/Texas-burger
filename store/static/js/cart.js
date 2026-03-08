// ===============================
// Показ/скрытие плавающей корзины
// ===============================
function updateFloatingCart(count) {
    const floatingCart = document.getElementById("floating-cart");
    const cartCount = document.getElementById("cart-count");

    if (count > 0) {
        floatingCart.classList.remove("hidden");
        cartCount.textContent = count;
    } else {
        floatingCart.classList.add("hidden");
    }
}


// ===============================
// Основная логика добавления в корзину
// ===============================
document.addEventListener("DOMContentLoaded", function () {

    const addToCartButtons = document.querySelectorAll(".add-to-cart");

    addToCartButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();

            let productId = this.dataset.productId;
            let hasOptions = this.dataset.hasOptions === "true";

            // ===============================
            // Если у товара есть добавки → модальное окно
            // ===============================
            if (hasOptions) {
                fetch(`/product/options/${productId}/`)
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById("extras-content").innerHTML = html;
                        document.getElementById("extras-modal").style.display = "block";

                        document.getElementById("confirm-add").onclick = function (e) {
                            e.preventDefault();

                            const form = document.getElementById("add-to-cart-form");
                            const formData = new FormData(form);

                            fetch(`/cart/add/product/${productId}/`, {
                                method: "POST",
                                headers: {
                                    "X-CSRFToken": getCookie("csrftoken")
                                },
                                body: formData
                            })
                            .then(r => r.json())
                            .then(data => {
                                if (data.success) {
                                    updateFloatingCart(data.quantity);
                                    document.getElementById("extras-modal").style.display = "none";
                                }
                            });
                        };
                    });

            // ===============================
            // Если добавок нет → добавляем сразу
            // ===============================
            } else {
                fetch(`/cart/add/product/${productId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ quantity: 1 })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        updateFloatingCart(data.quantity);
                    }
                });
            }
        });
    });

});


// ===============================
// Показ корзины при загрузке страницы
// ===============================
document.addEventListener("DOMContentLoaded", function () {
    const cartCount = document.getElementById("cart-count");

    if (cartCount && parseInt(cartCount.textContent) > 0) {
        document.getElementById("floating-cart").classList.remove("hidden");
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const closeModal = document.getElementById("close-modal");
    const extrasModal = document.getElementById("extras-modal");

    if (closeModal) {
        closeModal.addEventListener("click", function () {
            extrasModal.style.display = "none";
        });
    }

    // Закрытие по клику вне окна
    window.addEventListener("click", function (e) {
        if (e.target === extrasModal) {
            extrasModal.style.display = "none";
        }
    });
});



//document.addEventListener("DOMContentLoaded", function () {
//    const addToCartButtons = document.querySelectorAll(".add-to-cart");
//
//    addToCartButtons.forEach(button => {
//        button.addEventListener("click", function (event) {
//            event.preventDefault();
//
//            let productId = this.dataset.productId;
//
//            fetch(`/cart/add/product/${productId}/`, {
//                method: "POST",
//                headers: {
//                    "X-CSRFToken": getCookie("csrftoken"),
//                    "Content-Type": "application/json"
//                }
//            })
//
//            .then(response => response.json())
//            .then(data => {
//                if (data.success) {
//                    const cartCount = document.getElementById("cart-count");
////                   added
//                    updateFloatingCart(data.quantity);
//
//                    if (cartCount) {
//                        cartCount.textContent = data.quantity; // Показываем актуальное количество
//                    }
////                    alert("Mahsulot savatga qo'shildi!");
////                    location.reload(); // Перезагружаем страницу
//                } else {
//                    alert("Ошибка: " + data.error);
//              }
//          })
//          .catch(error => console.error("Ошибка в fetch:", error));
//        });
//    });
//});
//
//document.addEventListener("DOMContentLoaded", function () {
//    const cartCount = document.getElementById("cart-count");
//
//    if (cartCount && parseInt(cartCount.textContent) > 0) {
//        document.getElementById("floating-cart").classList.remove("hidden");
//    }
//});
////new
//document.addEventListener("DOMContentLoaded", function () {
//    const cartButton = document.getElementById("cart-button");
//    const cartContainer = document.getElementById("cart-container");
//    const closeCart = document.getElementById("close-cart");
//    const cartItems = document.getElementById("cart-items");
//
//    if (cartButton && cartContainer) {
//        cartButton.addEventListener("click", function () {
//            cartContainer.style.display = "block";
//
//            fetch("/cart/get-items/") // API-запрос на получение товаров
//                .then(response => response.json())
//                .then(data => {
//                    cartItems.innerHTML = data.items.map(item =>
//                        `<p>${item.name} x ${item.quantity} = ${item.price} сом</p>`
//                    ).join("");
//                });
//        });
//
//        closeCart.addEventListener("click", function () {
//            cartContainer.style.display = "none";
//        });
//    }
//});
//
//document.addEventListener("DOMContentLoaded", function () {
//    document.querySelectorAll(".quantity-input").forEach(input => {
//        input.addEventListener("change", function () {
//            console.log("Miqdor yangilanmoqda...");
//
//            let itemId = this.dataset.itemId;
//            let newQuantity = this.value;
//
//            fetch(`/cart/update/item/${itemId}/`, {
//                method: "POST",
//                headers: {
//                    "X-CSRFToken": getCookie("csrftoken"),
//                    "Content-Type": "application/json"
//                },
//                body: JSON.stringify({ quantity: newQuantity })
//            })
//            .then(response => response.json())
//            .then(data => {
//                if (data.success) {
//                    location.reload();
//
//
//                    this.value = data.quantity;
//                    document.getElementById(`item-total-${itemId}`).textContent = `${data.new_price} сом`;
//                    document.getElementById("total-sum").textContent = `Итоговая сумма: ${data.total_cart_price} сом`;
//                    // ✅ Display alert when update is successful
////                    alert("Количество обновлено!");
//                } else {
//                    alert("Ошибка: " + data.error);
//                }
//            })
//            .catch(error => console.error("Ошибка в обновлении корзины:", error));
//        });
//    });
//});
//function updateFloatingCart(count) {
//    const floatingCart = document.getElementById("floating-cart");
//    const cartCount = document.getElementById("cart-count");
//
//    if (count > 0) {
//        floatingCart.classList.remove("hidden");
//        cartCount.textContent = count;
//    } else {
//        floatingCart.classList.add("hidden");
//    }
//}
//
