// Run subtotal when page loads
document.addEventListener("DOMContentLoaded", () => {
    subtotalincardpage();
    total_calculate_for_card();
    phone_total_calculate_for_card()
    
});

document.getElementById('offcanvasCart').addEventListener('shown.bs.offcanvas', function () {
    loadCart()
});

function launchConfetti() {
    const duration = 3000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 2000 };

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    const interval = setInterval(function () {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        const particleCount = 50 * (timeLeft / duration);
        confetti(Object.assign({}, defaults, {
            particleCount,
            origin: { x: randomInRange(0.1, 0.9), y: Math.random() - 0.2 }
        }));
    }, 250);
}
// ================================
// SUBTOTAL CALCULATION
// ================================
function subtotalincardpage() {

    let total_bill0 = document.getElementById("total_bill00");
    let total_billcheck = document.getElementById("total_billcheck");
    let sub_total = document.getElementById("sub_total_bill");
    let input_amount_rzo = document.getElementById("totalAmount");

    let cart_items_container = document.getElementById("shoping_card_dynemic00");

    if (!cart_items_container) return;

    let total = 0;

    cart_items_container.querySelectorAll("span[id^='total_amount']").forEach(price_span => {

        let text = price_span.textContent.trim();

        // remove ₹ , spaces
        text = text.replace(/[₹, ]/g, "");

        let price = parseFloat(text);

        if (!isNaN(price)) {
            total += price;
        }

    });

    let roundedTotal = Math.round(total);
    if (sub_total) sub_total.textContent = "₹ " + roundedTotal;
    if (total_bill0) total_bill0.textContent = "₹ " + roundedTotal;
    if (total_billcheck) total_billcheck.textContent = "₹ " + roundedTotal;
    if (input_amount_rzo) input_amount_rzo.value = roundedTotal;
}



function openCartDrawer() {
    let offcanvasElement = document.getElementById("offcanvasCart");
    if (offcanvasElement) {
        try {
            let bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasElement);
            if (!bsOffcanvas) {
                bsOffcanvas = new bootstrap.Offcanvas(offcanvasElement, { scroll: true });
            }
            bsOffcanvas.show();
        } catch (e) {
            console.error("Offcanvas show error:", e);
        }
    }
}

// ================================
// LOAD CART (HTMX style refresh)
// ================================
function loadCart(shouldOpen = true) {
    fetch("/get-cart-data")
        .then(res => res.text())
        .then(html => {
            let container = document.getElementById("shoping_card_dynemic00");
            if (container) {
                container.innerHTML = html;
            }

            subtotalincardpage();

            if (shouldOpen) {
                setTimeout(() => {
                    openCartDrawer();
                }, 50);
            }
        })
        .catch(err => console.error("Cart Load Error:", err));
}

// ADD PRODUCT TO CART
// ================================
function Add_to_cart(p_id, btn) {
    let csrfInput = document.querySelector("[name='csrfmiddlewaretoken']");
    let csrf_token = csrfInput ? csrfInput.value : "";

    let originalHtml = btn ? btn.innerHTML : "";
    if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
        btn.disabled = true;
    }

    fetch("/add-to-cart", {
        method: "POST",
        body: JSON.stringify({ product_id: p_id }),
        headers: {
            "X-CSRFToken": csrf_token,
            "Content-Type": "application/json"
        }
    })
    .then(res => res.json())
    .then(data => {
        if (btn) {
            btn.innerHTML = '<i class="fa-solid fa-check"></i>';
            btn.classList.add("added");
        }
        
        if (window.showToast) {
            window.showToast(data.message || "Added to Cart!");
        }
        
        loadCart(true);
        
        if (btn) {
            setTimeout(() => {
                btn.innerHTML = originalHtml;
                btn.disabled = false;
            }, 2000);
        }
    })
    .catch(err => {
        console.error(err);
        if (btn) {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
        }
    });
}

