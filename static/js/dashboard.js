// Global variable to store gallery files - MOVED TO GLOBAL SCOPE
let galleryFiles = [];

window.addEventListener("load", () => {
  const p = document.getElementById("preloader");
  setTimeout(() => {
      p.classList.add("hide");
  }, 300);
});

document.addEventListener('DOMContentLoaded', function () {
    // ✅ 1. Sidebar Navigation with Persistent Active Tab + Premium Animation (MUST RUN FIRST)
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    const contentSections = document.querySelectorAll('.content-section');

    function activateTab(section) {
        navLinks.forEach(l => l.classList.remove('active'));
        contentSections.forEach(s => {
            s.classList.remove('active');
            s.style.animation = 'none';
            void s.offsetHeight;
        });

        const activeLink = document.querySelector(`.sidebar .nav-link[data-section="${section}"]`);
        const activeSection = document.getElementById(`${section}-section`);

        if (activeLink && activeSection) {
            activeLink.classList.add('active');
            activeSection.classList.add('active');
            activeSection.style.animation = 'sectionFadeIn 0.4s ease';
        }
    }

    // ✅ Load saved active tab on reload
    const savedSection = localStorage.getItem("activeSection") || "dashboard";
    activateTab(savedSection);

    // ✅ Set active tab on click
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            if (section) {
                localStorage.setItem("activeSection", section);
                activateTab(section);
            }
        });
    });

    // ✅ 2. Initialize Custom Rich Text Editors safely
    try {
        if (typeof initCustomEditor !== 'undefined') {
            if (document.getElementById('productDescription')) {
                initCustomEditor('#productDescription', { heightMin: 200, heightMax: 400 });
            }
            if (document.getElementById('productHighlight')) {
                initCustomEditor('#productHighlight', { heightMin: 150, heightMax: 300 });
            }
            if (document.getElementById('codinator_frola')) {
                initCustomEditor('#codinator_frola', { heightMin: 200, heightMax: 400 });
            }
            if (document.getElementById('coordinator_content_update')) {
                initCustomEditor('#coordinator_content_update', { heightMin: 200, heightMax: 400 });
            }
        }
    } catch (err) {
        console.warn('Custom Editor init skipped or failed:', err);
    }

    // ✅ Toggle product status
    const statusToggle = document.getElementById('productStatus');
    const statusText = document.getElementById('statusText');

    if (statusToggle) {
        statusToggle.addEventListener('change', function () {
            statusText.textContent = this.checked ? 'Active' : 'Inactive';
            statusText.className = this.checked ? 'status-badge status-active' : 'status-badge status-inactive';
        });
    }

    // ✅ Image preview drag/drop + click upload (SINGLE IMPLEMENTATION)
    const imageUploadArea = document.getElementById('imageUploadArea');
    const imageInput = document.getElementById('imageInput');
    const uploadImageBtn = document.getElementById('uploadImageBtn');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');

    // REMOVED: let galleryFiles = []; - NOW GLOBAL

    if (imageUploadArea) {
        // Open file browser when clicking the upload area or button
        imageUploadArea.addEventListener('click', () => imageInput.click());
        uploadImageBtn.addEventListener('click', (e) => { 
            e.stopPropagation(); 
            imageInput.click(); 
        });

        // Handle file selection
        imageInput.addEventListener('change', function () {
            if (this.files && this.files.length > 0) {
                for (let i = 0; i < this.files.length; i++) {
                    const file = this.files[i];
                    if (file.type.match('image.*')) {
                        // Add file to galleryFiles array
                        galleryFiles.push(file);

                        const reader = new FileReader();

                        reader.onload = function (e) {
                            const imagePreview = document.createElement('div');
                            imagePreview.className = 'image-preview';
                            imagePreview.setAttribute('data-file-name', file.name);

                            const img = document.createElement('img');
                            img.src = e.target.result;
                            img.alt = 'Product image preview';

                            const removeBtn = document.createElement('button');
                            removeBtn.type = 'button';
                            removeBtn.className = 'remove-image';
                            removeBtn.innerHTML = '<i class="fas fa-times"></i>';

                            removeBtn.addEventListener('click', function () {
                                // Remove from galleryFiles array
                                const fileName = imagePreview.getAttribute('data-file-name');
                                galleryFiles = galleryFiles.filter(f => f.name !== fileName);
                                imagePreview.remove();
                            });

                            imagePreview.appendChild(img);
                            imagePreview.appendChild(removeBtn);
                            imagePreviewContainer.appendChild(imagePreview);
                        };

                        reader.readAsDataURL(file);
                    }
                }
                console.log('Gallery files updated:', galleryFiles.length);
                this.value = '';
            }
        });

        // Drag and drop functionality
        imageUploadArea.addEventListener('dragover', function (e) {
            e.preventDefault();
            this.style.borderColor = '#3498db';
            this.style.backgroundColor = 'rgba(52, 152, 219, 0.1)';
        });

        imageUploadArea.addEventListener('dragleave', function () {
            this.style.borderColor = '#dee2e6';
            this.style.backgroundColor = '';
        });

        imageUploadArea.addEventListener('drop', function (e) {
            e.preventDefault();
            this.style.borderColor = '#dee2e6';
            this.style.backgroundColor = '';

            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                const files = Array.from(e.dataTransfer.files);
                files.forEach(file => {
                    if (file.type.match('image.*')) {
                        galleryFiles.push(file);

                        const reader = new FileReader();
                        reader.onload = function (e) {
                            const imagePreview = document.createElement('div');
                            imagePreview.className = 'image-preview';
                            imagePreview.setAttribute('data-file-name', file.name);

                            const img = document.createElement('img');
                            img.src = e.target.result;
                            img.alt = 'Product image preview';

                            const removeBtn = document.createElement('button');
                            removeBtn.type = 'button';
                            removeBtn.className = 'remove-image';
                            removeBtn.innerHTML = '<i class="fas fa-times"></i>';

                            removeBtn.addEventListener('click', function () {
                                const fileName = imagePreview.getAttribute('data-file-name');
                                galleryFiles = galleryFiles.filter(f => f.name !== fileName);
                                imagePreview.remove();
                            });

                            imagePreview.appendChild(img);
                            imagePreview.appendChild(removeBtn);
                            imagePreviewContainer.appendChild(imagePreview);
                        };
                        reader.readAsDataURL(file);
                    }
                });
                console.log('Gallery files from drop:', galleryFiles.length);
            }
        });
    }

    // ✅ Color Variants Functionality
    const colorVariantsContainer = document.getElementById('colorVariantsContainer');
    const addColorVariantBtn = document.getElementById('addColorVariant');
    let colorVariantCount = 0;

    if (addColorVariantBtn) {
        addColorVariantBtn.addEventListener('click', function () {
            colorVariantCount++;
            const variantId = `colorVariant${colorVariantCount}`;

            const variantCard = document.createElement('div');
            variantCard.className = 'card color-variant-card';
            variantCard.id = variantId;

            variantCard.innerHTML = `
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span>Color Variant #${colorVariantCount}</span>
                    <button type="button" class="btn btn-sm btn-danger remove-variant-btn">
                        <i class="fas fa-times"></i> Remove
                    </button>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Color Name</label>
                                <input type="text" class="form-control variant-color-name" required placeholder="e.g. Red, Blue, Black">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Color Code</label>
                                <div class="input-group">
                                    <input type="text" class="form-control variant-color-code" placeholder="e.g. #FF0000">
                                    <input type="color" required class="form-control form-control-color variant-color-picker" title="Choose color">
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Product Image</label>
                                <input type="file" required class="form-control variant-product-image" accept="image/*">
                                <div class="variant-image-preview mt-2" style="display: none;"></div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Image ALT Name</label>
                                <input type="text" required class="form-control variant-image-alt" placeholder="Image alternative text">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Gallery Images</label>
                        <input type="file" required class="form-control variant-gallery-images" multiple accept="image/*">
                        <div class="variant-gallery-container mt-2 d-flex"></div>
                    </div>
                </div>
            `;

            colorVariantsContainer.appendChild(variantCard);

            // Add event listeners for the new variant
            const removeBtn = variantCard.querySelector('.remove-variant-btn');
            const colorPicker = variantCard.querySelector('.variant-color-picker');
            const colorCodeInput = variantCard.querySelector('.variant-color-code');
            const productImageInput = variantCard.querySelector('.variant-product-image');
            const galleryImagesInput = variantCard.querySelector('.variant-gallery-images');

            removeBtn.addEventListener('click', function () {
                variantCard.remove();
            });

            // Color picker functionality
            colorPicker.addEventListener('input', function () {
                colorCodeInput.value = this.value;
            });

            colorCodeInput.addEventListener('input', function () {
                if (this.value.match(/^#[0-9A-F]{6}$/i)) {
                    colorPicker.value = this.value;
                }
            });

            // Product image preview
            productImageInput.addEventListener('change', function () {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    const previewContainer = variantCard.querySelector('.variant-image-preview');

                    reader.onload = function (e) {
                        previewContainer.innerHTML = `<img src="${e.target.result}" width="150" height="150" alt="Product preview">`;
                        previewContainer.style.display = 'flex';
                    };

                    reader.readAsDataURL(this.files[0]);
                }
            });

            // Gallery images preview
            galleryImagesInput.addEventListener('change', function () {
                const galleryContainer = variantCard.querySelector('.variant-gallery-container');
                galleryContainer.innerHTML = '';

                if (this.files && this.files.length > 0) {
                    for (let i = 0; i < this.files.length; i++) {
                        const file = this.files[i];
                        if (file.type.match('image.*')) {
                            const reader = new FileReader();

                            reader.onload = function (e) {
                                const removeBtn = document.createElement('button');
                                removeBtn.type = 'button';
                                removeBtn.className = 'remove-variant';
                                removeBtn.innerHTML = '<i class="fas fa-times"></i>';

                                removeBtn.addEventListener('click', function () {
                                    galleryItem.remove();
                                });

                                const galleryItem = document.createElement('div');
                                galleryItem.className = 'variant-image-preview';

                                const img = document.createElement('img');
                                img.src = e.target.result;
                                img.alt = 'Gallery image';
                                img.width = "150";
                                img.height = "150";

                                galleryItem.appendChild(img);
                                galleryItem.appendChild(removeBtn);
                                galleryContainer.appendChild(galleryItem);
                            };

                            reader.readAsDataURL(file);
                        }
                    }
                }
            });
        });
    }

    // ✅ Product search functionality
    const searchInput = document.getElementById('search_filter');
    const productItems = document.querySelectorAll('.product_item_dashbord');

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase().trim();
            const productList = document.getElementById('product-list');
            let noResultsMessage = document.getElementById('no-results-message');
            let hasVisibleItems = false;

            productItems.forEach(item => {
                const productName = item.querySelector('.text-gray-dark').textContent.toLowerCase();

                if (productName.includes(searchTerm)) {
                    item.classList.remove('hidden');
                    item.classList.add('highlight');
                    hasVisibleItems = true;
                } else {
                    item.classList.add('hidden');
                    item.classList.remove('highlight');
                }
            });

            // Show/hide no results message
            if (!hasVisibleItems) {
                if (!noResultsMessage) {
                    noResultsMessage = document.createElement('div');
                    noResultsMessage.id = 'no-results-message';
                    noResultsMessage.className = 'alert alert-info mt-3';
                    noResultsMessage.textContent = 'No products found matching your search.';
                    productList.appendChild(noResultsMessage);
                }
            } else if (noResultsMessage) {
                noResultsMessage.remove();
            }
        });
    }

    // ✅ Form submission
    const productForm = document.getElementById('productForm');
    if (productForm) {
        productForm.addEventListener('submit', function (e) {
            e.preventDefault();
            getAndSendProductData();
        });
    }
});

