function initProductDetailsScripts() {
    // ---------------------------------
    // 1. GALLERY VIEW MORE / LESS TOGGLE
    // ---------------------------------
    const productItems = document.querySelectorAll(".index_page_product");
    const viewMoreBtn = document.getElementById("viewMoreBtn");

    if (productItems.length > 0 && viewMoreBtn) {
        // Main Image (1) + 3 Gallery Images = 4 Total Visible Images initially
        const maxInitialGalleryVisible = 3;

        if (productItems.length > maxInitialGalleryVisible) {
            productItems.forEach((item, index) => {
                if (index >= maxInitialGalleryVisible) {
                    item.style.display = "none";
                } else {
                    item.style.display = "block";
                }
            });

            viewMoreBtn.style.display = "inline-block";
            viewMoreBtn.textContent = "View More";

            let expandedGallery = false;
            viewMoreBtn.onclick = function (e) {
                if (e) e.preventDefault();
                expandedGallery = !expandedGallery;

                productItems.forEach((item, index) => {
                    if (index >= maxInitialGalleryVisible) {
                        item.style.display = expandedGallery ? "block" : "none";
                    }
                });

                if (expandedGallery) {
                    viewMoreBtn.textContent = "View Less";
                } else {
                    viewMoreBtn.textContent = "View More";
                    window.scrollTo({ top: viewMoreBtn.offsetTop - 350, behavior: "smooth" });
                }
            };
        } else {
            viewMoreBtn.style.display = "none";
        }
    }

    // ---------------------------------
    // 2. READ MORE / LESS (Description)
    // ---------------------------------
    const descBox = document.getElementById("descBox");
    const descBtn = document.getElementById("descReadMoreBtn");
    if (descBox && descBtn) {
        if (descBox.scrollHeight > 130) {
            descBtn.style.display = "inline-flex";
        } else {
            descBtn.style.display = "none";
        }
        descBtn.onclick = function (e) {
            if (e) e.preventDefault();
            toggleDesc();
        };
    }

    // ---------------------------------
    // 3. READ MORE / LESS (Highlights)
    // ---------------------------------
    const highlightText = document.getElementById("highlightText");
    const highlightBtn = document.getElementById("highlightReadMoreBtn");
    if (highlightText && highlightBtn) {
        if (highlightText.scrollHeight > 120) {
            highlightBtn.style.display = "inline-flex";
        } else {
            highlightBtn.style.display = "none";
        }
        let expandedHighlight = false;
        highlightBtn.onclick = function (e) {
            if (e) e.preventDefault();
            expandedHighlight = !expandedHighlight;
            if (expandedHighlight) {
                highlightText.style.maxHeight = "none";
                highlightBtn.innerHTML = '<span>Read Less</span> <i class="fas fa-chevron-up ms-1"></i>';
            } else {
                highlightText.style.maxHeight = "100px";
                highlightBtn.innerHTML = '<span>Read More</span> <i class="fas fa-chevron-down ms-1"></i>';
            }
        };
    }
}

// Global Description Toggle Function
function toggleDesc() {
    var box = document.getElementById("descBox");
    var btn = document.getElementById("descReadMoreBtn");

    if (box) {
        box.classList.toggle("active");
        if (box.classList.contains("active")) {
            box.style.maxHeight = "none";
            if (btn) btn.innerHTML = '<span>Read Less</span> <i class="fas fa-chevron-up ms-1"></i>';
        } else {
            box.style.maxHeight = "120px";
            if (btn) btn.innerHTML = '<span>Read More</span> <i class="fas fa-chevron-down ms-1"></i>';
        }
    }
}

// Document Load Handlers
document.addEventListener("DOMContentLoaded", function () {
    initProductDetailsScripts();
});

window.addEventListener("load", function () {
    initProductDetailsScripts();
});

if (document.body) {
    document.body.addEventListener('htmx:afterSwap', function () {
        initProductDetailsScripts();
    });
}