// ================================
// ADD INNER PRODUCT
// ================================
function inner_p_Add_to_cart(Inner_product_id, btn) {
    let csrfInput = document.querySelector("[name='csrfmiddlewaretoken']");
    let csrf_token = csrfInput ? csrfInput.value : "";

    let originalHtml = btn ? btn.innerHTML : "";
    if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
        btn.disabled = true;
    }

    fetch("/add-to-cart_inner", {
        method: "POST",
        body: JSON.stringify({
            Inner_product_id: Inner_product_id
        }),
        headers: {
            "X-CSRFToken": csrf_token,
            "Content-Type": "application/json"
        }
    })
    .then(res => res.json())
    .then(data => {
        if (btn) {
            btn.innerHTML = '<i class="fa-solid fa-check"></i>';
        }
        
        if (window.showToast) {
            window.showToast(data.message || "Added to Cart!");
        }
        
        loadCart(true);

        if (btn) {
            setTimeout(() => {
                btn.innerHTML = originalHtml;
                btn.disabled = false;
            }, 2000);
        }
    })
    .catch(err => {
        console.error(err);
        if (btn) {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
        }
    });
}

// ================================
// REMOVE INNER PRODUCT
// ================================
function inner_p_remove_item_in_card(button, p_id) {
    let csrf_token = getCsrfToken();

    fetch("/add-to-cart_inner", {
        method: "POST",
        body: JSON.stringify({
            remove_product_id_inner: p_id
        }),
        headers: {
            "X-CSRFToken": csrf_token,
            "Content-Type": "application/json"
        }
    })
    .then(res => res.json())
    .then(data => {
        let card = document.getElementById("inner_card_item" + p_id);
        if (card) {
            card.remove();
        }
        resetAddButton(p_id);
        loadCart(false);
        if (window.showToast) {
            window.showToast("Item removed from cart");
        }
        if (window.updateCartBadges) {
            window.updateCartBadges();
        }
    })
    .catch(err => {
        console.error("Remove Inner Error:", err);
        loadCart(false);
    });
}

function resetAddButton(product_id){
    let btn = document.querySelector(`[data-product="${product_id}"]`);
    if(btn){
        btn.innerHTML = 'ADD TO CART';
        btn.classList.remove("added", "btn-success");
        btn.disabled = false;
    }
}

// ================================
// REMOVE NORMAL PRODUCT
// ================================
function remove_item_in_card(button, p_id) {
    let csrf_token = getCsrfToken();

    fetch("/add-to-cart", {
        method: "POST",
        body: JSON.stringify({
            remove_product_id: p_id
        }),
        headers: {
            "X-CSRFToken": csrf_token,
            "Content-Type": "application/json"
        }
    })
    .then(res => res.json())
    .then(data => {
        let card = document.getElementById("card_item" + p_id);
        if (card) {
            card.remove();
        }
        resetAddButton(p_id);
        loadCart(false);
        if (window.showToast) {
            window.showToast("Item removed from cart");
        }
        if (window.updateCartBadges) {
            window.updateCartBadges();
        }
    })
    .catch(err => {
        console.error("Remove Error:", err);
        loadCart(false);
    });
}

function ste_size_in_cart(p_id) {

    let size = document.getElementById(`p_size${p_id}`).value

    const csrftoken = document.querySelector('[name="csrfmiddlewaretoken"]').value

    fetch("/add-to-cart", {

        method: "POST",

        body: JSON.stringify({
            size_card_id: p_id,
            size_product: size
        }),

        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json"
        }

    })
}
function ste_size_in_cart_inner(p_id) {

    let size = document.getElementById(`p_size${p_id}`).value;

    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;

    fetch("/add-to-cart_inner", {
        method: "POST",
        body: JSON.stringify({
            size_card_id: p_id,
            size_product: size
        }),
        headers: {
            "X-CSRFToken": csrf_token,
            "Content-Type": "application/json"
        }
    })
    .then(res => res.json())
    .then(data => {
        console.log("Size updated");
    })
}


function checkout_checking_size(){

    let selects = document.querySelectorAll("select[dir='slect_size_issu']");

    for(let s of selects){

        if(!s.value){

            swal("Required", "Please select size for all items", "error");
            return;

        }

    }

    window.location.href="/checkout";
}

// check out f  