// ✅ Updated getAndSendProductData function - NOW CAN ACCESS galleryFiles
async function getAndSendProductData() {
    const formData = new FormData();
    const csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;

    // --- Basic Information ---
    formData.append("name", document.getElementById("productName").value);
    const descEl = document.getElementById("productDescription");
    const descVal = descEl._customEditorInstance ? descEl._customEditorInstance.getContent() : descEl.value;
    formData.append("description", descVal);

    const hlEl = document.getElementById("productHighlight");
    const hlVal = hlEl._customEditorInstance ? hlEl._customEditorInstance.getContent() : hlEl.value;
    formData.append("highlight", hlVal);
    const catVal = document.getElementById("productCategory") ? document.getElementById("productCategory").value : "";
    formData.append("category", (catVal === "None" || catVal === "null") ? "" : catVal);
    formData.append("brand", document.getElementById("productBrand") ? document.getElementById("productBrand").value : "");
    formData.append("ratings", document.getElementById("productratings") ? document.getElementById("productratings").value : "0");
    formData.append("total_sale_product", document.getElementById("total_sale_product") ? document.getElementById("total_sale_product").value : "0");
    formData.append("tshirt_type", document.getElementById("t-shirt-type") ? document.getElementById("t-shirt-type").value : "");
    formData.append("keywords", document.getElementById("key_word") ? document.getElementById("key_word").value : "");

    // --- Pricing & Inventory ---
    formData.append("sale_price", document.getElementById("sale-Price") ? document.getElementById("sale-Price").value : "0");
    formData.append("regular_price", document.getElementById("regularPrice") ? document.getElementById("regularPrice").value : "0");
    formData.append("color", document.getElementById("product-color") ? document.getElementById("product-color").value : "");
    formData.append("color_code", document.getElementById("product-color-code") ? document.getElementById("product-color-code").value : "");

    const qtyVal = document.getElementById("product_quantity_offer") ? document.getElementById("product_quantity_offer").value.trim() : "";
    formData.append("product_quantity_offer", (qtyVal === "None" || qtyVal === "null") ? "" : qtyVal);

    const amtVal = document.getElementById("product_amount_offer") ? document.getElementById("product_amount_offer").value.trim() : "";
    formData.append("product_amount_offer", (amtVal === "None" || amtVal === "null") ? "" : amtVal);

    // --- Product Image ---
    const productImage = document.getElementById("product_image").files[0];
    if (productImage) formData.append("main_image", productImage);
    formData.append("image_alt", document.getElementById("imagealtname").value);

    // --- Status & Options ---
    formData.append("is_active", document.getElementById("productStatus").checked ? "true" : "false");
    formData.append("show_at_home", document.getElementById("onlineStore").checked ? "true" : "false");

    // --- Sizes (checkboxes) ---
    const sizes = [];
    document.querySelectorAll('input[id^="size_"]:checked, input[name="sizes"]:checked').forEach(chk => {
        const val = (chk.value || '').trim();
        if (val && !['1', '0', 'on', 'true', 'false'].includes(val.toLowerCase()) && !/^\d+$/.test(val)) {
            const upper = val.toUpperCase();
            if (!sizes.includes(upper)) {
                sizes.push(upper);
            }
        }
    });
    formData.append("sizes", JSON.stringify(sizes));

    // --- MAIN PRODUCT GALLERY IMAGES ---
    console.log("Gallery files array:", galleryFiles);
    if (galleryFiles.length > 0) {
        galleryFiles.forEach((file, index) => {
            formData.append("gallery_images", file);
            console.log(`Added gallery image ${index}:`, file.name);
        });
    } else {
        console.log("No gallery images in galleryFiles array");
    }

    // --- COLOR VARIANTS ---
    const colorVariants = [];
    let variantIndex = 0;

    document.querySelectorAll('.color-variant-card').forEach(card => {
        const colorName = card.querySelector('.variant-color-name')?.value || '';
        const colorCode = card.querySelector('.variant-color-code')?.value || '';
        const imageAlt = card.querySelector('.variant-image-alt')?.value || '';
        const imageFile = card.querySelector('.variant-product-image')?.files[0] || null;

        // Get gallery files for this variant
        const galleryFiles = card.querySelector('.variant-gallery-images')?.files || [];

        // Add variant main image to formData
        if (imageFile) {
            formData.append(`variant_image_${variantIndex}`, imageFile);
        }

        // Add variant gallery images to formData
        for (let i = 0; i < galleryFiles.length; i++) {
            formData.append(`variant_gallery_${variantIndex}_${i}`, galleryFiles[i]);
        }

        colorVariants.push({
            color_name: colorName,
            color_code: colorCode,
            image_alt: imageAlt,
            variant_index: variantIndex,
            gallery_count: galleryFiles.length
        });

        variantIndex++;
    });

    formData.append("color_variants", JSON.stringify(colorVariants));

    console.log("✅ Final Data:");
    console.log("- Main Gallery images:", galleryFiles.length);
    console.log("- Color variants:", colorVariants.length);

    // --- Send data to Django ---
    try {
        let btn_form=document.getElementById("form_add_product_btn")
        let btn_form_spin=document.getElementById("form_add_product_btn_spin")
        btn_form_spin.style.display="block"
        btn_form.style.display="none"
        const response = await fetch("/usvesta-deshboard", {
            method: "POST",
            body: formData,
            headers: { "X-CSRFToken": csrf_token }
        });

        if (response.ok) {
            const data = await response.json();
            btn_form_spin.style.display="none";
            btn_form.style.display="block";
            if (data.status === "error") {
                swal({
                    text: "❌ Error: " + (data.message || "Failed to save product"),
                    icon: "error",
                });
                return;
            }
            swal({
                text: "✅ Product saved successfully!",
                icon: "success",
            }).then(() => {
                // Reset gallery files after successful submission
                galleryFiles = [];
                const imagePreviewContainer = document.getElementById('imagePreviewContainer');
                if (imagePreviewContainer) imagePreviewContainer.innerHTML = '';
                window.location.reload();
            });
        } else {
            swal({
                text: "❌ Error saving product.",
                icon: "error",
            });
        }
    } catch (error) {
        console.error("Network error:", error);
        swal({
            text: "⚠️ Failed to send data to the server.",
            icon: "warning",
        });
    }
}

