/* The Open Browser Company — interactions & animation controllers */

(() => {
  "use strict";

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Loader ---------- */
  const loader = document.getElementById("loader");
  const hideLoader = () => loader && loader.classList.add("is-done");
  if (prefersReduced) {
    hideLoader();
  } else {
    window.addEventListener("load", () => setTimeout(hideLoader, 900));
    // Safety: never trap the page behind the loader
    setTimeout(hideLoader, 3500);
  }

  /* ---------- Split headline into animated chars ---------- */
  document.querySelectorAll("[data-split]").forEach((el) => {
    const text = el.textContent;
    el.textContent = "";
    let idx = 0;
    for (const ch of text) {
      const span = document.createElement("span");
      span.className = "char";
      span.style.setProperty("--i", idx++);
      span.textContent = ch === " " ? "\u00A0" : ch;
      el.appendChild(span);
    }
  });

  /* ---------- Scroll progress + sticky nav ---------- */
  const bar = document.getElementById("progressBar");
  const nav = document.getElementById("nav");
  const onScroll = () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const p = max > 0 ? (window.scrollY / max) * 100 : 0;
    if (bar) bar.style.width = p.toFixed(2) + "%";
    nav && nav.classList.toggle("is-stuck", window.scrollY > 24);
    parallax();
  };
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---------- Reveal on scroll ---------- */
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !prefersReduced) {
    // Stagger siblings that share a parent
    const groups = new Map();
    revealEls.forEach((el) => {
      const key = el.parentElement;
      if (!groups.has(key)) groups.set(key, 0);
      const i = groups.get(key);
      el.style.setProperty("--d", i * 90 + "ms");
      groups.set(key, i + 1);
    });
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("is-in");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -8% 0px" }
    );
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("is-in"));
  }

  /* ---------- Hero logo: mouse-reactive 3D tilt ---------- */
  const heroMark = document.getElementById("heroMark");
  const heroIcon = document.getElementById("heroIcon");
  if (heroMark && heroIcon && !prefersReduced) {
    let raf = null;
    let targetX = 0, targetY = 0, curX = 0, curY = 0;

    const loop = () => {
      curX += (targetX - curX) * 0.08;
      curY += (targetY - curY) * 0.08;
      heroIcon.style.transform =
        `rotateY(${curX}deg) rotateX(${curY}deg)`;
      if (Math.abs(targetX - curX) > 0.05 || Math.abs(targetY - curY) > 0.05) {
        raf = requestAnimationFrame(loop);
      } else {
        raf = null;
      }
    };

    heroMark.addEventListener("mousemove", (e) => {
      const r = heroMark.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5;
      const py = (e.clientY - r.top) / r.height - 0.5;
      targetX = px * 28;
      targetY = -py * 22;
      if (!raf) raf = requestAnimationFrame(loop);
    });
    heroMark.addEventListener("mouseleave", () => {
      targetX = 0; targetY = 0;
      if (!raf) raf = requestAnimationFrame(loop);
    });
  }

  /* ---------- Card spotlight follows cursor ---------- */
  document.querySelectorAll(".card").forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const r = card.getBoundingClientRect();
      card.style.setProperty("--mx", ((e.clientX - r.left) / r.width) * 100 + "%");
      card.style.setProperty("--my", ((e.clientY - r.top) / r.height) * 100 + "%");
    });
  });

  /* ---------- Parallax banner ---------- */
  const parallaxImg = document.getElementById("parallaxImg");
  function parallax() {
    if (!parallaxImg || prefersReduced) return;
    const r = parallaxImg.parentElement.getBoundingClientRect();
    if (r.bottom < 0 || r.top > window.innerHeight) return;
    const progress = (window.innerHeight - r.top) / (window.innerHeight + r.height);
    const shift = (progress - 0.5) * 40; // px
    parallaxImg.style.transform = `translateY(${-shift}px)`;
  }

  /* ---------- Logo animation playground ---------- */
  const markBtn = document.getElementById("markBtn");
  const stageIcon = document.getElementById("stageIcon");
  const markLabel = document.getElementById("markLabel");
  const markDots = document.getElementById("markDots");
  const MODES = ["Chrome sheen", "Full rotation", "Heartbeat pulse", "3D tilt"];
  let mode = 0;

  const applyMode = (m) => {
    if (!stageIcon) return;
    mode = ((m % MODES.length) + MODES.length) % MODES.length;
    stageIcon.className = "mark__icon mode-" + mode;
    if (markLabel) {
      markLabel.style.opacity = 0;
      setTimeout(() => {
        markLabel.textContent = MODES[mode];
        markLabel.style.opacity = 1;
      }, 160);
      markLabel.style.transition = "opacity .16s ease";
    }
    if (markDots) {
      [...markDots.children].forEach((d, i) => d.classList.toggle("is-on", i === mode));
    }
  };

  if (markBtn) {
    applyMode(0);
    markBtn.addEventListener("click", () => applyMode(mode + 1));
    // Auto-cycle until the user interacts
    if (!prefersReduced) {
      let auto = setInterval(() => applyMode(mode + 1), 4000);
      markBtn.addEventListener("click", () => { clearInterval(auto); auto = null; }, { once: true });
    }
  }

  /* ---------- Mobile nav ---------- */
  const toggle = document.getElementById("navToggle");
  const links = document.querySelector(".nav__links");
  if (toggle && links) {
    toggle.addEventListener("click", () => {
      const open = links.classList.toggle("is-open");
      toggle.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    });
    links.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => {
        links.classList.remove("is-open");
        toggle.classList.remove("is-open");
      })
    );
  }

  /* ---------- Ambient particles ---------- */
  const canvas = document.getElementById("particles");
  if (canvas && !prefersReduced) {
    const ctx = canvas.getContext("2d");
    let w, h, dots = [];

    const resize = () => {
      w = canvas.width = window.innerWidth * devicePixelRatio;
      h = canvas.height = window.innerHeight * devicePixelRatio;
      canvas.style.width = window.innerWidth + "px";
      canvas.style.height = window.innerHeight + "px";
      const count = Math.min(90, Math.floor((window.innerWidth * window.innerHeight) / 22000));
      dots = Array.from({ length: count }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.22 * devicePixelRatio,
        vy: (Math.random() - 0.5) * 0.22 * devicePixelRatio,
        r: (Math.random() * 1.4 + 0.4) * devicePixelRatio,
        a: Math.random() * 0.5 + 0.15,
        tw: Math.random() * Math.PI * 2,
      }));
    };

    const tick = () => {
      ctx.clearRect(0, 0, w, h);
      for (const d of dots) {
        d.x += d.vx; d.y += d.vy; d.tw += 0.02;
        if (d.x < 0) d.x = w; if (d.x > w) d.x = 0;
        if (d.y < 0) d.y = h; if (d.y > h) d.y = 0;
        const alpha = d.a * (0.7 + 0.3 * Math.sin(d.tw));
        ctx.beginPath();
        ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${alpha.toFixed(3)})`;
        ctx.fill();
      }
      requestAnimationFrame(tick);
    };

    resize();
    window.addEventListener("resize", resize);
    requestAnimationFrame(tick);
  }

  onScroll();
})();