function phone_increase_quantity_for_cart(p_id, price_p, offer_qty, offer_amount) {
    let inputElement = document.getElementById(`pcard_quantity_inputval${p_id}`);
    let sending_amount_rezorpay = document.getElementById("pproduct_total_bill");

    let total_bil = document.getElementById(`pcard_total_amount${p_id}`);
    let offer_div = document.getElementById(`poffer_Session${p_id}`);
    let currentValue = parseInt(inputElement.value);
    const csrftoken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

    let newValue = currentValue + 1;
    inputElement.value = newValue;

    let normal_total = newValue * parseInt(price_p);
    let per_item = offer_amount / offer_qty;  // Ex: 1199 / 4 = 299.75
    let offer_total = (newValue * per_item).toFixed(2); // rounded

    if (newValue >= offer_qty) {
        // ✅ OFFER ACTIVE
        total_bil.textContent = "₹ " + offer_total;
        sending_amount_rezorpay.value=offer_total

        offer_div.innerHTML = `
            <span class="fw-semibold text-success">✅ Offer Activated!</span>
            <span class="text-dark">You are paying </span>
            <span class="text-success fw-bold">₹ ${per_item.toFixed(2)}</span> per item 🎉
        `;

        // Trigger confetti only when offer is first activated
        if (currentValue < offer_qty) launchConfetti();
    } else {
        // ❌ OFFER NOT ACTIVE
        total_bil.textContent = "₹ " + normal_total;
        sending_amount_rezorpay.value=normal_total


        offer_div.innerHTML = `
            <span class="fw-semibold text-dark">🎉 Special Offer!</span>
            <span class="text-muted">Buy <b>${offer_qty}</b> & pay only </span>
            <span class="text-success fw-bold">₹${offer_amount}</span>
        `;
    }

    // Update DB
    fetch("/add-to-cart", {
        method: "POST",
        body: JSON.stringify({ "card_id": p_id, "quantity": newValue }),
        headers: { "X-CSRFToken": csrftoken }
    });

    phone_total_calculate_for_card();
}

function phone_decrease_quantity_for_card(p_id, price_p, offer_qty, offer_amount) {
    let sending_amount_rezorpay = document.getElementById("pproduct_total_bill");

    let inputElement = document.getElementById(`pcard_quantity_inputval${p_id}`);
    let total_bil = document.getElementById(`pcard_total_amount${p_id}`);
    let offer_div = document.getElementById(`poffer_Session${p_id}`);
    let currentValue = parseInt(inputElement.value);
    const csrftoken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

    if (currentValue < 2) {
        swal("Limit", "Minimum quantity is 1", "error");
        return;
    }

    let newValue = currentValue - 1;
    inputElement.value = newValue;

    let normal_total = newValue * parseInt(price_p);
    let per_item = offer_amount / offer_qty;
    let offer_total = (newValue * per_item).toFixed(2);

    if (newValue >= offer_qty) {
        total_bil.textContent = "₹ " + offer_total;
        sending_amount_rezorpay.value=offer_total
        offer_div.innerHTML = `
            <span class="fw-semibold text-success">✅ Offer Activated!</span>
            <span class="text-dark">You are paying </span>
            <span class="text-success fw-bold">₹ ${per_item.toFixed(2)}</span> per item 🎉
        `;
    } else {
        total_bil.textContent = "₹ " + normal_total;
        sending_amount_rezorpay.value=normal_total

        offer_div.innerHTML = `
            <span class="fw-semibold text-dark">🎉 Special Offer!</span>
            <span class="text-muted">Buy <b>${offer_qty}</b> & pay only </span>
            <span class="text-success fw-bold">₹${offer_amount}</span>
        `;
    }

    fetch("/add-to-cart", {
        method: "POST",
        body: JSON.stringify({ "card_id": p_id, "quantity": newValue }),
        headers: { "X-CSRFToken": csrftoken }
    });

    phone_total_calculate_for_card();
}