// ... REST OF THE FUNCTIONS REMAIN THE SAME ...
// (Category Management, Product Management, Coordinator, Reviews, Order Functions)

// ✅ Category Management Functions
function Category_delete(p_id) {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    formdata0 = new FormData()
    formdata0.append("remove_category", p_id)

    fetch("/usvesta-deshboard", {
        method: "POST",
        body: formdata0,
        headers: {
            "X-CSRFToken": csrf_token,
        }
    })
    .then(res => res.json())
    .then(data => {
        swal({
            text: data.res,
            icon: "success",
        }).then(() => window.location.reload());
    })
    .catch(error => console.error("Error:", error));
}

function SubCategory_delete(p_id) {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    formdata0 = new FormData()
    formdata0.append("remove_sub_category", p_id)

    fetch("/usvesta-deshboard", {
        method: "POST",
        body: formdata0,
        headers: {
            "X-CSRFToken": csrf_token,
        }
    })
    .then(res => res.json())
    .then(data => {
        swal({
            text: data.res,
            icon: "success",
        }).then(() => window.location.reload());
    })
    .catch(error => console.error("Error:", error));
}

function open_categoryedit_model(p_id, nme) {
    document.getElementById("editcategoryid").value = p_id;
    document.getElementById("editcategory").value = nme;
    var myModal = new bootstrap.Modal(document.getElementById('categorymodel'));
    myModal.show();
}

