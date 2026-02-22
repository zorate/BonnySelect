<!-- ADD THIS TO YOUR index.html BEFORE {% endblock %} -->

<script>
    // ====================================
    // REAL-TIME PRODUCT UPDATE SYSTEM
    // ====================================
    
    class ProductManager {
        constructor() {
            this.products = this.getInitialProducts();
            this.pollInterval = 3000; // Poll every 3 seconds
            this.lastUpdate = Date.now();
            this.isPolling = false;
            this.init();
        }

        init() {
            // Start polling
            this.startPolling();
            
            // Listen for visibility changes
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) {
                    // Page became visible, refresh immediately
                    this.refreshProducts();
                } else {
                    // Page hidden, pause polling
                    this.stopPolling();
                }
            });

            // Refresh on page focus
            window.addEventListener('focus', () => {
                this.refreshProducts();
            });
        }

        getInitialProducts() {
            const productCards = document.querySelectorAll('[data-product-id]');
            const products = {};
            
            productCards.forEach(card => {
                const id = card.dataset.productId;
                const status = card.querySelector('[data-status]').dataset.status;
                products[id] = { status };
            });
            
            return products;
        }

        startPolling() {
            if (this.isPolling) return;
            this.isPolling = true;
            
            this.pollTimer = setInterval(() => {
                this.refreshProducts();
            }, this.pollInterval);
        }

        stopPolling() {
            if (this.pollTimer) {
                clearInterval(this.pollTimer);
                this.isPolling = false;
            }
        }

        refreshProducts() {
            // Fetch latest products from API
            fetch('/admin/api/products')
                .then(response => {
                    if (!response.ok) throw new Error('Failed to fetch products');
                    return response.json();
                })
                .then(freshProducts => {
                    this.updateProductsUI(freshProducts);
                })
                .catch(err => {
                    console.log('Product refresh failed (will retry):', err);
                });
        }

        updateProductsUI(freshProducts) {
            freshProducts.forEach(freshProduct => {
                const id = freshProduct._id;
                const card = document.querySelector(`[data-product-id="${id}"]`);
                
                if (!card) {
                    // New product added! Add it to the grid
                    this.addNewProductCard(freshProduct);
                    return;
                }

                // Update existing product
                const badge = card.querySelector('[data-status]');
                const oldStatus = badge.dataset.status;
                const newStatus = freshProduct.status;

                if (oldStatus !== newStatus) {
                    // Status changed
                    this.updateProductStatus(card, newStatus);
                }
            });

            // Check for deleted products
            this.checkForDeletedProducts(freshProducts);
        }

        addNewProductCard(product) {
            const grid = document.getElementById('productsGrid');
            if (!grid) return;

            // Create new product card
            const card = document.createElement('a');
            card.href = `/product/${product._id}`;
            card.className = 'product-card';
            card.dataset.productId = product._id;
            card.style.position = 'relative';
            
            card.innerHTML = `
                <img src="${product.image}" alt="${product.title}" class="product-image" loading="lazy">
                <div class="product-badge available" data-status="${product.status}">
                    ${product.status.toUpperCase()}
                </div>
                <div class="product-info">
                    <h3 class="product-title">${product.title}</h3>
                    <p class="product-price">₦${product.price}</p>
                    <button type="button" class="product-btn" onclick="event.preventDefault(); navigateToProduct(event)">
                        View
                    </button>
                </div>
            `;

            // Animate entrance
            card.style.opacity = '0';
            card.style.transform = 'scale(0.95)';
            grid.appendChild(card);

            // Trigger animation
            setTimeout(() => {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            }, 10);

            // Show notification
            this.showNotification('✨ New product added!');
            
            // Track in our products
            this.products[product._id] = { status: product.status };
        }

        updateProductStatus(card, newStatus) {
            const badge = card.querySelector('[data-status]');
            const btn = card.querySelector('.product-btn');
            
            // Update badge
            badge.dataset.status = newStatus;
            badge.textContent = newStatus.toUpperCase();
            badge.classList.toggle('available', newStatus === 'available');

            // Update button
            if (newStatus === 'available') {
                btn.disabled = false;
                btn.style.opacity = '1';
                btn.style.cursor = 'pointer';
                btn.textContent = 'View';
                btn.onclick = navigateToProduct;
            } else {
                btn.disabled = true;
                btn.style.opacity = '0.5';
                btn.style.cursor = 'not-allowed';
                btn.textContent = 'Sold Out';
                btn.onclick = null;
            }

            // Animate change
            badge.style.animation = 'none';
            setTimeout(() => {
                badge.style.animation = 'pulse 0.6s ease';
            }, 10);

            // Update tracking
            this.products[card.dataset.productId] = { status: newStatus };
            
            this.showNotification(`Product ${newStatus === 'available' ? 'available' : 'sold out'}!`);
        }

        checkForDeletedProducts(freshProducts) {
            const freshIds = new Set(freshProducts.map(p => p._id));
            const cards = document.querySelectorAll('[data-product-id]');

            cards.forEach(card => {
                const id = card.dataset.productId;
                if (!freshIds.has(id)) {
                    // Product was deleted
                    this.removeProductCard(card);
                }
            });
        }

        removeProductCard(card) {
            // Animate removal
            card.style.transition = 'all 0.3s ease';
            card.style.opacity = '0';
            card.style.transform = 'scale(0.95)';

            setTimeout(() => {
                card.remove();
                this.showNotification('Product removed');
            }, 300);

            // Remove from tracking
            delete this.products[card.dataset.productId];
        }

        showNotification(message) {
            // Create notification element
            const notif = document.createElement('div');
            notif.style.cssText = `
                position: fixed;
                bottom: 80px;
                left: 50%;
                transform: translateX(-50%);
                background: #0a0a0a;
                color: #ffffff;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                z-index: 8000;
                animation: slideUp 0.3s ease;
                max-width: 80%;
                text-align: center;
            `;
            notif.textContent = message;
            
            document.body.appendChild(notif);

            // Auto-remove after 3 seconds
            setTimeout(() => {
                notif.style.animation = 'slideDown 0.3s ease';
                setTimeout(() => notif.remove(), 300);
            }, 3000);
        }
    }

    // Initialize product manager when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        if (document.getElementById('productsGrid')) {
            window.productManager = new ProductManager();
        }
    });

    // Add pulse animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
    `;
    document.head.appendChild(style);
</script>