function phone_total_calculate_for_card() {
    let total_amounta = document.getElementById("ptotal_amount_for_pay");

    let sending_amount_rezorpay =
        document.getElementById("pproduct_total_bill") ||
        document.getElementById("product_total_bill");

    let total_bill_btn = document.getElementById("total_bill_of_phone_i_place_button");
    let total_bill_upi = document.getElementById("total_bill_of_phone_i_place_button_upi_screen");

    let total = 0;

    const priceElements = document.querySelectorAll('[dir="pper_product_price"]');

    if (priceElements.length > 0) {
        // 🛒 Cart case
        priceElements.forEach(el => {
            let text = el.innerText || el.textContent;
            let digits = text.replace(/[^0-9.]/g, "");
            if (digits) total += parseFloat(digits);
        });
    } else {
        // 📦 Single product case
        if (sending_amount_rezorpay && sending_amount_rezorpay.value) {
            total = parseFloat(sending_amount_rezorpay.value);
        }
    }

    if (total_amounta) {
        total_amounta.textContent = "₹ " + total.toFixed(2);
    }

    if (sending_amount_rezorpay) {
        sending_amount_rezorpay.value = total.toFixed(2);
    }

    if (total_bill_btn) {
        total_bill_btn.textContent = "₹ " + total.toFixed(2);
    }

    if (total_bill_upi) {
        total_bill_upi.textContent = "₹ " + total.toFixed(2);
    }
}




function increase_quantity_for_cart(p_id, price_p, offer_qty, offer_amount) {
    let inputElement = document.getElementById(`card_quantity_inputval${p_id}`);
    let total_bil = document.getElementById(`card_total_amount${p_id}`);
    let offer_div = document.getElementById(`offer_Session${p_id}`);
    let currentValue = parseInt(inputElement.value);
    const csrftoken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

    let newValue = currentValue + 1;
    inputElement.value = newValue;

    let normal_total = newValue * parseInt(price_p);
    let per_item = offer_amount / offer_qty;  // Ex: 1199 / 4 = 299.75
    let offer_total = (newValue * per_item).toFixed(2); // rounded

    if (newValue >= offer_qty) {
        // ✅ OFFER ACTIVE
        total_bil.textContent = "₹ " + offer_total;

        offer_div.innerHTML = `
            <span class="fw-semibold text-success">✅ Offer Activated!</span>
            <span class="text-dark">You are paying </span>
            <span class="text-success fw-bold">₹ ${per_item.toFixed(2)}</span> per item 🎉
        `;

        // Trigger confetti only when offer is first activated
        if (currentValue < offer_qty) launchConfetti();
    } else {
        // ❌ OFFER NOT ACTIVE
        total_bil.textContent = "₹ " + normal_total;

        offer_div.innerHTML = `
            <span class="fw-semibold text-dark">🎉 Special Offer!</span>
            <span class="text-muted">Buy <b>${offer_qty}</b> & pay only </span>
            <span class="text-success fw-bold">₹${offer_amount}</span>
        `;
    }

    // Update DB
    fetch("/add-to-cart", {
        method: "POST",
        body: JSON.stringify({ "card_id": p_id, "quantity": newValue }),
        headers: { "X-CSRFToken": csrftoken }
    });

    total_calculate_for_card();
}

function decrease_quantity_for_card(p_id, price_p, offer_qty, offer_amount) {
    let inputElement = document.getElementById(`card_quantity_inputval${p_id}`);
    let total_bil = document.getElementById(`card_total_amount${p_id}`);
    let offer_div = document.getElementById(`offer_Session${p_id}`);
    let currentValue = parseInt(inputElement.value);
    const csrftoken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

    if (currentValue < 2) {
        swal("Limit", "Minimum quantity is 1", "error");
        return;
    }

    let newValue = currentValue - 1;
    inputElement.value = newValue;

    let normal_total = newValue * parseInt(price_p);
    let per_item = offer_amount / offer_qty;
    let offer_total = (newValue * per_item).toFixed(2);

    if (newValue >= offer_qty) {
        total_bil.textContent = "₹ " + offer_total;
        offer_div.innerHTML = `
            <span class="fw-semibold text-success">✅ Offer Activated!</span>
            <span class="text-dark">You are paying </span>
            <span class="text-success fw-bold">₹ ${per_item.toFixed(2)}</span> per item 🎉
        `;
    } else {
        total_bil.textContent = "₹ " + normal_total;
        offer_div.innerHTML = `
            <span class="fw-semibold text-dark">🎉 Special Offer!</span>
            <span class="text-muted">Buy <b>${offer_qty}</b> & pay only </span>
            <span class="text-success fw-bold">₹${offer_amount}</span>
        `;
    }

    fetch("/add-to-cart", {
        method: "POST",
        body: JSON.stringify({ "card_id": p_id, "quantity": newValue }),
        headers: { "X-CSRFToken": csrftoken }
    });

    total_calculate_for_card();
}