function open_sub_categoryedit_model(cid, p_nm) {
    document.getElementById("subeditcategory").value = p_nm;
    document.getElementById("subeditcategoryid").value = cid;
    var myModal = new bootstrap.Modal(document.getElementById('subcategorymodeledit'));
    myModal.show();
}

function Edit_category() {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    const form = document.getElementById("editocategoryform");
    let formdata0 = new FormData(form);

    fetch("/usvesta-deshboard", {
        method: "POST",
        body: formdata0,
        headers: {
            "X-CSRFToken": csrf_token,
        }
    })
    .then(res => res.json())
    .then(data => {
        swal({
            text: data.res,
            icon: "success",
        }).then(() => window.location.reload());
    })
    .catch(error => console.error("Error:", error));
}

function Edit_sub_category() {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    const form = document.getElementById("editosubcategoryform");
    let formdata0 = new FormData(form);

    fetch("/usvesta-deshboard", {
        method: "POST",
        body: formdata0,
        headers: {
            "X-CSRFToken": csrf_token,
        }
    })
    .then(res => res.json())
    .then(data => {
        swal({
            text: data.res,
            icon: "success",
        }).then(() => window.location.reload());
    })
    .catch(error => console.error("Error:", error));
}

function submitCategory() {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    const form = document.getElementById("categoryForm");
    const formData = new FormData(form);

    fetch("/usvesta-deshboard", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrf_token,
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        swal({
            text: data.res,
            icon: "success",
        }).then(() => window.location.reload());
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function submitsubCategory() {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    const form = document.getElementById("subcategoryForm");
    const formData = new FormData(form);

    fetch("/usvesta-deshboard", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrf_token,
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        swal({
            text: data.res,
            icon: "success",
        }).then(() => window.location.reload());
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

// ✅ Product Management Functions
function product_delete(p_id, removethatitem) {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    formdata0 = new FormData()
    formdata0.append("remove_product_from_crm", p_id)

    fetch("/usvesta-deshboard", {
        method: "POST",
        body: formdata0,
        headers: {
            "X-CSRFToken": csrf_token,
        }
    })
    .then(res => res.json())
    .then(data => {
        swal({
            text: data.res,
            icon: "success",
        }).then(() => {
            let productRow = removethatitem.closest(".d-flex.text-muted.pt-3");
            if (productRow) productRow.remove();
        });
    })
    .catch(error => console.error("Error:", error));
}

function Iner_product_delete(p_id, removethatitem) {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    formdata0 = new FormData()
    formdata0.append("inner_remove_product_from_crm", p_id)

    fetch("/usvesta-deshboard", {
        method: "POST",
        body: formdata0,
        headers: {
            "X-CSRFToken": csrf_token,
        }
    })
    .then(res => res.json())
    .then(data => {
        swal({
            text: data.res,
            icon: "success",
        }).then(() => {
            let productRow = removethatitem.closest(".d-flex.text-muted.pt-3");
            if (productRow) productRow.remove();
        });
    })
    .catch(error => console.error("Error:", error));
}

function add_product_form() {
    document.getElementById("productForm").style.display = "block";
    document.getElementById("all_products_list").style.display = "none";
    document.getElementById("bulk_product_add_form").style.display = "none";

    
}
function add_product_form_in_bulk() {
    document.getElementById("bulk_product_add_form").style.display = "block";
    document.getElementById("productForm").style.display = "none";
    document.getElementById("all_products_list").style.display = "none";
    
}
document.addEventListener("DOMContentLoaded", function () {

    const bulkForm = document.getElementById("bulk_product_add_form");
    const progressBox = document.getElementById("uploadProgressBox");
    const progressBar = document.getElementById("uploadProgressBar");
    const progressText = document.getElementById("uploadProgressText");

    // 🛑 SAFETY CHECK
    if (!bulkForm || !progressBox || !progressBar || !progressText) {
        console.error("Progress bar elements not found in HTML");
        return;
    }

    bulkForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(bulkForm);
        const csrf = document.querySelector("[name='csrfmiddlewaretoken']").value;

        // ✅ FORCE SHOW PROGRESS BAR
        progressBox.style.display = "block";
        progressBar.style.width = "5%";
        progressText.innerText = "Starting upload...";

        let progress = 5;
        const fakeProgress = setInterval(() => {
            if (progress < 90) {
                progress += 5;
                progressBar.style.width = progress + "%";
                progressText.innerText = `Uploading products... ${progress}%`;
            }
        }, 500);

        try {
            const response = await fetch("/upload-bulk-order", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": csrf
                }
            });

            const data = await response.json();

            clearInterval(fakeProgress);
            progressBar.style.width = "100%";
            progressText.innerText = "Finalizing upload...";

            setTimeout(() => {
                if (data.status === "success") {
                    swal({
                        text: `✅ ${data.created} Products Added
❌ ${data.skipped} Skipped`,
                        icon: "success"
                    }).then(() => location.reload());
                } else {
                    swal({
                        text: data.message,
                        icon: "error"
                    });
                }
            }, 600);

        } catch (err) {
            clearInterval(fakeProgress);
            progressBar.style.width = "0%";
            progressText.innerText = "Upload failed";

            swal({
                text: "Upload failed. Please try again.",
                icon: "error"
            });
        }
    });
});


