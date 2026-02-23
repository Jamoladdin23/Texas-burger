
function updateCartUI() {
    console.log("Обновление корзины...");
}

document.addEventListener("DOMContentLoaded", function () {
    // ✅ Проверяем, загружена ли updateCartUI() из cart.js
    if (typeof updateCartUI !== "undefined") {
        updateCartUI(); // Обновляем корзину при загрузке страницы
    } else {
        console.warn("⚠️ Функция updateCartUI() не найдена! Проверь, загружается ли cart.js.");
    }

    // ✅ Открытие формы заказа
    let orderButton = document.getElementById("open-order-form");
    let orderForm = document.getElementById("order-form");

    if (orderButton && orderForm) {
        orderForm.style.display = "none"; // Скрываем форму при загрузке
        orderButton.addEventListener("click", function () {
            orderForm.style.display = "block"; // Показываем форму при нажатии
        });
//    } else {
//        console.error("⚠️ Ошибка: #open-order-form или #order-form не найден!");
    }

    // ✅ Добавляем обработчик для оформления заказа
    let submitOrderButton = document.getElementById("order-button");
    if (submitOrderButton) {
        submitOrderButton.addEventListener("click", function (event) {
            event.preventDefault(); // Предотвращаем стандартную отправку формы

            let orderData = new FormData(orderForm);
            let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

            fetch(orderForm.action, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken },
                body: orderData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("✅ Заказ успешно оформлен!");
                    orderForm.reset();
                } else {
                    alert("⚠️ Ошибка оформления заказа. Проверьте данные!");
                }
            })
            .catch(error => console.error("Ошибка заказа:", error));
        })

    }
});