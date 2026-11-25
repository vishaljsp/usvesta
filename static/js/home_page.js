// ============================================
// US VESTA — Premium Brand Interactions v5.0
// ============================================

document.addEventListener('DOMContentLoaded', function() {

    const isHomePage = window.location.pathname === '/' || window.location.pathname === '/index.html' || document.body.classList.contains('home-page');

    // =========== LUXURY CUSTOM CURSOR & MAGNETIC BUTTONS ===========
    if (typeof gsap !== 'undefined' && window.innerWidth > 992) {
        const cursor = document.createElement('div');
        const follower = document.createElement('div');
        cursor.className = 'luxury-cursor';
        follower.className = 'luxury-cursor-follower';
        document.body.appendChild(cursor);
        document.body.appendChild(follower);

        document.addEventListener('mousemove', (e) => {
            gsap.to(cursor, { x: e.clientX, y: e.clientY, duration: 0.08 });
            gsap.to(follower, { x: e.clientX, y: e.clientY, duration: 0.25 });
        });

        document.body.addEventListener('mouseenter', (e) => {
            const target = e.target.closest('a, button, .luxury-quick-add, .swiper-btn-prev, .swiper-btn-next, .faq-question-luxury, .search-trigger, .luxury-cat-card, .luxury-product-card');
            if (target) {
                cursor.classList.add('active');
                follower.classList.add('active');
            }
        }, true);

        document.body.addEventListener('mouseleave', (e) => {
            const target = e.target.closest('a, button, .luxury-quick-add, .swiper-btn-prev, .swiper-btn-next, .faq-question-luxury, .search-trigger, .luxury-cat-card, .luxury-product-card');
            if (target) {
                cursor.classList.remove('active');
                follower.classList.remove('active');
            }
        }, true);

        // Magnetic hover effect on luxury buttons
        document.querySelectorAll('.btn-luxury-outline, .btn-luxury-link, .swiper-btn-prev, .swiper-btn-next').forEach((btn) => {
            btn.addEventListener('mousemove', (e) => {
                const rect = btn.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                gsap.to(btn, { x: x * 0.25, y: y * 0.25, duration: 0.4, ease: 'power2.out' });
            });
            btn.addEventListener('mouseleave', () => {
                gsap.to(btn, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1, 0.4)' });
            });
        });
    }

    // =========== HERO SLIDER SWIPER ===========
    if (isHomePage && typeof Swiper !== 'undefined') {
        const heroEl = document.querySelector('.hero-swiper');
        if (heroEl) {
            new Swiper('.hero-swiper', {
                effect: 'fade',
                fadeEffect: { crossFade: true },
                speed: 1200,
                loop: true,
                autoplay: {
                    delay: 5000,
                    disableOnInteraction: false,
                },
                pagination: {
                    el: '.hero-swiper-pagination',
                    clickable: true,
                },
                navigation: {
                    nextEl: '.hero-swiper-btn-next',
                    prevEl: '.hero-swiper-btn-prev',
                },
            });
        }
    }

    // =========== NEW ARRIVALS SWIPER ===========
    if (isHomePage && typeof Swiper !== 'undefined') {
        const arrivalsEl = document.querySelector('.new-arrivals-swiper');
        if (arrivalsEl) {
            new Swiper('.new-arrivals-swiper', {
                slidesPerView: 1.2,
                spaceBetween: 20,
                grabCursor: true,
                navigation: {
                    nextEl: '.swiper-btn-next',
                    prevEl: '.swiper-btn-prev',
                },
                breakpoints: {
                    576: { slidesPerView: 2.2, spaceBetween: 24 },
                    992: { slidesPerView: 3.2, spaceBetween: 28 },
                    1200: { slidesPerView: 4, spaceBetween: 32 },
                },
            });
        }
    }

    // =========== GSAP ANIMATIONS (Homepage) ===========
    if (isHomePage && typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        // Hero entrance
        if (document.querySelector('.hero-eyebrow, .hero-title')) {
            const heroTl = gsap.timeline({ delay: 0.15 });
            heroTl.from('.hero-eyebrow', { opacity: 0, y: 24, duration: 1, ease: 'power3.out' })
                  .from('.hero-title', { opacity: 0, y: 50, duration: 1.2, ease: 'power3.out' }, '-=0.5')
                  .from('.hero-subtitle', { opacity: 0, y: 30, duration: 1, ease: 'power3.out' }, '-=0.6')
                  .from('.btn-luxury-outline', { opacity: 0, y: 24, duration: 0.8, ease: 'power3.out' }, '-=0.4');
        }

        // Hero parallax
        const heroMedia = document.querySelector('.hero-bg-media img, .hero-bg-media video');
        const heroSection = document.querySelector('.cinematic-hero');
        if (heroMedia && heroSection) {
            gsap.to(heroMedia, {
                y: '15%',
                ease: 'none',
                scrollTrigger: { trigger: heroSection, start: 'top top', end: 'bottom top', scrub: true }
            });
        }

        // Parallax elements
        document.querySelectorAll('[data-parallax]').forEach(el => {
            const amount = parseFloat(el.dataset.parallax) || 0.1;
            gsap.to(el.querySelector('img, video') || el, {
                y: `${amount * 100}%`,
                ease: 'none',
                scrollTrigger: {
                    trigger: el.closest('section') || el,
                    start: 'top bottom',
                    end: 'bottom top',
                    scrub: true
                }
            });
        });

        // Universal reveal animations (skip staggered items)
        const staggeredSelectors = '.luxury-cat-card, .luxury-product-card--minimal, .why-card-luxury, .testimonial-card-luxury, .insta-magazine-item, .faq-item-luxury, .timeline-item, .philosophy-card, .gallery-item, .stat-card-luxury';

        gsap.utils.toArray('[data-reveal]').forEach((el) => {
            if (el.matches(staggeredSelectors)) return;
            gsap.from(el, {
                opacity: 0,
                y: 40,
                duration: 1,
                ease: 'power3.out',
                scrollTrigger: {
                    trigger: el,
                    start: 'top 88%',
                    toggleActions: 'play none none none'
                }
            });
        });

        // Stagger groups
        const staggerGroups = [
            { selector: '.luxury-cat-card', trigger: '#categorySection' },
            // Best Sellers cards
            { selector: '#bestSellers .luxury-product-card--minimal', trigger: '#bestSellers' },
            // New Arrivals cards — separate trigger so they animate independently
            { selector: '#newArrivals .luxury-product-card--minimal', trigger: '#newArrivals' },
            { selector: '.why-card-luxury', trigger: '#whyChooseUs' },
            { selector: '.testimonial-card-luxury', trigger: '#testimonials' },
            { selector: '.insta-magazine-item', trigger: '#instagram' },
            { selector: '.faq-item-luxury', trigger: '#faq' },
            { selector: '.timeline-item', trigger: '#brandTimeline' },
            { selector: '.philosophy-card', trigger: '#designPhilosophy' },
            { selector: '.gallery-item', trigger: '#customerGallery' },
            { selector: '.stat-card-luxury', trigger: '#luxuryStats' },
        ];

        staggerGroups.forEach(({ selector, trigger }) => {
            const items = document.querySelectorAll(selector);
            if (items.length) {
                gsap.from(items, {
                    opacity: 0,
                    y: 35,
                    duration: 0.9,
                    stagger: 0.08,
                    ease: 'power3.out',
                    scrollTrigger: {
                        trigger: trigger,
                        start: 'top 85%',
                        toggleActions: 'play none none none'
                    }
                });
            }
        });

        // Counter animation
        document.querySelectorAll('.stat-number[data-count]').forEach(counter => {
            const target = parseInt(counter.dataset.count, 10);
            const obj = { val: 0 };
            gsap.to(obj, {
                val: target,
                duration: 2,
                ease: 'power2.out',
                scrollTrigger: {
                    trigger: counter.closest('.stat-card-luxury'),
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                },
                onUpdate: () => {
                    counter.textContent = Math.round(obj.val);
                }
            });
        });

        // Section title line reveal
        gsap.utils.toArray('.luxury-section-title').forEach(title => {
            gsap.from(title, {
                opacity: 0,
                y: 30,
                duration: 1,
                ease: 'power3.out',
                scrollTrigger: {
                    trigger: title,
                    start: 'top 90%',
                    toggleActions: 'play none none none'
                }
            });
        });
    }

    // =========== GSAP SCROLLTRIGGER REFRESH ON RESIZE ===========
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (typeof ScrollTrigger !== 'undefined') {
                ScrollTrigger.refresh();
            }
        }, 250);
    });
    
    // Failsafe timer: if GSAP fails or scroll animations don't trigger, force elements visible
    setTimeout(() => {
        document.querySelectorAll('[data-reveal], .luxury-cat-card, .luxury-product-card--minimal, .why-card-luxury, .testimonial-card-luxury, .insta-magazine-item, .faq-item-luxury, .timeline-item, .philosophy-card, .gallery-item, .stat-card-luxury').forEach(el => {
            const computedOpacity = parseFloat(window.getComputedStyle(el).opacity);
            if (computedOpacity < 0.1 || el.style.opacity === '0') {
                if (typeof gsap !== 'undefined') {
                    gsap.killTweensOf(el);
                }
                el.style.opacity = '1';
                el.style.transform = 'none';
                el.style.visibility = 'visible';
            }
        });
    }, 1500);
});