// ================= BULK DELETE & CHECK-ALL FUNCTIONS =================
function toggleCheckAll(type, source) {
    const checkboxes = document.querySelectorAll(`.${type}-checkbox`);
    const headCheckbox = type === 'product' ? document.getElementById('checkAllProductsHead') : document.getElementById('checkAllOrdersHead');
    const mainCheckbox = type === 'product' ? document.getElementById('checkAllProducts') : document.getElementById('checkAllOrders');
    checkboxes.forEach(cb => cb.checked = source.checked);
    if (headCheckbox && headCheckbox !== source) headCheckbox.checked = source.checked;
    if (mainCheckbox && mainCheckbox !== source) mainCheckbox.checked = source.checked;
    updateBulkDeleteBtn(type);
}

function updateBulkDeleteBtn(type) {
    const checked = document.querySelectorAll(`.${type}-checkbox:checked`);
    const btn = document.getElementById(type === 'product' ? 'bulkDeleteProductsBtn' : 'bulkDeleteOrdersBtn');
    const count = document.getElementById(type === 'product' ? 'selectedProductsCount' : 'selectedOrdersCount');
    if (checked.length > 0) {
        btn.style.display = 'inline-flex';
        count.textContent = checked.length;
    } else {
        btn.style.display = 'none';
        count.textContent = '0';
    }
}