function total_calculate_for_card() {
    let total_amounta = document.getElementById("total_amount_for_paycart");
    let total_amount_for_pay_forcart = document.getElementById("total_amount_for_pay_forcart");

    let sending_amount_rezorpay =
        document.getElementById("product_total_bill") ||
        document.getElementById("pproduct_total_bill");

    const priceElements = document.querySelectorAll('[dir="pper_product_price"]');

    let total = 0;

    if (priceElements.length > 0) {
        priceElements.forEach(el => {
            let text = el.innerText || el.textContent;
            let digits = text.replace(/[^0-9.]/g, "");
            if (digits) total += parseFloat(digits);
        });
    } else {
        // fallback (single product)
        if (sending_amount_rezorpay && sending_amount_rezorpay.value) {
            total = parseFloat(sending_amount_rezorpay.value);
        }
    }

    if (total_amounta) {
        total_amounta.value = total.toFixed(2);
    }

    if (total_amount_for_pay_forcart) {
        total_amount_for_pay_forcart.textContent = "₹ " + total.toFixed(2);
    }

    if (sending_amount_rezorpay) {
        sending_amount_rezorpay.value = total.toFixed(2);
    }
}








function increase_quantity(p_id, price_p,offer_qty, offer_amount) {
    let inputElement = document.getElementById(`quantity_inputval${p_id}`);
    let total_bil = document.getElementById(`total_amount${p_id}`)
    let offer_div = document.getElementById(`offer_Session${p_id}`);
    let currentValue = parseInt(inputElement.value); // Get the current value and parse it to an integer
   
    
    let newValue = currentValue + 1;
    inputElement.value = newValue;

    let normal_total = newValue * parseInt(price_p);
    let per_item = offer_amount / offer_qty;  // Ex: 1199 / 4 = 299.75
    let offer_total = (newValue * per_item).toFixed(2); // rounded

    if (newValue >= offer_qty) {
        // ✅ OFFER ACTIVE
        total_bil.textContent = "₹ " + offer_total;

        offer_div.innerHTML = `
            <span class="fw-semibold text-success">✅ Offer Activated!</span>
            <span class="text-dark">You are paying </span>
            <span class="text-success fw-bold">₹ ${per_item.toFixed(2)}</span> per item 🎉
        `;
        total_calculate(offer_total)


        // Trigger confetti only when offer is first activated
        if (currentValue < offer_qty) launchConfetti();
    } else {
        // ❌ OFFER NOT ACTIVE
        total_bil.textContent = "₹ " + normal_total;

        offer_div.innerHTML = `
            <span class="fw-semibold text-dark">🎉 Special Offer!</span>
            <span class="text-muted">Buy <b>${offer_qty}</b> & pay only </span>
            <span class="text-success fw-bold">₹${offer_amount}</span>
        `;
        total_calculate(normal_total)

    }

}


function total_calculate(amount) {
    let total_amounta = document.getElementById("total_amount_for_pay");
    let sub_total_bill = document.getElementById("sub_total_bill");

    let sending_amount_rezorpay = document.getElementById("product_total_bill");

    if (total_amounta) {
        total_amounta.textContent = "₹ " + amount;
    }

    if (sending_amount_rezorpay) {
        sending_amount_rezorpay.value = amount;
    }
}

