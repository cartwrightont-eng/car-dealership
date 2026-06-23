// ── NAV ───────────────────────────────────────────────────────────────────────
function toggleNav() {
  const mobile = document.getElementById('navMobile');
  if (mobile) mobile.classList.toggle('open');
}

// ── AUTO-DISMISS FLASH ────────────────────────────────────────────────────────
document.querySelectorAll('.flash').forEach(flash => {
  setTimeout(() => {
    flash.style.opacity = '0';
    flash.style.transition = 'opacity 0.4s';
    setTimeout(() => flash.remove(), 400);
  }, 4000);
});

// ── SCROLL ANIMATIONS ─────────────────────────────────────────────────────────
const observer = new IntersectionObserver(
  entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); }),
  { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
);

document.querySelectorAll('.car-card, .why-feature, .fin-card, .testimonial-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});

document.addEventListener('DOMContentLoaded', () => {
  // Trigger visible for already-in-view items
  document.querySelectorAll('.car-card, .why-feature, .fin-card, .testimonial-card').forEach(el => {
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight) el.classList.add('visible');
  });
});

document.addEventListener('animationend', () => {}, false);

// Inject visible style
const style = document.createElement('style');
style.textContent = '.visible { opacity: 1 !important; transform: translateY(0) !important; }';
document.head.appendChild(style);

// ── PRICE FORMATTER ───────────────────────────────────────────────────────────
// Format any element with data-kes attribute
document.querySelectorAll('[data-kes]').forEach(el => {
  const val = parseInt(el.dataset.kes);
  if (!isNaN(val)) el.textContent = 'KES ' + val.toLocaleString();
});

// ── LAZY LOAD IMAGES ──────────────────────────────────────────────────────────
if ('loading' in HTMLImageElement.prototype) {
  // Native support — nothing needed
} else {
  // Polyfill for older browsers
  const lazyImgs = document.querySelectorAll('img[loading="lazy"]');
  const imgObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.src = e.target.dataset.src || e.target.src;
        imgObserver.unobserve(e.target);
      }
    });
  });
  lazyImgs.forEach(img => imgObserver.observe(img));
}

// ── FILTER FORM SUBMIT ON CHANGE ──────────────────────────────────────────────
const filterForm = document.getElementById('filterForm');
if (filterForm) {
  filterForm.querySelectorAll('select').forEach(sel => {
    // Don't auto-submit — user hits button. But mark changed ones.
    sel.addEventListener('change', () => sel.classList.add('changed'));
  });
}

// ── STICKY NAV SHADOW ON SCROLL ───────────────────────────────────────────────
const nav = document.querySelector('.nav');
if (nav) {
  window.addEventListener('scroll', () => {
    nav.style.boxShadow = window.scrollY > 20
      ? '0 4px 24px rgba(0,0,0,0.4)'
      : 'none';
  }, { passive: true });
}

// ── WHATSAPP DEEP LINK HELPER ─────────────────────────────────────────────────
// Normalise Kenyan phone numbers to international format for WA links
function normaliseKEPhone(phone) {
  phone = phone.replace(/\s+/g, '');
  if (phone.startsWith('0')) return '254' + phone.slice(1);
  if (phone.startsWith('+')) return phone.slice(1);
  return phone;
}
