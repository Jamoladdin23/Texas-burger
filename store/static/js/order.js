document.addEventListener("DOMContentLoaded", function () {
    const orderForm = document.getElementById("order-form");
    const openBtn = document.getElementById("open-order-form");

    if (openBtn && orderForm) {
        openBtn.addEventListener("click", () => {
            orderForm.style.display = "block";
            openBtn.style.display = "none";
        });

        orderForm.addEventListener("submit", function (event) {
            event.preventDefault();

            let formData = new FormData(orderForm);

            fetch("/place_order/", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Accept": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log("SERVER RESPONSE:", data);

                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    alert(data.error);
                }
            })
            .catch(err => {
                console.error("Fetch error:", err);
                alert("Server xatosi. Keyinroq urinib ko‘ring.");
            });
        });
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
