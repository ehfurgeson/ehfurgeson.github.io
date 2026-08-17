(() => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Menu ---------- */
  const nav = document.querySelector("[data-nav]");
  const menuBtn = document.querySelector("[data-menu-toggle]");
  const overlay = document.querySelector("[data-overlay]");
  const menuLinks = document.querySelectorAll(".menu-link");

  function setMenu(open) {
    if (!nav || !menuBtn) return;
    nav.classList.toggle("is-open", open);
    menuBtn.classList.toggle("is-open", open);
    menuBtn.setAttribute("aria-expanded", String(open));
    nav.setAttribute("aria-hidden", open ? "false" : "true");
    document.body.style.overflow = open ? "hidden" : "";
  }

  menuBtn?.addEventListener("click", () => setMenu(!nav.classList.contains("is-open")));
  overlay?.addEventListener("click", () => setMenu(false));
  menuLinks.forEach((link) => link.addEventListener("click", () => setMenu(false)));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") setMenu(false);
  });

  /* ---------- Experience panes ---------- */
  const panes = document.querySelector(".panes");
  const paneItems = panes ? [...panes.querySelectorAll(":scope > li")] : [];

  function setActivePane(index) {
    if (!panes || !paneItems.length) return;
    const cols = paneItems.map((_, i) => (i === index ? "10fr" : "1fr")).join(" ");
    panes.style.gridTemplateColumns = cols;
    paneItems.forEach((item, i) => {
      item.dataset.active = i === index ? "true" : "false";
    });
  }

  if (paneItems.length) {
    setActivePane(0);
    paneItems.forEach((item, i) => {
      item.addEventListener("mouseenter", () => {
        if (window.matchMedia("(hover: hover) and (min-width: 601px)").matches) {
          setActivePane(i);
        }
      });
      item.addEventListener("click", () => setActivePane(i));
      item.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          setActivePane(i);
        }
      });
    });
  }

  /* ---------- Scroll reveal ---------- */
  const reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("is-visible"));
  }

  /* ---------- Hero name animations (4 variants) ---------- */
  const canvas = document.getElementById("name-canvas");
  const fallback = document.querySelector(".hero-fallback");
  if (!canvas) return;

  const ctx = canvas.getContext("2d", { alpha: true });
  const name = "Eli Furgeson";

  const params = new URLSearchParams(window.location.search);

  let width = 0;
  let height = 0;
  let dpr = 1;
  let fontSize = 64;
  let nameMetrics = { x: 0, y: 0, w: 0, h: 0 };
  let targets = [];
  let edgeTargets = [];
  let maskCanvas = null;
  let maskCtx = null;
  let maskAlpha = null;
  let maskW = 0;
  let maskH = 0;
  let particles = [];
  let streams = [];
  let rivulets = [];
  let mistDrops = [];
  let ambient = [];
  let shimmerCanvas = null;
  let shimmerCtx = null;
  let startTime = performance.now();
  let raf = 0;
  let settled = false;

  function fontSpec(size) {
    return `700 ${size}px Syne, Arial Black, sans-serif`;
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    fontSize = Math.min(width * 0.14, height * 0.22, 128);
    nameMetrics = {
      x: width / 2,
      y: height / 2 - fontSize * 0.05,
      w: width * 0.78,
      h: fontSize,
    };
    buildMaskAndTargets();
  }

  function buildMaskAndTargets() {
    maskCanvas = document.createElement("canvas");
    maskCanvas.width = Math.max(1, Math.floor(width));
    maskCanvas.height = Math.max(1, Math.floor(height));
    maskCtx = maskCanvas.getContext("2d");
    maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
    maskCtx.fillStyle = "#000";
    maskCtx.textAlign = "center";
    maskCtx.textBaseline = "middle";
    maskCtx.font = fontSpec(fontSize);
    maskCtx.fillText(name, nameMetrics.x, nameMetrics.y);

    const data = maskCtx.getImageData(0, 0, maskCanvas.width, maskCanvas.height).data;
    const pts = [];
    const edges = [];
    const step = Math.max(1, Math.floor(fontSize / 55));
    const w = maskCanvas.width;
    const h = maskCanvas.height;
    maskW = w;
    maskH = h;
    maskAlpha = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        maskAlpha[y * w + x] = data[(y * w + x) * 4 + 3];
      }
    }

    shimmerCanvas = document.createElement("canvas");
    shimmerCanvas.width = Math.max(1, Math.floor(width * dpr));
    shimmerCanvas.height = Math.max(1, Math.floor(height * dpr));
    shimmerCtx = shimmerCanvas.getContext("2d");

    for (let y = 0; y < h; y += step) {
      for (let x = 0; x < w; x += step) {
        const a = maskAlpha[y * w + x];
        if (a > 140) {
          pts.push({
            x,
            y,
            ox: (Math.random() - 0.5) * 1.5,
            oy: (Math.random() - 0.5) * 1.5,
          });
          const neighbors = [
            y >= step ? maskAlpha[(y - step) * w + x] : 0,
            y + step < h ? maskAlpha[(y + step) * w + x] : 0,
            x >= step ? maskAlpha[y * w + (x - step)] : 0,
            x + step < w ? maskAlpha[y * w + (x + step)] : 0,
          ];
          if (neighbors.some((n) => n < 140)) {
            edges.push({ x, y, ox: 0, oy: 0 });
          }
        }
      }
    }
    targets = pts;
    edgeTargets = edges.length ? edges : pts;
  }

  function isInsideName(x, y) {
    if (!maskAlpha) return false;
    const ix = Math.max(0, Math.min(maskW - 1, x | 0));
    const iy = Math.max(0, Math.min(maskH - 1, y | 0));
    return maskAlpha[iy * maskW + ix] > 40;
  }

  function currentSeason(date = new Date()) {
    const m = date.getMonth(); // 0–11
    if (m >= 2 && m <= 4) return "spring";
    if (m >= 5 && m <= 7) return "summer";
    if (m >= 8 && m <= 10) return "fall";
    return "winter";
  }

  const SEASON_PALETTES = {
    winter: {
      fills: ["#111111", "#1a1a1a", "#222222", "#2a2a2a"],
      vein: "rgba(255,255,255,0.35)",
      scaffold: "#111111",
      label: "Winter",
    },
    spring: {
      greens: ["#2f6b3a", "#3d8a45", "#4a9a52", "#25633a", "#5aad62", "#6bb86f"],
      pinks: ["#e8a4b8", "#f0b7c6", "#d989a4"],
      vein: "rgba(255,255,255,0.28)",
      scaffold: "#2a5a32",
      label: "Spring",
    },
    summer: {
      fills: ["#1e4d2b", "#2a6236", "#347a40", "#3f8f4c", "#256b34", "#1a3f24"],
      vein: "rgba(255,255,255,0.25)",
      scaffold: "#1e4d2b",
      label: "Summer",
    },
    fall: {
      fills: ["#c45c26", "#d4782e", "#b33a1a", "#a84820", "#e0953a", "#8b3a1a", "#c96b2f"],
      vein: "rgba(255,255,255,0.3)",
      scaffold: "#8b3a1a",
      label: "Fall",
    },
  };

  const seasonParam = params.get("season");
  const season =
    seasonParam && SEASON_PALETTES[seasonParam] ? seasonParam : currentSeason();
  const seasonPalette = SEASON_PALETTES[season];

  function pickSeasonColor() {
    if (season === "spring") {
      // ~12% pink blossom flecks
      if (Math.random() < 0.12) {
        const pinks = seasonPalette.pinks;
        return pinks[(Math.random() * pinks.length) | 0];
      }
      const greens = seasonPalette.greens;
      return greens[(Math.random() * greens.length) | 0];
    }
    const fills = seasonPalette.fills;
    return fills[(Math.random() * fills.length) | 0];
  }

  function leafShape(seed) {
    return seed % 3;
  }

  function drawLeaf(p) {
    const { x, y, rot, size, shape, alpha } = p;
    const fill = p.color || "#111";
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rot);
    ctx.globalAlpha = alpha;
    ctx.fillStyle = fill;
    if (shape === 0) {
      ctx.beginPath();
      ctx.moveTo(0, -size);
      ctx.quadraticCurveTo(size * 0.9, -size * 0.2, 0, size);
      ctx.quadraticCurveTo(-size * 0.9, -size * 0.2, 0, -size);
      ctx.fill();
      ctx.globalAlpha = alpha * 0.35;
      ctx.beginPath();
      ctx.moveTo(0, -size * 0.7);
      ctx.lineTo(0, size * 0.7);
      ctx.strokeStyle = seasonPalette.vein;
      ctx.lineWidth = 0.6;
      ctx.stroke();
    } else if (shape === 1) {
      ctx.beginPath();
      ctx.moveTo(0, -size * 1.1);
      ctx.quadraticCurveTo(size * 0.75, -size * 0.1, 0, size);
      ctx.quadraticCurveTo(-size * 0.75, -size * 0.1, 0, -size * 1.1);
      ctx.fill();
    } else {
      ctx.beginPath();
      ctx.ellipse(0, 0, size * 0.55, size, 0, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  function drawNameSolid(alpha = 1, fill = "#111") {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = fill;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = fontSpec(fontSize);
    ctx.fillText(name, nameMetrics.x, nameMetrics.y);
    ctx.restore();
  }

  function resetScene(restartClock = true) {
    cancelAnimationFrame(raf);
    particles = [];
    streams = [];
    rivulets = [];
    mistDrops = [];
    ambient = [];
    settled = false;
    if (restartClock) startTime = performance.now();
    canvas.style.opacity = "1";
    fallback?.classList.remove("is-visible");

    initLeavesSettle();

    if (!reduceMotion) raf = requestAnimationFrame(tick);
    else drawStatic();
  }

  /* ===== Variant 1: Leaves settle into name (natural landing) ===== */
  function initLeavesSettle() {
    // Prefer one leaf per sampled glyph point so the full letter fills in
    const pool = targets.length ? [...targets] : [];
    for (let i = pool.length - 1; i > 0; i--) {
      const j = (Math.random() * (i + 1)) | 0;
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    const count = Math.min(Math.max(pool.length * 2, 500), 3200);
    for (let i = 0; i < count; i++) {
      const t = pool[i % pool.length];
      // Spawn mostly above the letter point so landing feels like a natural fall
      const scatterX = (Math.random() - 0.5) * fontSize * 0.45;
      const startY = -20 - Math.random() * height * 0.55;
      const fallDist = Math.max(40, t.y - startY);
      // Slight jitter so stacked leaves on the same glyph point still fill volume
      const ox = (Math.random() - 0.5) * 2.2;
      const oy = (Math.random() - 0.5) * 2.2;
      particles.push({
        x: t.x + scatterX,
        y: startY,
        vx: (Math.random() - 0.5) * 0.45,
        vy: 0.7 + Math.random() * 0.5 + fallDist * 0.009,
        rot: Math.random() * Math.PI * 2,
        rotSpeed: (Math.random() - 0.5) * 0.035,
        size: 1.7 + Math.random() * 2.4,
        shape: leafShape(i),
        target: { x: t.x, y: t.y, ox, oy },
        delay: Math.random() * 0.25,
        sway: 1.0 + Math.random() * 1.8,
        swayAmp: 0.3 + Math.random() * 0.45,
        swayPhase: Math.random() * Math.PI * 2,
        alpha: 0.62 + Math.random() * 0.35,
        color: pickSeasonColor(),
        settled: false,
        landEase: 0,
      });
    }
  }

  function updateLeavesSettle(t) {
    const mist = ctx.createLinearGradient(0, 0, 0, height);
    mist.addColorStop(0, 'rgba(255,255,255,0)');
    mist.addColorStop(0.45, 'rgba(255,255,255,0.08)');
    mist.addColorStop(1, 'rgba(241,241,241,0)');
    ctx.fillStyle = mist;
    ctx.fillRect(0, 0, width, height);

    if (t > 1.3) drawNameSolid(Math.min(0.1, (t - 1.3) * 0.04), seasonPalette.scaffold);

    let allSettled = true;
    for (const leaf of particles) {
      const local = t - leaf.delay;
      if (local < 0) {
        allSettled = false;
        continue;
      }

      const tx = leaf.target.x + leaf.target.ox;
      const ty = leaf.target.y + leaf.target.oy;

      if (!leaf.settled) {
        allSettled = false;

        const dx = tx - leaf.x;
        const dy = ty - leaf.y;
        const dist = Math.hypot(dx, dy);
        // Scale slowdown to distance-to-target (letter-sized), NOT the viewport —
        // otherwise leaves heading for the bottom of a glyph brake at the top
        const arriveScale = Math.max(28, fontSize * 0.85);
        const near = Math.max(0, Math.min(1, 1 - dist / arriveScale));

        const slowRadius = Math.max(22, fontSize * 0.35);
        const maxSpeed = 4;
        const desiredSpeed =
          dist < slowRadius ? maxSpeed * Math.pow(dist / slowRadius, 0.85) : maxSpeed;
        const inv = dist > 0.001 ? 1 / dist : 0;
        const desiredVx = dx * inv * desiredSpeed;
        const desiredVy = dy * inv * desiredSpeed;

        const blend = 0.05 + near * 0.055;
        leaf.vx += (desiredVx - leaf.vx) * blend;
        leaf.vy += (desiredVy - leaf.vy) * blend;

        // Keep a bit of gravity until close to the actual landing spot
        if (dist > slowRadius) {
          leaf.vy += 0.055;
        }

        const drag = 0.978 - near * 0.05;
        leaf.vx *= drag;
        leaf.vy *= drag;

        if (near > 0.7) {
          const cap = 0.95 * (1 - (near - 0.7) * 0.55);
          const spd = Math.hypot(leaf.vx, leaf.vy);
          if (spd > cap && spd > 0) {
            leaf.vx = (leaf.vx / spd) * cap;
            leaf.vy = (leaf.vy / spd) * cap;
          }
        }

        const swayFade = Math.max(0, 1 - near * 1.1);
        leaf.x += leaf.vx + Math.sin(local * leaf.sway + leaf.swayPhase) * leaf.swayAmp * swayFade;
        leaf.y += leaf.vy;
        leaf.rot += leaf.rotSpeed * swayFade;
        leaf.rot *= 0.985 - near * 0.02;

        if (leaf.y > ty + 1.2) {
          leaf.y = ty + 1.2;
          leaf.vy *= 0.3;
        }

        const speed = Math.hypot(leaf.vx, leaf.vy);
        if (dist < 3.2 && speed < 0.45) {
          leaf.landEase = Math.min(1, leaf.landEase + 0.035);
          leaf.x += (tx - leaf.x) * 0.055 * leaf.landEase;
          leaf.y += (ty - leaf.y) * 0.055 * leaf.landEase;
          leaf.vx *= 0.82;
          leaf.vy *= 0.82;
          leaf.rot *= 0.9;
          if (leaf.landEase > 0.88 && dist < 0.85 && speed < 0.22) {
            leaf.settled = true;
            leaf.x = tx;
            leaf.y = ty;
            leaf.vx = 0;
            leaf.vy = 0;
          }
        }

        drawLeaf(leaf);
      } else {
        const breathe = Math.sin(t * 0.9 + leaf.swayPhase) * 0.35;
        const drift = Math.sin(t * 0.55 + leaf.swayPhase * 1.3) * 0.25;
        drawLeaf({
          ...leaf,
          x: tx + drift,
          y: ty + breathe,
          rot: Math.sin(t * 0.7 + leaf.swayPhase) * 0.12,
        });
      }
    }
    settled = allSettled;
    if (settled) spawnAmbientLeaves(t, 0.045);
  }

  function spawnAmbientLeaves(t, rate, gusty = false) {
    if (Math.random() < rate) {
      ambient.push({
        x: gusty ? (Math.random() > 0.5 ? -10 : width + 10) : Math.random() * width,
        y: gusty ? Math.random() * height * 0.4 : -10,
        vx: gusty ? (Math.random() > 0.5 ? 1.2 : -1.2) : 0,
        vy: 0.55 + Math.random() * 1.1,
        rot: Math.random() * Math.PI,
        rotSpeed: (Math.random() - 0.5) * 0.04,
        size: 2 + Math.random() * 2.8,
        shape: leafShape(Math.floor(Math.random() * 9)),
        sway: 1 + Math.random() * 2,
        phase: Math.random() * Math.PI * 2,
        life: 1,
        alpha: 0.45,
        color: pickSeasonColor(),
      });
    }
    for (let i = ambient.length - 1; i >= 0; i--) {
      const a = ambient[i];
      a.y += a.vy;
      a.x += (a.vx || 0) * 0.6 + Math.sin(t * a.sway + a.phase) * 0.45;
      a.rot += a.rotSpeed;
      a.life -= 0.004;
      if (a.life <= 0 || a.y > height + 30 || a.x < -40 || a.x > width + 40) ambient.splice(i, 1);
      else drawLeaf({ ...a, alpha: a.life * a.alpha });
    }
  }

  function drawStatic() {
    ctx.clearRect(0, 0, width, height);
    drawNameSolid(1);
    fallback?.classList.add("is-visible");
    canvas.style.opacity = "0.35";
  }

  function tick(now) {
    const t = (now - startTime) / 1000;
    ctx.clearRect(0, 0, width, height);
    updateLeavesSettle(t);
    raf = requestAnimationFrame(tick);
  }




  window.addEventListener("resize", () => {
    resize();
    resetScene(true);
  });

  const start = () => {
    resize();
    resetScene(true);
    setTimeout(() => {
      if (targets.length < 40) {
        fallback?.classList.add("is-visible");
        canvas.style.opacity = "0.25";
      }
    }, 800);
  };

  if (document.fonts?.ready) document.fonts.ready.then(start).catch(start);
  else start();
})();