// =========== MOBILE TOUCH: Show product card actions on tap ===========
// On touch devices, hover never fires. This gives touch users the same access.
(function() {
    if (!('ontouchstart' in window)) return; // Desktop only uses hover

    function handleTouch(e) {
        var card = e.target.closest('.luxury-product-card');
        if (!card) {
            // Tapped outside — close any open cards
            document.querySelectorAll('.luxury-product-card.touch-active').forEach(function(c) {
                c.classList.remove('touch-active');
            });
            return;
        }
        // If already open and tapping a button, let the button handle it
        if (e.target.closest('.action-btn, .luxury-quick-add, a')) return;
        // Toggle touch-active on this card
        var isActive = card.classList.contains('touch-active');
        document.querySelectorAll('.luxury-product-card.touch-active').forEach(function(c) {
            c.classList.remove('touch-active');
        });
        if (!isActive) {
            card.classList.add('touch-active');
            e.preventDefault();
        }
    }

    document.addEventListener('touchstart', handleTouch, { passive: false });
})();

// =========== HTMX RE-INIT ===========
document.body.addEventListener('htmx:afterSwap', function() {
    if (typeof ScrollTrigger !== 'undefined') {
        ScrollTrigger.refresh();
    }
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.querySelectorAll('.modal-backdrop, .offcanvas-backdrop').forEach(function(el) { el.remove(); });
    document.querySelectorAll('.offcanvas.show').forEach(function(el) {
        var inst = bootstrap.Offcanvas.getInstance(el);
        if (inst) inst.hide();
    });
});