function bulkDeleteProducts() {
    const checked = document.querySelectorAll('.product-checkbox:checked');
    if (checked.length === 0) return swal({ text: 'Please select at least one product.', icon: 'warning' });
    swal({
        title: 'Are you sure?',
        text: `Delete ${checked.length} product(s)? This action cannot be undone.`,
        icon: 'warning',
        buttons: ['Cancel', 'Delete'],
        dangerMode: true,
    }).then(willDelete => {
        if (!willDelete) return;
        const csrf = document.querySelector("[name='csrfmiddlewaretoken']").value;
        const formData = new FormData();
        formData.append('bulk_delete_products', 'true');
        checked.forEach(cb => {
            const row = cb.closest('tr');
            const id = row.getAttribute('data-product-id');
            if (id) formData.append('product_ids[]', id);
        });
        fetch('/usvesta-deshboard', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': csrf }
        }).then(r => r.json()).then(d => {
            swal({ text: d.res, icon: 'success' }).then(() => location.reload());
        }).catch(() => swal({ text: 'Error deleting products.', icon: 'error' }));
    });
}

function bulkDeleteOrders() {
    const checked = document.querySelectorAll('.order-checkbox:checked');
    if (checked.length === 0) return swal({ text: 'Please select at least one order.', icon: 'warning' });
    swal({
        title: 'Are you sure?',
        text: `Delete ${checked.length} order(s)? This action cannot be undone.`,
        icon: 'warning',
        buttons: ['Cancel', 'Delete'],
        dangerMode: true,
    }).then(willDelete => {
        if (!willDelete) return;
        const csrf = document.querySelector("[name='csrfmiddlewaretoken']").value;
        const formData = new FormData();
        formData.append('bulk_delete_orders', 'true');
        checked.forEach(cb => {
            const row = cb.closest('tr');
            const id = row.getAttribute('data-order-id');
            if (id) formData.append('order_ids[]', id);
        });
        fetch('/usvesta-deshboard', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': csrf }
        }).then(r => r.json()).then(d => {
            swal({ text: d.res, icon: 'success' }).then(() => location.reload());
        }).catch(() => swal({ text: 'Error deleting orders.', icon: 'error' }));
    });
}

