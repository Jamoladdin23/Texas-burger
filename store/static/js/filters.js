document.addEventListener("DOMContentLoaded", function() {
    const filterCategory = document.querySelector('#filter-category');
    if (filterCategory) {
        filterCategory.addEventListener('change', function() {
            const filterValue = this.value;

            fetch(`/category/filter/?filter=${filterValue}`)
                .then(response => response.json())
                .then(data => {
                    const container = document.querySelector('#category-container');
                    if (container) {
                        container.innerHTML = '';
                        data.products.forEach(product => {
                            container.innerHTML += `
                                <div class="product-item" data-aos="fade-up">
                                    <img src="${product.photo_url}" alt="${product.name}">
                                    <h3>${product.name}</h3>
                                    <p>${product.description}</p>
                                    <p>Цена: ${product.price}</p>
                                </div>`;
                        });
                        AOS.refresh();
                    }
                });
        });
    }
});