// =========== SHOP SEARCH FILTER ===========
function filterProducts(val) {
    var count = 0;
    document.querySelectorAll('.product-item').forEach(function(el) {
        var name = (el.getAttribute('data-name') || '').toLowerCase();
        var match = name.includes(val);
        el.style.display = match ? 'block' : 'none';
        if (match) count++;
    });
    var c = document.getElementById('itemCount');
    if (c) c.textContent = count + ' items';
}

function resetAllFilters() { window.location.href = '/shop'; }

function loadMoreProducts(cls, count, btn) {
    var items = document.querySelectorAll('.' + cls);
    var vis = document.querySelectorAll('.' + cls + '.show').length;
    if (btn) {
        var t = btn.querySelector('.btn-text');
        var s = btn.querySelector('.spinner-border');
        if (t) t.classList.add('d-none');
        if (s) s.classList.remove('d-none');
    }
    setTimeout(function() {
        for (var i = vis; i < vis + count; i++) {
            if (items[i]) {
                items[i].classList.remove('d-none');
                (function(idx) {
                    setTimeout(function() { items[idx].classList.add('show'); }, 100);
                })(i);
            }
        }
        if (btn) {
            var t = btn.querySelector('.btn-text');
            var s = btn.querySelector('.spinner-border');
            if (t) t.classList.remove('d-none');
            if (s) s.classList.add('d-none');
        }
        if (vis + count >= items.length && btn) btn.style.display = 'none';
    }, 300);
}

// Global Failsafe: ensures all elements are visible after 2s under all conditions
setTimeout(() => {
    document.querySelectorAll('[data-reveal], .luxury-cat-card, .luxury-product-card--minimal, .why-card-luxury, .testimonial-card-luxury, .insta-magazine-item, .faq-item-luxury, .timeline-item, .philosophy-card, .gallery-item, .stat-card-luxury').forEach(el => {
        // Use parseFloat so GSAP mid-tween values like 0.000001 are caught
        const computedOpacity = parseFloat(window.getComputedStyle(el).opacity);
        if (computedOpacity < 0.1 || el.style.opacity === '0') {
            if (typeof gsap !== 'undefined') {
                gsap.killTweensOf(el);
            }
            el.style.opacity = '1';
            el.style.transform = 'none';
            el.style.visibility = 'visible';
        }
    });
}, 2000);

// =========== WISHLIST AJAX TOGGLE & BADGES ===========
window.updateWishlistBadges = function() {
    const badges = document.querySelectorAll('.wishlist-count-badge');
    if (badges.length === 0) return;
    const count = parseInt(localStorage.getItem('wishlist_count') || '0', 10);
    badges.forEach(b => {
        b.textContent = count;
        b.style.display = count > 0 ? 'inline-block' : 'none';
    });
};

window.toggleWishlist = function(productId, btn) {
    // Use getCsrfToken helper (supports both form input and cookie)
    const csrf_token = window.getCsrfToken ? window.getCsrfToken() : (document.querySelector("[name='csrfmiddlewaretoken']")?.value || '');
    
    const icon = btn.querySelector('i');
    const isActive = icon.classList.contains('fa-solid') || icon.classList.contains('active');
    
    if (isActive) {
        icon.className = 'fa-regular fa-heart';
        btn.classList.remove('active');
    } else {
        icon.className = 'fa-solid fa-heart active';
        btn.classList.add('active');
    }
    
    fetch('/wish-list', {
        method: 'POST',
        body: JSON.stringify({ product_id: productId }),
        headers: {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (window.showToast) {
            window.showToast(data.message || "Wishlist updated!");
        }
        
        let count = parseInt(localStorage.getItem('wishlist_count') || '0', 10);
        if (data.added) {
            count++;
            icon.className = 'fa-solid fa-heart active';
            btn.classList.add('active');
        } else {
            count = Math.max(0, count - 1);
            icon.className = 'fa-regular fa-heart';
            btn.classList.remove('active');
        }
        localStorage.setItem('wishlist_count', count);
        window.updateWishlistBadges();
    })
    .catch(err => {
        console.error(err);
        if (isActive) {
            icon.className = 'fa-solid fa-heart active';
            btn.classList.add('active');
        } else {
            icon.className = 'fa-regular fa-heart';
            btn.classList.remove('active');
        }
    });
};
