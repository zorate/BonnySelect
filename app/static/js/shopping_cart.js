// ====================================
// SHOPPING CART MANAGER
// ====================================

class ShoppingCart {
    constructor() {
        this.storageKey = 'bonny_shopping_cart';
        this.cart = this.loadCart();
        this.init();
    }

    init() {
        // Update cart icon on page load
        this.updateCartUI();
        
        // Listen for storage changes (multi-tab sync)
        window.addEventListener('storage', () => {
            this.cart = this.loadCart();
            this.updateCartUI();
        });
    }

    loadCart() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            console.log('Cart load error:', e);
            return [];
        }
    }

    saveCart() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.cart));
            this.updateCartUI();
        } catch (e) {
            console.log('Cart save error:', e);
        }
    }

    addItem(product) {
        // Check if item already in cart
        const existing = this.cart.find(item => item._id === product._id);
        
        if (existing) {
            // Item already in cart, just increment quantity
            existing.quantity += 1;
        } else {
            // New item
            this.cart.push({
                _id: product._id,
                title: product.title,
                price: product.price,
                image: product.image,
                quantity: 1
            });
        }
        
        this.saveCart();
        return true;
    }

    removeItem(productId) {
        this.cart = this.cart.filter(item => item._id !== productId);
        this.saveCart();
    }

    updateQuantity(productId, quantity) {
        const item = this.cart.find(item => item._id === productId);
        if (item) {
            item.quantity = Math.max(1, quantity);
            this.saveCart();
        }
    }

    getTotal() {
        return this.cart.reduce((sum, item) => {
            return sum + (parseInt(item.price) * item.quantity);
        }, 0);
    }

    getCount() {
        return this.cart.reduce((count, item) => count + item.quantity, 0);
    }

    isEmpty() {
        return this.cart.length === 0;
    }

    clear() {
        this.cart = [];
        this.saveCart();
    }

    updateCartUI() {
        const count = this.getCount();
        const badge = document.getElementById('cartBadge');
        const count_text = document.getElementById('cartCount');
        
        if (badge) {
            if (count > 0) {
                badge.style.display = 'flex';
                badge.textContent = count > 99 ? '99+' : count;
            } else {
                badge.style.display = 'none';
            }
        }
        
        if (count_text) {
            count_text.textContent = count;
        }
    }

    getItems() {
        return this.cart;
    }
}

// Initialize cart globally
const cart = new ShoppingCart();