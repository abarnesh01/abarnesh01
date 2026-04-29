// Initialize Lucide icons
lucide.createIcons();

// Custom cursor glow effect
const glow = document.querySelector('.cursor-glow');

document.addEventListener('mousemove', (e) => {
    const { clientX, clientY } = e;
    glow.style.left = `${clientX}px`;
    glow.style.top = `${clientY}px`;
});

// Smooth reveal on scroll
const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('reveal');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.glass-card').forEach(card => {
    observer.observe(card);
});

// Navbar scroll effect
const nav = document.querySelector('nav');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        nav.style.padding = '0.5rem 0';
        nav.style.background = 'rgba(9, 9, 11, 0.95)';
    } else {
        nav.style.padding = '0';
        nav.style.background = 'rgba(9, 9, 11, 0.8)';
    }
});

// Magnetic effect for social icons (optional premium touch)
const socialItems = document.querySelectorAll('.social-item');
socialItems.forEach(item => {
    item.addEventListener('mousemove', (e) => {
        const { left, top, width, height } = item.getBoundingClientRect();
        const centerX = left + width / 2;
        const centerY = top + height / 2;
        const moveX = (e.clientX - centerX) * 0.3;
        const moveY = (e.clientY - centerY) * 0.3;
        
        item.style.transform = `translate(${moveX}px, ${moveY}px)`;
    });

    item.addEventListener('mouseleave', () => {
        item.style.transform = '';
    });
});