function deleteOrder(orderId, btn) {
    swal({
        title: 'Delete Order?',
        text: 'This action cannot be undone.',
        icon: 'warning',
        buttons: ['Cancel', 'Delete'],
        dangerMode: true,
    }).then(willDelete => {
        if (!willDelete) return;
        const csrf = document.querySelector("[name='csrfmiddlewaretoken']").value;
        const formData = new FormData();
        formData.append('delete_single_order', 'true');
        formData.append('order_id', orderId);
        fetch('/usvesta-deshboard', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': csrf }
        }).then(r => r.json()).then(d => {
            swal({ text: d.res, icon: 'success' }).then(() => {
                const row = btn.closest('tr');
                if (row) row.remove();
            });
        }).catch(() => swal({ text: 'Error deleting order.', icon: 'error' }));
    });
}

function show_product_list_form() {
    document.getElementById("productForm").style.display = "none";
    document.getElementById("all_products_list").style.display = "block";
    document.getElementById("bulk_product_add_form").style.display = "none";

}

function dashboard_product_edit(pid, product_type) {
    
    document.getElementById("productForm").style.display = "none";
    document.getElementById("all_products_list").style.display = "none";
    document.getElementById("set_id_of_edit_product").value = pid;
}

// ✅ Coordinator Functions
function Coordinator_add_form() {
    document.getElementById("adding_coodinator_form").style.display = "block";
    document.getElementById("coodinator_list").style.display = "none";
}

function Coordinator_edit_form(name, sub_cat,subcat_id, content, cid, pages) {
    document.getElementById("coordinator_name_update").value = name;
    
    let contentField = document.getElementById("coordinator_content_update");
    if(contentField) {
        contentField.value = content;
        if(window.jQuery && window.jQuery(contentField).summernote) {
            window.jQuery(contentField).summernote('code', content);
        }
        else if (contentField['froalaEditor']) {
            window.jQuery(contentField).froalaEditor('html.set', content);
        }
    }
    
    document.getElementById("coordinator_update_id").value = cid;
    document.getElementById("coordinator_sub_category_update").textContent = sub_cat;
    document.getElementById("coordinator_sub_category_update").value = subcat_id;

    let selectEl = document.getElementById("show_on_pages_update");
    if (selectEl && pages) {
        for (let i = 0; i < selectEl.options.length; i++) {
            if (pages.includes(selectEl.options[i].value)) {
                selectEl.options[i].selected = true;
            } else {
                selectEl.options[i].selected = false;
            }
        }
    }

    document.getElementById("adding_coodinator_form").style.display = "none";
    document.getElementById("coodinator_list").style.display = "none";
    document.getElementById("update_coodinator_form").style.display = "block";
}

function Coordinator_show_list() {
    document.getElementById("adding_coodinator_form").style.display = "none";
    document.getElementById("coodinator_list").style.display = "block";
    document.getElementById("update_coodinator_form").style.display = "none";
}

function Coordinator_delete(p_id, removethatitem) {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    formdata0 = new FormData()
    formdata0.append("coordinator_delete_id", p_id)

    fetch("/usvesta-deshboard-sending_databdbjajnsjansJnj", {
        method: "POST",
        body: formdata0,
        headers: {
            "X-CSRFToken": csrf_token,
        }
    })
    .then(res => res.json())
    .then(data => {
        swal({
            text: data.res,
            icon: "success",
        }).then(() => {
            let row = removethatitem.closest("tr");
            if (row) row.remove();
        });
    })
    .catch(error => console.error("Error:", error));
}

// ✅ Reviews Functions
function review_add_form() {
    document.getElementById("adding_reviews_form").style.display = "block";
    document.getElementById("reviweslist").style.display = "none";
    document.getElementById("update_reviews_form").style.display = "none";
}