function phone_decrease_quantity(p_id, price_p,offer_qty, offer_amount) {
    let sending_amount_rezorpay = document.getElementById("pproduct_total_bill");

    let inputElement = document.getElementById(`pquantity_inputval${p_id}`);
    let total_bil = document.getElementById(`ptotal_amount${p_id}`)
    let currentValue = parseInt(inputElement.value); // Get the current value and parse it to an integer
    let offer_div = document.getElementById(`poffer_Session${p_id}`);

    if (currentValue < 2) {
        swal("Limit", "minimum limit is 1", "error");
        return;

    } 
    
    let newValue = currentValue - 1;
    inputElement.value = newValue;

    let normal_total = newValue * parseInt(price_p);
    let per_item = offer_amount / offer_qty;
    let offer_total = (newValue * per_item).toFixed(2);

    if (newValue >= offer_qty) {
        total_bil.textContent = "₹ " + offer_total;
        sending_amount_rezorpay.value=offer_total
        offer_div.innerHTML = `
            <span class="fw-semibold text-success">✅ Offer Activated!</span>
            <span class="text-dark">You are paying </span>
            <span class="text-success fw-bold">₹ ${per_item.toFixed(2)}</span> per item 🎉
        `;
        phone_total_calculate(offer_total)

    } else {
        total_bil.textContent = "₹ " + normal_total;
        sending_amount_rezorpay.value=normal_total

        offer_div.innerHTML = `
            <span class="fw-semibold text-dark">🎉 Special Offer!</span>
            <span class="text-muted">Buy <b>${offer_qty}</b> & pay only </span>
            <span class="text-success fw-bold">₹${offer_amount}</span>
        `;
        phone_total_calculate(normal_total)

    }

}
function phone_increase_quantity(p_id, price_p,offer_qty, offer_amount) {
    let inputElement = document.getElementById(`pquantity_inputval${p_id}`);
    let sending_amount_rezorpay = document.getElementById("pproduct_total_bill");

    let total_bil = document.getElementById(`ptotal_amount${p_id}`)
    let offer_div = document.getElementById(`poffer_Session${p_id}`);
    let currentValue = parseInt(inputElement.value); // Get the current value and parse it to an integer
   
    
    let newValue = currentValue + 1;
    inputElement.value = newValue;

    let normal_total = newValue * parseInt(price_p);
    let per_item = offer_amount / offer_qty;  // Ex: 1199 / 4 = 299.75
    let offer_total = (newValue * per_item).toFixed(2); // rounded

    if (newValue >= offer_qty) {
        // ✅ OFFER ACTIVE
        total_bil.textContent = "₹ " + offer_total;
        sending_amount_rezorpay.value=offer_total;

        offer_div.innerHTML = `
            <span class="fw-semibold text-success">✅ Offer Activated!</span>
            <span class="text-dark">You are paying </span>
            <span class="text-success fw-bold">₹ ${per_item.toFixed(2)}</span> per item 🎉
        `;
        phone_total_calculate(offer_total)


        // Trigger confetti only when offer is first activated
        if (currentValue < offer_qty) launchConfetti();
    } else {
        // ❌ OFFER NOT ACTIVE
        total_bil.textContent = "₹ " + normal_total;
        sending_amount_rezorpay.value=normal_total;


        offer_div.innerHTML = `
            <span class="fw-semibold text-dark">🎉 Special Offer!</span>
            <span class="text-muted">Buy <b>${offer_qty}</b> & pay only </span>
            <span class="text-success fw-bold">₹${offer_amount}</span>
        `;
        phone_total_calculate(normal_total)

    }

}


function phone_total_calculate(amount){
    let total_amounta=document.getElementById("ptotal_amount_for_pays")
    let ptotal_amount_for_pay=document.getElementById("total_bill_of_phone_i_place_buttons")
    let total_bill_of_phone_i_place_button_upi_screen=document.getElementById("total_bill_of_phone_i_place_button_upi_screens")
    let sending_price_in_django_view_js=document.getElementById("sending_price_in_django_view")

    // let sending_amount_rezorpay=document.getElementById("product_total_bill").value= amount
    
    total_amounta.textContent = "₹ "+amount
    ptotal_amount_for_pay.textContent= "₹ "+amount
    total_bill_of_phone_i_place_button_upi_screen.textContent= "₹ "+amount
    sending_price_in_django_view_js.value=amount
}




function decrease_quantity(p_id, price_p,offer_qty, offer_amount) {
    let inputElement = document.getElementById(`quantity_inputval${p_id}`);
    let total_bil = document.getElementById(`total_amount${p_id}`)
    let currentValue = parseInt(inputElement.value); // Get the current value and parse it to an integer
    let offer_div = document.getElementById(`offer_Session${p_id}`);

    if (currentValue < 2) {
        swal("Limit", "minimum limit is 1", "error");
        return;

    } 
    
    let newValue = currentValue - 1;
    inputElement.value = newValue;

    let normal_total = newValue * parseInt(price_p);
    let per_item = offer_amount / offer_qty;
    let offer_total = (newValue * per_item).toFixed(2);

    if (newValue >= offer_qty) {
        total_bil.textContent = "₹ " + offer_total;
        offer_div.innerHTML = `
            <span class="fw-semibold text-success">✅ Offer Activated!</span>
            <span class="text-dark">You are paying </span>
            <span class="text-success fw-bold">₹ ${per_item.toFixed(2)}</span> per item 🎉
        `;
        total_calculate(offer_total)

    } else {
        total_bil.textContent = "₹ " + normal_total;
        offer_div.innerHTML = `
            <span class="fw-semibold text-dark">🎉 Special Offer!</span>
            <span class="text-muted">Buy <b>${offer_qty}</b> & pay only </span>
            <span class="text-success fw-bold">₹${offer_amount}</span>
        `;
        total_calculate(normal_total)

    }

}




