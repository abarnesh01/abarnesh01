import React, { useEffect } from 'react';

const CustomCursor = () => {
    useEffect(() => {
        // Prevent duplicate cursors
        if (document.querySelector(".cursor-glow")) return;

        const cursor = document.createElement("div");
        cursor.className = "cursor-glow";
        document.body.appendChild(cursor);

        const cursorInner = document.createElement("div");
        cursorInner.className = "cursor-inner";
        cursor.appendChild(cursorInner);

        let mouseX = 0;
        let mouseY = 0;
        let cursorX = 0;
        let cursorY = 0;

        const handleMouseMove = (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        };

        const handleMouseDown = () => cursor.classList.add("clicked");
        const handleMouseUp = () => cursor.classList.remove("clicked");

        const handleMouseOver = (e) => {
            const target = e.target;
            const isClickable = target.tagName === 'A' ||
                target.tagName === 'BUTTON' ||
                target.closest('a') ||
                target.closest('button') ||
                target.closest('.hover-trigger');

            if (isClickable) {
                cursor.classList.add("hovering");
            } else {
                cursor.classList.remove("hovering");
            }
        };

        const animate = () => {
            // Smooth trailing effect using lerp
            const lerpFactor = 0.15;
            cursorX += (mouseX - cursorX) * lerpFactor;
            cursorY += (mouseY - cursorY) * lerpFactor;

            cursor.style.transform = `translate3d(${cursorX}px, ${cursorY}px, 0)`;

            requestAnimationFrame(animate);
        };

        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mousedown', handleMouseDown);
        window.addEventListener('mouseup', handleMouseUp);
        window.addEventListener('mouseover', handleMouseOver);

        const animationId = requestAnimationFrame(animate);

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mousedown', handleMouseDown);
            window.removeEventListener('mouseup', handleMouseUp);
            window.removeEventListener('mouseover', handleMouseOver);
            cancelAnimationFrame(animationId);
            if (cursor && cursor.parentNode) {
                cursor.parentNode.removeChild(cursor);
            }
        };
    }, []);

    return null; // This component handles its own DOM insertion
};

export default CustomCursor;