function review_edit_form(name, email, msg, star, show, rid) {
    document.getElementById("adding_reviews_form").style.display = "none";
    document.getElementById("reviweslist").style.display = "none";
    document.getElementById("update_reviews_form").style.display = "block";

    document.getElementById("update_review_name").value = name;
    document.getElementById("update_review_email").value = email;
    document.getElementById("update_reviews_meseje").value = msg;
    document.getElementById("update_review_id").value = rid;

    const checkbox = document.getElementById("update_reviews_showhide");
    checkbox.checked = show === true || show === 1 || show === "True" || show === "true";

    const starInputs = document.querySelectorAll('input[name="update_reviews_rating"]');
    starInputs.forEach(input => {
        input.checked = parseInt(input.value) === parseInt(star);
    });

    document.getElementById("update_reviews_form").scrollIntoView({ behavior: "smooth" });
}

function review_show_list() {
    document.getElementById("adding_reviews_form").style.display = "none";
    document.getElementById("reviweslist").style.display = "block";
    document.getElementById("update_reviews_form").style.display = "none";
}

function review_delete(p_id, removethatitem) {
    let csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    formdata0 = new FormData()
    formdata0.append("review_delete_id", p_id)

    fetch("/usvesta-deshboard-sending_databdbjajnsjansJnj", {
        method: "POST",
        body: formdata0,
        headers: {
            "X-CSRFToken": csrf_token,
        }
    })
    .then(res => res.json())
    .then(data => {
        swal({
            text: data.res,
            icon: "success",
        }).then(() => {
            let row = removethatitem.closest("tr");
            if (row) row.remove();
        });
    })
    .catch(error => console.error("Error:", error));
}

// ✅ Order Functions
function view_order_details_in_dashboard(order_id) {
    const csrf_token = document.querySelector("[name='csrfmiddlewaretoken']").value;
    const form = new FormData();
    form.append("order_id", order_id);

    fetch("/ordermodel_popup", {
        method: "POST",
        body: form,
        headers: {
            "X-CSRFToken": csrf_token,
        },
    })
    .then(res => res.text())
    .then(html => {
        const oldModal = document.getElementById("orderDetailsModal");
        if (oldModal) oldModal.remove();

        document.body.insertAdjacentHTML("beforeend", html);

        const modalElement = document.getElementById("orderDetailsModal");
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    })
    .catch(error => console.error("Error:", error));
}

function set_order_st(pid, currentStatus) {
    let inputEl = document.getElementById("product_id_set_order");
    if (inputEl) inputEl.value = pid;

    let selectEl = document.getElementById("o_status_select");
    if (selectEl && currentStatus) {
        selectEl.value = currentStatus;
    }

    let modalEl = document.getElementById('exampleModal003');
    if (modalEl) {
        if (modalEl.parentElement !== document.body) {
            document.body.appendChild(modalEl);
        }
        modalEl.style.zIndex = "1060";
        try {
            if (window.bootstrap && bootstrap.Modal) {
                let modalInstance = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
                modalInstance.show();
            } else if (window.$ && $.fn.modal) {
                $(modalEl).modal('show');
            } else {
                modalEl.classList.add('show');
                modalEl.style.display = 'block';
            }
        } catch(e) {
            console.log("Modal trigger error:", e);
        }
    }
}






document.getElementById("generateReviewsBtn").addEventListener("click", function () {

    if (!confirm("Generate 5 fake reviews for ALL products?")) return;

    const progressBox = document.getElementById("reviewProgressBox");
    const progressBar = document.getElementById("reviewProgressBar");
    const progressText = document.getElementById("reviewProgressText");

    // 🔹 Show progress UI
    progressBox.style.display = "block";
    progressBar.style.width = "5%";
    progressText.innerText = "Starting review generation...";

    let progress = 5;
    const fakeProgress = setInterval(() => {
        if (progress < 90) {
            progress += 5;
            progressBar.style.width = progress + "%";
            progressText.innerText = `Generating fake reviews... ${progress}%`;
        }
    }, 500);

    fetch("/generate-fake-reviews", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        }
    })
    .then(res => res.json())
    .then(data => {
        clearInterval(fakeProgress);
        progressBar.style.width = "100%";
        progressText.innerText = "Finalizing...";

        setTimeout(() => {
            if (data.status === "success") {
                alert(`✅ ${data.created} reviews generated`);
                window.location.reload()
            } else {
                alert(data.message);
            }
        }, 500);
    })
    .catch(() => {
        clearInterval(fakeProgress);
        progressBar.style.width = "0%";
        progressText.innerText = "Failed";

        alert("Something went wrong");
    });
});