function delete_product(p_id) {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    swal({
        title: "Are you sure?",
        text: "Once deleted, you will not be able to recover this Book !",
        icon: "warning",
        buttons: true,
        dangerMode: true,
    })
        .then((willDelete) => {
            if (willDelete) {
                fetch("/view-book", {
                    method: "POST",
                    body: JSON.stringify({ "delete_product_id": p_id }),
                    headers: {
                        "X-CSRFToken": csrf_token,
                        "Content-Type": "application/json"  // Important!
                    }
                })
                    .then(res => res.json())  // Expecting JSON response
                    .then(data => {
                        swal({
                            text: data.message,
                            icon: "success",
                        })
                            .then(() => { window.location.reload() })
                    })
            } else {
                swal("Your imaginary file is safe!");
            }
        });


}


function Colorset_image(cid) {
    const path = window.location.pathname;
    window.location.href = `${path}?color-id-filter=${cid}`

}
function encryptData(data) {
    const text = JSON.stringify(data);
    return btoa(text);  // base64 encode
}

function save_size(pro_id, check_model_inner_ya_product) {
    const qut = 1
    const sizes = document.querySelectorAll('[dir="product_size"]');

    let set_size = null;
    // Get selected size
    sizes.forEach(sz => {
        if (sz.checked) {
            set_size = sz.value;
        }
    });

    // Validation
    if (set_size == null) {
        swal({
            title: "Required",
            text: "Please select a size",
            icon: "warning",

        })

        return false;
    }
     // Build encrypted data
    const data = {
        product_id_p: pro_id,
        p_size: set_size,
        quent: qut
    };
    

    const encrypted = encryptData(data);
    window.location.href = `/checkout?data=${encodeURIComponent(encrypted)}`;


}
function save_size_for_inner(pro_id) {
    const qut = document.getElementById("qunt_product").value;
    const sizes = document.querySelectorAll('[dir="product_size"]');

    let set_size = null;
    // Get selected size
    sizes.forEach(sz => {
        if (sz.checked) {
            set_size = sz.value;
        }
    });

    // Validation
    if (set_size == null) {
        swal({
            title: "Required",
            text: "Please select a size",
            icon: "warning",

        })
        return false;
    }
     // Build encrypted data
    const data = {
        inner_product: pro_id,
        p_size: set_size,
        quent: qut
    };

    const encrypted = encryptData(data);
    window.location.href = `/checkout?data=${encodeURIComponent(encrypted)}`;

}

function products_page_plus() {
    let inputElement = document.getElementById(`qunt_product`);
    let currentValue = parseInt(inputElement.value); // Get the current value and parse it to an integer

    if (currentValue > 20) {
        alert("maximum limit is 21")
    } else {
        let newValue = currentValue + 1; // Increment the current value by 1
        inputElement.value = newValue


    }
    return currentValue


}

function products_page_minus() {
    let inputElement = document.getElementById(`qunt_product`);
    let currentValue = parseInt(inputElement.value); // Get the current value and parse it to an integer

    if (currentValue < 2) {
        swal("Limit", "minimum limit is 1", "error");

    } else {
        let newValue = currentValue - 1; // Increment the current value by 1
        inputElement.value = newValue


    }
    return currentValue


}

function Search_filter() {
        const searchInput = $("#shop_search").val().toLowerCase();
        
        $('.product_tt').each(function() {
            const productText = $(this).text().toLowerCase();
            const productItem = $(this).closest('.product-item');
            
            if (productText.includes(searchInput)) {
                productItem.show();
            } else {
                productItem.hide();
            }
        });
    }


function hideModal() {
    let modal = bootstrap.Modal.getInstance(document.getElementById("dekstop_addres"))
    modal.hide()
}
function phonehideModal() {
  const offcanvasEl = document.getElementById('offcanvasRightaddresphone');
  const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
  bsOffcanvas.hide();
}

function showToast() {
    const toastEl = document.getElementById("addressToast");
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}



// Product page CSS + JS load for HTMX navigation

document.body.addEventListener("htmx:afterSwap", function (event) {

    // check if product page exists
    if (document.querySelector(".this_is_product_page")) {

        // CSS load
        if (!document.getElementById("product-details-css")) {

            let link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = "/static/css/product-details.css";
            link.id = "product-details-css";

            document.head.appendChild(link);
        }

        // JS load
        if (!document.getElementById("product-details-js")) {

            let script = document.createElement("script");
            script.src = "/static/js/product-details.js";
            script.id = "product-details-js";

            document.body.appendChild(script);
        }

    }

});

// retun request _model 

function cancel_model_in_profile(pid){
    let np=document.getElementById("cancel_order_id").value=pid
     // modal open करना
    let modal = new bootstrap.Modal(document.getElementById('cancelOrderModal'));
    modal.show();
    
}
function retun_modelusing_js(pid){
    let np=document.getElementById("retun_model").value=pid
     // modal open करना
    let modal = new bootstrap.Modal(document.getElementById('returnModal'));
    modal.show();
    
}

// Global Wishlist Functions
function Add_to_wish(productId) {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']") ? document.querySelector("[name='csrfmiddlewaretoken']").value : "";
    fetch("/wish-list", {
        method: "POST",
        body: JSON.stringify({ product_id: productId }),
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token
        }
    })
    .then(res => res.json())
    .then(data => {
        swal({
            text: data.message,
            icon: "success"
        });
    })
    .catch(err => console.error("Wishlist error:", err));
}

function Inner_p_Add_to_wish(productId) {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']") ? document.querySelector("[name='csrfmiddlewaretoken']").value : "";
    fetch("/wish-list", {
        method: "POST",
        body: JSON.stringify({ inner_product_id: productId }),
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token
        }
    })
    .then(res => res.json())
    .then(data => {
        swal({
            text: data.message,
            icon: "success"
        });
    })
    .catch(err => console.error("Wishlist error:", err));
}

// ================================
// LUXURY DYNAMIC INTERACTIONS
// ================================
window.showToast = function(message, type = 'success') {
    let container = document.getElementById('luxury-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'luxury-toast-container';
        container.style.cssText = 'position: fixed; top: 30px; right: 30px; z-index: 10000; display: flex; flex-direction: column; gap: 10px; pointer-events: none;';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `luxury-toast ${type}`;
    toast.style.cssText = `
        background: #111111;
        color: #ffffff;
        padding: 16px 28px;
        border-radius: 50px;
        font-family: 'Outfit', sans-serif;
        font-size: 0.85rem;
        font-weight: 400;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        transform: translateY(-20px);
        opacity: 0;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        pointer-events: auto;
        border: 1px solid rgba(255,255,255,0.1);
    `;
    
    const icon = document.createElement('i');
    icon.className = type === 'success' ? 'fa-solid fa-check text-success' : 'fa-solid fa-circle-exclamation text-warning';
    toast.appendChild(icon);
    
    const textNode = document.createTextNode(message);
    toast.appendChild(textNode);
    
    container.appendChild(toast);
    
    // trigger reflow
    toast.offsetHeight;
    
    toast.style.transform = 'translateY(0)';
    toast.style.opacity = '1';
    
    setTimeout(() => {
        toast.style.transform = 'translateY(-20px)';
        toast.style.opacity = '0';
        setTimeout(() => {
            toast.remove();
        }, 400);
    }, 3000);
};

window.updateCartBadges = function() {
    let count = 0;
    let items = document.querySelectorAll('#offcanvasCart [id^="card_item"], #offcanvasCart [id^="inner_card_item"]');
    count = items.length;
    
    document.querySelectorAll('.cart-count-badge').forEach(badge => {
        badge.textContent = count;
        if (count === 0) {
            badge.style.display = 'none';
        } else {
            badge.style.display = 'inline-block';
        }
    });
};

// Initial count on page load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(window.updateCartBadges, 800);
});