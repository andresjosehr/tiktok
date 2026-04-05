// ─── CONFIG ───
const ROUND_SECONDS = 180;
const WIN_DIFF = 30;
const AUTO_RESTART_DELAY = 2500;
const GLORY_ROUNDS = 5;
const GLORY_DELAY = 6000;

const CATEGORIES = [
    { label: 'Genero', title: 'HOMBRES vs MUJERES', left: '👨', right: '👩', leftName: 'HOMBRES', rightName: 'MUJERES', leftColor: '#4a9aff', rightColor: '#ff4a9a' },
    { label: 'Deporte', title: 'MESSI vs CR7', left: '🇦🇷', right: '🇵🇹', leftName: 'MESSI', rightName: 'CR7', leftColor: '#75aaff', rightColor: '#ff7575' },
    { label: 'Generacion', title: 'GEN Z vs MILLENNIALS', left: '📱', right: '💻', leftName: 'GEN Z', rightName: 'MILLENNIALS', leftColor: '#a855f7', rightColor: '#f59e0b' },
    { label: 'Mascota', title: 'PERRO vs GATO', left: '🐕', right: '🐈', leftName: 'PERRO', rightName: 'GATO', leftColor: '#f59e0b', rightColor: '#a855f7' },
    { label: 'Paises', title: 'MEXICO vs COLOMBIA', left: '🇲🇽', right: '🇨🇴', leftName: 'MEXICO', rightName: 'COLOMBIA', leftColor: '#00a86b', rightColor: '#fcd116' },
    { label: 'Estacion', title: 'VERANO vs INVIERNO', left: '☀️', right: '❄️', leftName: 'VERANO', rightName: 'INVIERNO', leftColor: '#f59e0b', rightColor: '#60a5fa' },
    { label: 'Opinion', title: 'PIZZA vs HAMBURGUESA', left: '🍕', right: '🍔', leftName: 'PIZZA', rightName: 'HAMBURGUESA', leftColor: '#ef4444', rightColor: '#f59e0b' },
    { label: 'Personalidad', title: 'INTROVERTIDOS vs EXTROVERTIDOS', left: '📖', right: '🎉', leftName: 'INTROVERTIDOS', rightName: 'EXTROVERTIDOS', leftColor: '#6366f1', rightColor: '#ec4899' },
];

// ─── STATE ───
let leftPoints = 0;
let rightPoints = 0;
let gameOver = false;
let timeLeft = ROUND_SECONDS;
let timerInterval = null;
let roundNumber = 1;
let currentCategory = 0;
let globalWins = { left: 0, right: 0 };
let seriesWins = { left: 0, right: 0 };
let gloryActive = false;
let streaks = {
    men:   { count: 0, lastTime: 0, decayTimer: null },
    women: { count: 0, lastTime: 0, decayTimer: null },
};

// ─── ELEMENTS ───
const arena = document.getElementById('arena');
const wall = document.getElementById('wall');
const charLeft = document.getElementById('charMen');
const charRight = document.getElementById('charWomen');
const leftGlow = document.getElementById('menGlow');
const rightGlow = document.getElementById('womenGlow');
const leftBar = document.getElementById('menBar');
const rightBar = document.getElementById('womenBar');
const leftPct = document.getElementById('menPct');
const rightPct = document.getElementById('womenPct');
const leftScoreEl = document.getElementById('menScore');
const rightScoreEl = document.getElementById('womenScore');
const timerEl = document.getElementById('timer');
const winOverlay = document.getElementById('winOverlay');
const winnerText = document.getElementById('winnerText');
const winnerEmoji = document.getElementById('winnerEmoji');
const winnerCrown = document.getElementById('winnerCrown');
const winnerSubtitle = document.getElementById('winnerSubtitle');
const gameContainer = document.getElementById('gameContainer');
const bgGradient = document.getElementById('bgGradient');
const edgeLeft = document.getElementById('edgeLeft');
const edgeRight = document.getElementById('edgeRight');
const roundCounterEl = document.getElementById('roundCounter');
const categoryLabel = document.getElementById('categoryLabel');
const roundTitle = document.getElementById('roundTitle');
const countdownOverlay = document.getElementById('countdownOverlay');
const cdNumber = document.getElementById('cdNumber');
const cdCategory = document.getElementById('cdCategory');
const cdLabel = document.getElementById('cdLabel');

// ─── PARTICLE SYSTEM ───
const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');
let particles = [];

const tiktokFrame = document.getElementById('tiktokFrame');
function resizeCanvas() {
    canvas.width = tiktokFrame.offsetWidth;
    canvas.height = tiktokFrame.offsetHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

class Particle {
    constructor(x, y, color, size, vx, vy, life) {
        this.x = x; this.y = y;
        this.color = color;
        this.size = size;
        this.vx = vx; this.vy = vy;
        this.life = life;
        this.maxLife = life;
        this.gravity = 0.15;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.vy += this.gravity;
        this.life--;
        this.vx *= 0.99;
    }

    draw(ctx) {
        const alpha = Math.max(0, this.life / this.maxLife);
        ctx.globalAlpha = alpha;
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * alpha, 0, Math.PI * 2);
        ctx.fill();

        // Glow
        ctx.globalAlpha = alpha * 0.3;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * alpha * 3, 0, Math.PI * 2);
        ctx.fill();
    }
}

function spawnParticleBurst(x, y, color, count, power) {
    for (let i = 0; i < count; i++) {
        const angle = (Math.PI * 2 / count) * i + (Math.random() - 0.5) * 0.5;
        const speed = 2 + Math.random() * power;
        particles.push(new Particle(
            x, y, color,
            2 + Math.random() * 3,
            Math.cos(angle) * speed,
            Math.sin(angle) * speed - 2,
            30 + Math.random() * 30
        ));
    }
}

function spawnWallSparks(color) {
    const wallRect = wall.getBoundingClientRect();
    const cx = wallRect.left + wallRect.width / 2;
    for (let i = 0; i < 12; i++) {
        const y = wallRect.top + Math.random() * wallRect.height;
        particles.push(new Particle(
            cx, y, color,
            1 + Math.random() * 2,
            (Math.random() - 0.5) * 8,
            (Math.random() - 0.5) * 6,
            15 + Math.random() * 20
        ));
    }
}

// Ambient floating particles
function spawnAmbientParticle() {
    if (particles.length > 200) return;
    const cat = CATEGORIES[currentCategory];
    const color = Math.random() > 0.5 ? cat.leftColor : cat.rightColor;
    particles.push(new Particle(
        Math.random() * canvas.width,
        canvas.height + 10,
        color + '44',
        1 + Math.random() * 2,
        (Math.random() - 0.5) * 0.5,
        -0.5 - Math.random() * 1,
        100 + Math.random() * 100
    ));
}

function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.globalAlpha = 1;

    for (let i = particles.length - 1; i >= 0; i--) {
        particles[i].update();
        particles[i].draw(ctx);
        if (particles[i].life <= 0) particles.splice(i, 1);
    }

    if (Math.random() < 0.15) spawnAmbientParticle();
    requestAnimationFrame(animateParticles);
}

// ─── FLAME AURA SYSTEM ───
const flameLeftCanvas = document.getElementById('flameLeft');
const flameRightCanvas = document.getElementById('flameRight');
const flameLeftCtx = flameLeftCanvas.getContext('2d');
const flameRightCtx = flameRightCanvas.getContext('2d');

// Flame intensity per team (0 = off, grows infinitely)
let flameIntensity = { men: 0, women: 0 };
let flameTargetIntensity = { men: 0, women: 0 };

// ─── RANDOM USERNAMES ───
const USERNAME_PARTS_1 = ['Dark','Luna','Fire','Ice','Neo','Xx','El','La','Mr','Miss','DJ','King','Queen','Baby','Lil','Big','Pro','Epic','Shadow','Storm','Star','Magic','Ultra','Mega','Super','Cool','Hot','Wild','Crazy','Lucky'];
const USERNAME_PARTS_2 = ['Wolf','Dragon','Angel','Demon','Tiger','Panda','Eagle','Phoenix','Ninja','Gamer','Boss','Chief','Killer','Master','Lord','Prince','Queen','Warrior','Legend','Champion','Viper','Cobra','Fox','Bear','Lion','Shark','Hawk','Ghost','Rider','Knight'];
const USERNAME_NUMS = ['','','','01','07','23','99','777','420','69','88','2k','_xd','_gg','HD','tv','YT'];

function randomUsername() {
    const p1 = USERNAME_PARTS_1[Math.floor(Math.random() * USERNAME_PARTS_1.length)];
    const p2 = USERNAME_PARTS_2[Math.floor(Math.random() * USERNAME_PARTS_2.length)];
    const n = USERNAME_NUMS[Math.floor(Math.random() * USERNAME_NUMS.length)];
    return p1 + p2 + n;
}

// ─── COMEBACK SYSTEM ───
let prevRatio = 0.5;
let comebackShown = { men: false, women: false };

// ─── DANGER / TENSION ───
let leftDangerActive = false;
let rightDangerActive = false;
const tensionVignette = document.getElementById('tensionVignette');
let tensionActive = false;
let heartbeatInterval = null;
let dangerSoundPlaying = false;

// Flame particles (separate from main particle system)
let flameParticlesLeft = [];
let flameParticlesRight = [];

class FlameParticle {
    constructor(x, y, baseColor, intensity) {
        this.x = x + (Math.random() - 0.5) * Math.min(intensity * 3, 60);
        this.y = y;
        this.baseX = x;
        this.size = 2 + Math.random() * (3 + intensity * 0.3);
        this.maxLife = 20 + Math.random() * (15 + intensity * 2);
        this.life = this.maxLife;
        // Speed increases with intensity
        this.vy = -(1.5 + Math.random() * (2 + intensity * 0.15));
        this.vx = (Math.random() - 0.5) * (1.5 + intensity * 0.08);
        this.wobbleSpeed = 2 + Math.random() * 3;
        this.wobbleAmp = 1 + Math.random() * (1.5 + intensity * 0.05);
        this.baseColor = baseColor;
        this.intensity = intensity;
        this.t = Math.random() * Math.PI * 2;
    }

    update() {
        this.t += 0.15;
        this.x += this.vx + Math.sin(this.t * this.wobbleSpeed) * this.wobbleAmp * 0.3;
        this.y += this.vy;
        this.life--;
    }

    draw(ctx) {
        const progress = 1 - (this.life / this.maxLife); // 0 = new, 1 = dying
        const alpha = Math.max(0, 1 - progress * 1.2) * Math.min(1, this.intensity / 3);

        // Color evolves: at low intensity just team color
        // As intensity grows: core goes white → yellow → team color at edges
        let color;
        const inten = this.intensity;

        if (inten < 5) {
            // Low: just team color with glow
            color = this.baseColor;
        } else if (inten < 12) {
            // Medium: orange/yellow core
            if (progress < 0.3) color = '#ffffff';
            else if (progress < 0.5) color = '#ffee44';
            else if (progress < 0.7) color = '#ffaa22';
            else color = this.baseColor;
        } else if (inten < 25) {
            // High: white-hot core, blue/team color tips
            if (progress < 0.2) color = '#ffffff';
            else if (progress < 0.35) color = '#ffffaa';
            else if (progress < 0.5) color = '#ffcc44';
            else if (progress < 0.7) color = '#ff6622';
            else color = this.baseColor;
        } else {
            // Godlike: electric white core, intense colors
            if (progress < 0.15) color = '#ffffff';
            else if (progress < 0.25) color = '#eeeeff';
            else if (progress < 0.4) color = '#ffdd66';
            else if (progress < 0.55) color = '#ff8833';
            else if (progress < 0.75) color = '#ff4411';
            else color = this.baseColor;
        }

        const sz = this.size * (1 - progress * 0.5);

        // Main dot
        ctx.globalAlpha = alpha;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, sz, 0, Math.PI * 2);
        ctx.fill();

        // Glow (grows with intensity)
        const glowMult = 2 + Math.min(inten * 0.15, 4);
        ctx.globalAlpha = alpha * 0.25;
        ctx.beginPath();
        ctx.arc(this.x, this.y, sz * glowMult, 0, Math.PI * 2);
        ctx.fill();

        // Extra outer glow for high intensity
        if (inten >= 15) {
            ctx.globalAlpha = alpha * 0.1;
            ctx.beginPath();
            ctx.arc(this.x, this.y, sz * glowMult * 1.8, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}

function updateFlameAuras() {
    // Smooth intensity towards target
    for (const team of ['men', 'women']) {
        const diff = flameTargetIntensity[team] - flameIntensity[team];
        flameIntensity[team] += diff * 0.12;
        // Natural decay when no combo
        if (flameTargetIntensity[team] === 0) {
            flameIntensity[team] *= 0.94;
            if (flameIntensity[team] < 0.1) flameIntensity[team] = 0;
        }
    }

    // Dynamically size canvases to fit growing flames
    for (const [fcanvas, inten] of [[flameLeftCanvas, flameIntensity.men], [flameRightCanvas, flameIntensity.women]]) {
        const w = 200 + Math.min(inten * 8, 300);
        const h = 300 + Math.min(inten * 10, 400);
        if (Math.abs(fcanvas.width - w) > 10) { fcanvas.width = w; }
        if (Math.abs(fcanvas.height - h) > 10) { fcanvas.height = h; }
    }

    renderFlame(flameLeftCtx, flameLeftCanvas, flameParticlesLeft, flameIntensity.men, CATEGORIES[currentCategory].leftColor, leftDangerActive);
    renderFlame(flameRightCtx, flameRightCanvas, flameParticlesRight, flameIntensity.women, CATEGORIES[currentCategory].rightColor, rightDangerActive);

    // Position canvases to follow characters
    const arenaRect = arena.getBoundingClientRect();

    const leftRect = charLeft.getBoundingClientRect();
    const leftCx = leftRect.left - arenaRect.left + leftRect.width / 2;
    const leftCy = leftRect.top - arenaRect.top + leftRect.height / 2;
    flameLeftCanvas.style.left = (leftCx - flameLeftCanvas.width / 2) + 'px';
    flameLeftCanvas.style.top = (leftCy - flameLeftCanvas.height * 0.55) + 'px';

    const rightRect = charRight.getBoundingClientRect();
    const rightCx = rightRect.left - arenaRect.left + rightRect.width / 2;
    const rightCy = rightRect.top - arenaRect.top + rightRect.height / 2;
    flameRightCanvas.style.left = (rightCx - flameRightCanvas.width / 2) + 'px';
    flameRightCanvas.style.top = (rightCy - flameRightCanvas.height * 0.55) + 'px';

    requestAnimationFrame(updateFlameAuras);
}

function renderFlame(fctx, fcanvas, fparticles, intensity, baseColor, inDanger) {
    fctx.clearRect(0, 0, fcanvas.width, fcanvas.height);

    if (intensity < 0.3) return;

    const cx = fcanvas.width / 2;
    const cy = fcanvas.height * 0.7;

    // Spawn rate increases with intensity (no cap = no limit feeling)
    const spawnRate = Math.min(intensity * 0.8, 15);
    for (let i = 0; i < spawnRate; i++) {
        if (Math.random() < 0.7) {
            fparticles.push(new FlameParticle(cx, cy, baseColor, intensity));
        }
    }

    // Wide base flames at higher intensity
    if (intensity > 8) {
        const extra = Math.min((intensity - 8) * 0.3, 5);
        for (let i = 0; i < extra; i++) {
            const p = new FlameParticle(cx, cy, baseColor, intensity);
            p.x = cx + (Math.random() - 0.5) * Math.min(intensity * 5, 140);
            p.vy *= 0.7;
            p.maxLife *= 0.6;
            p.life = p.maxLife;
            fparticles.push(p);
        }
    }

    // Update & draw
    for (let i = fparticles.length - 1; i >= 0; i--) {
        fparticles[i].update();
        fparticles[i].draw(fctx);
        if (fparticles[i].life <= 0) fparticles.splice(i, 1);
    }

    // Central glow (grows with intensity)
    const glowRadius = 20 + Math.min(intensity * 4, 80);
    const glowAlpha = Math.min(intensity * 0.04, 0.4);
    fctx.globalAlpha = glowAlpha;
    const grad = fctx.createRadialGradient(cx, cy, 0, cx, cy, glowRadius);
    grad.addColorStop(0, intensity > 15 ? '#ffffff' : baseColor);
    grad.addColorStop(0.4, baseColor);
    grad.addColorStop(1, 'transparent');
    fctx.fillStyle = grad;
    fctx.beginPath();
    fctx.arc(cx, cy, glowRadius, 0, Math.PI * 2);
    fctx.fill();
    fctx.globalAlpha = 1;
}

updateFlameAuras();

animateParticles();

// ─── TTS AUDIO SYSTEM ───
const ttsAudios = { male: {}, female: {} };
let ttsPlaying = false; // prevent overlapping TTS

// Preload all TTS clips
function preloadTTS() {
    const manifest = {"male":{"round_start_1":"audio/male/round_start_1.mp3","round_start_2":"audio/male/round_start_2.mp3","combo_t1":"audio/male/combo_t1.mp3","combo_t2":"audio/male/combo_t2.mp3","combo_t3_a":"audio/male/combo_t3_a.mp3","combo_t3_b":"audio/male/combo_t3_b.mp3","combo_t4_a":"audio/male/combo_t4_a.mp3","combo_t4_b":"audio/male/combo_t4_b.mp3","combo_t5_a":"audio/male/combo_t5_a.mp3","combo_t5_b":"audio/male/combo_t5_b.mp3","danger_1":"audio/male/danger_1.mp3","danger_critical":"audio/male/danger_critical.mp3","comeback_1":"audio/male/comeback_1.mp3","comeback_2":"audio/male/comeback_2.mp3","round_win_1":"audio/male/round_win_1.mp3","round_win_2":"audio/male/round_win_2.mp3","regalo_1":"audio/male/regalo_1.mp3","tension_30s":"audio/male/tension_30s.mp3","tension_10s":"audio/male/tension_10s.mp3","glory_1":"audio/male/glory_1.mp3","glory_2":"audio/male/glory_2.mp3","empate":"audio/male/empate.mp3","hype_1":"audio/male/hype_1.mp3","hype_2":"audio/male/hype_2.mp3","hype_3":"audio/male/hype_3.mp3","hype_4":"audio/male/hype_4.mp3"},"female":{"round_start_1":"audio/female/round_start_1.mp3","round_start_2":"audio/female/round_start_2.mp3","combo_t1":"audio/female/combo_t1.mp3","combo_t2":"audio/female/combo_t2.mp3","combo_t3_a":"audio/female/combo_t3_a.mp3","combo_t3_b":"audio/female/combo_t3_b.mp3","combo_t4_a":"audio/female/combo_t4_a.mp3","combo_t4_b":"audio/female/combo_t4_b.mp3","combo_t5_a":"audio/female/combo_t5_a.mp3","combo_t5_b":"audio/female/combo_t5_b.mp3","danger_1":"audio/female/danger_1.mp3","danger_critical":"audio/female/danger_critical.mp3","comeback_1":"audio/female/comeback_1.mp3","comeback_2":"audio/female/comeback_2.mp3","round_win_1":"audio/female/round_win_1.mp3","round_win_2":"audio/female/round_win_2.mp3","regalo_1":"audio/female/regalo_1.mp3","tension_30s":"audio/female/tension_30s.mp3","tension_10s":"audio/female/tension_10s.mp3","glory_1":"audio/female/glory_1.mp3","glory_2":"audio/female/glory_2.mp3","empate":"audio/female/empate.mp3","hype_1":"audio/female/hype_1.mp3","hype_2":"audio/female/hype_2.mp3","hype_3":"audio/female/hype_3.mp3","hype_4":"audio/female/hype_4.mp3"}};

    for (const gender of ['male', 'female']) {
        for (const [id, path] of Object.entries(manifest[gender])) {
            const audio = new Audio(STATIC_BASE + path);
            audio.preload = 'auto';
            ttsAudios[gender][id] = audio;
        }
    }
}

// Play a TTS clip. gender: 'male'|'female', id: clip name
// force: play even if another TTS is playing
function playTTS(id, gender, force) {
    // Pick random gender if not specified
    if (!gender) gender = Math.random() > 0.5 ? 'male' : 'female';

    if (ttsPlaying && !force) return;

    const audio = ttsAudios[gender]?.[id];
    if (!audio) return;

    ttsPlaying = true;
    const clone = audio.cloneNode();
    clone.volume = 0.8;
    clone.play().catch(() => {});
    clone.onended = () => { ttsPlaying = false; };
    // Safety timeout in case onended doesn't fire
    setTimeout(() => { ttsPlaying = false; }, 4000);
}

// Pick random from alternatives (e.g. 'combo_t3' picks 'combo_t3_a' or 'combo_t3_b')
function playTTSRandom(idPrefix, gender, force) {
    const suffixes = ['_a', '_b', '_1', '_2'];
    const options = suffixes.map(s => idPrefix + s).filter(id => ttsAudios[gender || 'male']?.[id]);
    // Also check without suffix
    if (ttsAudios[gender || 'male']?.[idPrefix]) options.push(idPrefix);
    if (options.length === 0) return;
    const pick = options[Math.floor(Math.random() * options.length)];
    playTTS(pick, gender, force);
}

preloadTTS();

// ─── SFX MUSIC SYSTEM ───
const sfx = {};
let battleMusicEl = null;
let drumRollEl = null;

function preloadSFX() {
    const sfxFiles = {
        'round_win_fanfare': 'audio/sfx/sfx_round_win_fanfare.mp3',
        'glory_anthem': 'audio/sfx/sfx_glory_anthem.mp3',
        'battle_loop': 'audio/sfx/sfx_battle_loop.mp3',
        'drum_roll': 'audio/sfx/sfx_drum_roll.mp3',
        'countdown_tick': 'audio/sfx/sfx_countdown_tick.mp3',
        'comeback_hit': 'audio/sfx/sfx_comeback_hit.mp3',
    };
    for (const [id, path] of Object.entries(sfxFiles)) {
        const audio = new Audio();
        audio.preload = 'auto';
        audio.src = STATIC_BASE + path;
        audio.load();
        sfx[id] = audio;
    }
}

function playSFX(id, volume, loop) {
    const audio = sfx[id];
    if (!audio) { console.warn('SFX not found:', id); return null; }
    const clone = audio.cloneNode();
    clone.volume = volume || 0.5;
    clone.loop = loop || false;
    clone.play().then(() => {
        console.log('SFX playing:', id);
    }).catch(e => {
        console.error('SFX play failed:', id, e.message);
    });
    return clone;
}

function startBattleMusic() {
    stopBattleMusic();
    battleMusicEl = playSFX('battle_loop', 0.25, true);
}

function stopBattleMusic() {
    if (battleMusicEl) {
        battleMusicEl.pause();
        battleMusicEl = null;
    }
}

function startDrumRoll() {
    stopDrumRoll();
    drumRollEl = playSFX('drum_roll', 0.4, true);
}

function stopDrumRoll() {
    if (drumRollEl) {
        drumRollEl.pause();
        drumRollEl = null;
    }
}

preloadSFX();

// ─── SCREEN SHAKE ───
function screenShake(intensity) {
    gameContainer.classList.remove('shake-light', 'shake-heavy');
    void gameContainer.offsetWidth;
    gameContainer.classList.add(intensity >= 10 ? 'shake-heavy' : 'shake-light');
}

// ─── SOUND ENGINE (Web Audio API) ───
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

let audioUnlocked = false;

// Master volume
const masterGain = audioCtx.createGain();
masterGain.gain.value = 0.4;
masterGain.connect(audioCtx.destination);

function playTone(freq, type, duration, volume, pan) {
    const now = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    const panner = audioCtx.createStereoPanner();

    osc.type = type;
    osc.frequency.setValueAtTime(freq, now);
    panner.pan.setValueAtTime(pan || 0, now);

    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(volume, now + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

    osc.connect(gain);
    gain.connect(panner);
    panner.connect(masterGain);

    osc.start(now);
    osc.stop(now + duration);
}

function playNoise(duration, volume, filterFreq, pan) {
    const now = audioCtx.currentTime;
    const bufferSize = audioCtx.sampleRate * duration;
    const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;

    const source = audioCtx.createBufferSource();
    source.buffer = buffer;

    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(filterFreq || 3000, now);

    const gain = audioCtx.createGain();
    gain.gain.setValueAtTime(volume, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

    const panner = audioCtx.createStereoPanner();
    panner.pan.setValueAtTime(pan || 0, now);

    source.connect(filter);
    filter.connect(gain);
    gain.connect(panner);
    panner.connect(masterGain);

    source.start(now);
}

// ── GIFT SOUNDS ──

// Pitch multiplier: men = grave (0.75), women = agudo (1.3)
function getP(isLeft) { return isLeft ? 0.75 : 1.3; }

function sfxRosa(pan, p) {
    playTone(880 * p, 'sine', 0.15, 0.3, pan);
    playTone(1100 * p, 'sine', 0.1, 0.15, pan);
}

function sfxMusica(pan, p) {
    [523, 659, 784].forEach((f, i) => {
        setTimeout(() => playTone(f * p, 'triangle', 0.15, 0.25, pan), i * 50);
    });
    playNoise(0.08, 0.05, 4000 * p, pan);
}

function sfxHelado(pan, p) {
    playNoise(0.25, 0.15, 2000 * p, pan);
    playTone(220 * p, 'sine', 0.3, 0.3, pan);
    playTone(440 * p, 'triangle', 0.2, 0.15, pan);
    setTimeout(() => {
        playTone(1200 * p, 'sine', 0.1, 0.12, pan);
        playTone(1600 * p, 'sine', 0.08, 0.08, pan);
    }, 100);
}

function sfxRegalo(pan, p) {
    const now = audioCtx.currentTime;

    // Sub boom (pitch affects starting freq)
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(80 * p, now);
    osc.frequency.exponentialRampToValueAtTime(30 * p, now + 0.5);
    g.gain.setValueAtTime(0.5, now);
    g.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
    osc.connect(g); g.connect(masterGain);
    osc.start(now); osc.stop(now + 0.6);

    // Noise explosion
    playNoise(0.4, 0.2, 5000 * p, pan);

    // Rising sweep
    const sweep = audioCtx.createOscillator();
    const sg = audioCtx.createGain();
    sweep.type = 'sawtooth';
    sweep.frequency.setValueAtTime(200 * p, now);
    sweep.frequency.exponentialRampToValueAtTime(2000 * p, now + 0.3);
    sg.gain.setValueAtTime(0.12, now);
    sg.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
    sweep.connect(sg); sg.connect(masterGain);
    sweep.start(now); sweep.stop(now + 0.35);

    // Sparkle cascade
    [1200, 1500, 1800, 2200, 2600].forEach((f, i) => {
        setTimeout(() => playTone(f * p, 'sine', 0.12, 0.08, pan), 80 + i * 60);
    });

    // Impact chord
    [130, 165, 196, 262].forEach(f => {
        playTone(f * p, 'triangle', 0.5, 0.1, pan);
    });
}

function sfxDonate(amount, isLeft) {
    const pan = isLeft ? -0.5 : 0.5;
    const p = getP(isLeft);
    if (amount <= 1) sfxRosa(pan, p);
    else if (amount <= 5) sfxHelado(pan, p);
    else sfxRegalo(pan, p);
}

// ── COMBO SOUNDS ──

function sfxCombo(tier, isLeft) {
    const pan = isLeft ? -0.4 : 0.4;
    const p = getP(isLeft);
    const now = audioCtx.currentTime;

    if (tier === 1) {
        playTone(600 * p, 'square', 0.06, 0.1, pan);
        setTimeout(() => playTone(800 * p, 'square', 0.06, 0.12, pan), 60);
    } else if (tier === 2) {
        [500, 700, 1000].forEach((f, i) => {
            setTimeout(() => playTone(f * p, 'square', 0.08, 0.12, pan), i * 50);
        });
    } else if (tier === 3) {
        // MEGA: sub punch + rising power chord + bright hit
        // Sub punch gives it weight
        playTone(55 * p, 'sine', 0.35, 0.3, pan);
        playNoise(0.2, 0.12, 2500 * p, pan);

        // Rising power chord (3 notes staggered = building momentum)
        [220, 330, 440, 550].forEach((f, i) => {
            setTimeout(() => playTone(f * p, 'sawtooth', 0.3, 0.07, pan), i * 45);
        });

        // Bright hit at the peak
        setTimeout(() => {
            playTone(880 * p, 'triangle', 0.2, 0.12, pan);
            playTone(1100 * p, 'sine', 0.15, 0.06, pan);
        }, 180);

    } else if (tier === 4) {
        // ULTRA: deep boom + fast rising sweep + stacked chord + cymbal
        // Deep boom (lower and longer than tier 3)
        playTone(40 * p, 'sine', 0.5, 0.4, pan);
        playTone(55 * p, 'sine', 0.4, 0.2, pan);
        playNoise(0.3, 0.15, 3500 * p, pan);

        // Fast rising sweep (dramatic tension)
        const sweep = audioCtx.createOscillator();
        const sg = audioCtx.createGain();
        sweep.type = 'sawtooth';
        sweep.frequency.setValueAtTime(80 * p, now);
        sweep.frequency.exponentialRampToValueAtTime(1800 * p, now + 0.35);
        sg.gain.setValueAtTime(0.1, now);
        sg.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
        sweep.connect(sg); sg.connect(masterGain);
        sweep.start(now); sweep.stop(now + 0.4);

        // Stacked power chord (5 notes = wall of sound)
        [165, 220, 330, 440, 660].forEach((f, i) => {
            setTimeout(() => playTone(f * p, 'sawtooth', 0.4, 0.06, pan), 50 + i * 35);
        });

        // Cymbal crash + bright sparkle at the top
        setTimeout(() => {
            playNoise(0.5, 0.1, 8000 * p, pan);
            playTone(1200 * p, 'sine', 0.2, 0.1, pan);
            playTone(1500 * p, 'sine', 0.15, 0.06, pan);
        }, 200);

        // Trailing sub rumble
        setTimeout(() => playTone(35 * p, 'sine', 0.3, 0.15, pan), 300);

    } else {
        // GODLIKE: earthquake sub + triple sweep + massive layered chord
        //          + cymbal wall + sparkle cascade + trailing thunder

        // Earthquake sub (lowest, longest, loudest)
        playTone(28 * p, 'sine', 0.8, 0.5, pan);
        playTone(42 * p, 'sine', 0.6, 0.3, pan);
        playTone(56 * p, 'sine', 0.5, 0.2, pan);

        // Noise layers (low rumble + high crash)
        playNoise(0.6, 0.18, 1200 * p, pan);
        playNoise(0.4, 0.15, 6000 * p, pan);

        // Triple staggered sweeps (wall of rising sound)
        [['sawtooth', 60, 2500, 0.5], ['square', 100, 3500, 0.4], ['sawtooth', 150, 4500, 0.35]].forEach(([type, f1, f2, dur], i) => {
            setTimeout(() => {
                const sw = audioCtx.createOscillator();
                const g2 = audioCtx.createGain();
                sw.type = type;
                sw.frequency.setValueAtTime(f1 * p, audioCtx.currentTime);
                sw.frequency.exponentialRampToValueAtTime(f2 * p, audioCtx.currentTime + dur);
                g2.gain.setValueAtTime(0.07, audioCtx.currentTime);
                g2.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur + 0.05);
                sw.connect(g2); g2.connect(masterGain);
                sw.start(audioCtx.currentTime); sw.stop(audioCtx.currentTime + dur + 0.05);
            }, i * 70);
        });

        // Massive chord (7 notes staggered = epic orchestral wall)
        [110, 165, 220, 330, 440, 660, 880].forEach((f, i) => {
            setTimeout(() => {
                playTone(f * p, 'sawtooth', 0.6, 0.05, pan);
                playTone(f * p, 'triangle', 0.5, 0.04, pan);
            }, 30 + i * 30);
        });

        // Cymbal wall
        setTimeout(() => {
            playNoise(0.8, 0.12, 10000 * p, pan);
            playNoise(0.5, 0.08, 6000 * p, pan);
        }, 150);

        // Bright sparkle cascade (high freq rain)
        for (let i = 0; i < 12; i++) {
            setTimeout(() => {
                playTone((1200 + Math.random() * 2500) * p, 'sine', 0.12, 0.04, pan);
            }, 200 + i * 50);
        }

        // Trailing thunder (delayed sub rumbles)
        setTimeout(() => {
            playTone(30 * p, 'sine', 0.5, 0.2, pan);
            playNoise(0.4, 0.08, 800 * p, pan);
        }, 400);
        setTimeout(() => {
            playTone(25 * p, 'sine', 0.4, 0.12, pan);
        }, 600);
    }
}

// ── WALL CLASH ──

function sfxWallClash(amount) {
    const intensity = Math.min(amount / 50, 1);
    playNoise(0.06 + intensity * 0.1, 0.05 + intensity * 0.1, 1500 + intensity * 3000, 0);
    playTone(150 + intensity * 100, 'triangle', 0.08, 0.05 + intensity * 0.1, 0);
}

// ── VICTORY ──

function sfxVictory() {
    const now = audioCtx.currentTime;

    // Fanfare: rising major arpeggio
    const notes = [262, 330, 392, 524, 660, 784, 1048];
    notes.forEach((f, i) => {
        setTimeout(() => {
            playTone(f, 'triangle', 0.4, 0.15, 0);
            playTone(f * 0.5, 'sine', 0.5, 0.08, 0);
        }, i * 100);
    });

    // Cymbal crash
    setTimeout(() => playNoise(1.2, 0.12, 8000, 0), 200);

    // Sub boom at climax
    setTimeout(() => {
        playTone(60, 'sine', 0.8, 0.3, 0);
        playNoise(0.4, 0.15, 2000, 0);
    }, 600);

    // Sparkle tail
    for (let i = 0; i < 12; i++) {
        setTimeout(() => playTone(1000 + Math.random() * 3000, 'sine', 0.1, 0.03, Math.random() * 2 - 1), 800 + i * 80);
    }
}

// ── COUNTDOWN ──

function sfxCountdownTick() {
    playTone(800, 'square', 0.08, 0.15, 0);
    playTone(400, 'sine', 0.1, 0.08, 0);
}

function sfxCountdownGo() {
    // Epic "GO" stinger
    playNoise(0.15, 0.12, 5000, 0);
    playTone(524, 'sawtooth', 0.15, 0.15, 0);
    playTone(660, 'triangle', 0.3, 0.12, 0);
    playTone(784, 'triangle', 0.3, 0.1, 0);
    playTone(1048, 'sine', 0.4, 0.08, 0);
    playTone(130, 'sine', 0.3, 0.2, 0);
}

// ── DANGER ALARM ──

function sfxDangerAlarm() {
    // Short warning siren: two alternating tones
    playTone(400, 'square', 0.12, 0.08, 0);
    setTimeout(() => playTone(500, 'square', 0.12, 0.08, 0), 150);
    setTimeout(() => playTone(400, 'square', 0.12, 0.06, 0), 300);
}

// ── TIMER WARNING ──

function sfxTimerTick() {
    playTone(1000, 'square', 0.03, 0.06, 0);
}

// ─── DONATE ───
function donate(team, amount, donorName) {
    if (gameOver) return;

    const cat = CATEGORIES[currentCategory];
    const isLeft = team === 'men';
    const charEl = isLeft ? charLeft : charRight;
    const color = isLeft ? cat.leftColor : cat.rightColor;
    const username = donorName || randomUsername();

    if (isLeft) leftPoints += amount;
    else rightPoints += amount;

    // Sound
    sfxDonate(amount, isLeft);
    sfxWallClash(amount);

    // Push animation
    charEl.classList.remove('pushing');
    void charEl.offsetWidth;
    charEl.classList.add('pushing');

    // Wall clash
    wall.classList.remove('clash');
    void wall.offsetWidth;
    wall.classList.add('clash');

    // Floating point with donor name
    spawnFloatingPoint(charEl, amount, color, username);

    const rect = charEl.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;

    // ─── GIFT-TIER EFFECTS (escalating with amount) ───
    if (amount <= 1) {
        // 1 moneda (GG/Rose): small burst, small sparks
        spawnParticleBurst(cx, cy, color, 8, 3);
        spawnWallSparks(color);
    } else if (amount <= 5) {
        // 5 monedas (Finger Heart/Embroidered Heart): medium+ burst + shake + lightning
        if (Math.random() < 0.3) playTTSRandom('hype', isLeft ? 'male' : 'female');
        spawnParticleBurst(cx, cy, color, 25, 4);
        spawnWallSparks(color);
        spawnWallSparks(color);
        screenShake(10);
        spawnLightning(color);
        spawnParticleBurst(cx, cy, color, 35, 5);
        spawnParticleBurst(cx, cy, '#ffffff', 12, 3);
        spawnWallSparks(color);
        spawnWallSparks(color);
        spawnWallSparks('#ffffff');
        screenShake(15);
        spawnLightning(color);
        // Shockwave ring
        spawnShockwave(cx, cy, color);
    } else {
        // Regalo (50): ABSOLUTE SPECTACLE
        // Multiple particle bursts staggered
        spawnParticleBurst(cx, cy, color, 60, 8);
        setTimeout(() => spawnParticleBurst(cx, cy, '#ffffff', 40, 6), 80);
        setTimeout(() => spawnParticleBurst(cx, cy, color, 30, 5), 160);

        // Triple wall sparks
        spawnWallSparks(color);
        spawnWallSparks('#ffffff');
        setTimeout(() => { spawnWallSparks(color); spawnWallSparks(color); }, 100);

        // Heavy screen shake
        screenShake(50);

        // Double lightning
        spawnLightning(color);
        setTimeout(() => spawnLightning('#ffffff'), 100);
        setTimeout(() => spawnLightning(color), 200);

        // Shockwave
        spawnShockwave(cx, cy, color);
        setTimeout(() => spawnShockwave(cx, cy, '#ffffff'), 150);

        // Particle rain from top
        for (let i = 0; i < 15; i++) {
            setTimeout(() => {
                spawnParticleBurst(Math.random() * canvas.width, 0, color, 4, 2);
            }, i * 40);
        }

        // Gift name flash across screen
        showGiftFlash(isLeft, color, username);
        playTTS('regalo_1', isLeft ? 'male' : 'female');
    }

    // Independent streak tracking per team
    const now = Date.now();
    const s = streaks[team];

    if (now - s.lastTime < 2000) {
        s.count++;
    } else {
        s.count = 1;
    }
    s.lastTime = now;

    if (s.count >= 3) {
        const tier = getComboTier(s.count);
        showCombo(isLeft, s.count, color, username);
        updatePersistentCombo(isLeft, s.count, color);
        sfxCombo(tier, isLeft);

        // TTS combo (only on tier transitions, not every hit)
        const prevTier = getComboTier(s.count - 1);
        if (tier > prevTier) {
            const comboGender = isLeft ? 'male' : 'female';
            playTTSRandom('combo_t' + tier, comboGender);
        }

        // Flame aura grows with combo count (no cap!)
        flameTargetIntensity[team] = s.count;

        // Escalating effects based on combo tier
        if (tier >= 2) screenShake(s.count * 3);
        if (tier >= 3) spawnParticleBurst(canvas.width / 2, canvas.height / 2, color, s.count * 3, tier * 2);
        if (tier >= 4) spawnLightning(color);
        if (tier >= 5) {
            spawnLightning(color);
            spawnLightning('#ffffff');
            for (let i = 0; i < 20; i++) {
                setTimeout(() => {
                    spawnParticleBurst(
                        Math.random() * canvas.width,
                        0, color, 5, 3
                    );
                }, i * 30);
            }
        }
    }

    // Decay timer per team (resets combo if no donation in 2.5s)
    clearTimeout(s.decayTimer);
    s.decayTimer = setTimeout(() => {
        if (s.count >= 3) hidePersistentCombo(team === 'men');
        s.count = 0;
        flameTargetIntensity[team] = 0;
    }, 2500);

    // Big donation lightning
    if (amount >= 10) spawnLightning(color);

    updateVisuals();
    checkWin();
}

// ─── COMBO TIER SYSTEM ───
const COMBO_TIERS = [
    { min: 3,  label: 'COMBO',      tier: 1 },
    { min: 5,  label: 'SUPER',      tier: 2 },
    { min: 8,  label: 'MEGA',       tier: 3 },
    { min: 12, label: 'ULTRA',      tier: 4 },
    { min: 20, label: 'GODLIKE',    tier: 5 },
];

const COMBO_MESSAGES = {
    1: ['COMBO!', 'NICE!', 'DALE!'],
    2: ['SUPER!', 'ON FIRE!', 'VAMOS!'],
    3: ['MEGA!', 'BRUTAL!', 'IMPARABLE!'],
    4: ['ULTRA!', 'DESTRUCCION!', 'LOCURA!'],
    5: ['GODLIKE!', 'LEGENDARIO!', 'APOCALIPSIS!', 'DIOS MIO!'],
};

function getComboTier(count) {
    let tier = 1;
    for (const t of COMBO_TIERS) {
        if (count >= t.min) tier = t.tier;
    }
    return tier;
}

function getComboMessage(tier) {
    const msgs = COMBO_MESSAGES[tier];
    return msgs[Math.floor(Math.random() * msgs.length)];
}

// Persistent combo counters (one per side)
let persistentComboLeft = null;
let persistentComboRight = null;
// (decay timers are now per-team in streaks object)

function showCombo(isLeft, count, color, username) {
    const tier = getComboTier(count);
    const msg = getComboMessage(tier);

    const combo = document.createElement('div');
    combo.className = `combo-text combo-t${tier}`;

    // Font size scales with tier
    const baseFontSize = [36, 48, 64, 80, 110][tier - 1];
    combo.style.fontSize = baseFontSize + 'px';
    combo.style.color = color;

    // Text shadow intensity scales with tier
    const glowSize = [20, 30, 45, 60, 80][tier - 1];
    const layers = tier >= 4 ? `, 0 0 ${glowSize * 2}px ${color}, 0 0 ${glowSize * 3}px ${color}` : '';
    combo.style.textShadow = `0 0 ${glowSize}px ${color}${layers}`;

    // Stroke effect for higher tiers
    if (tier >= 3) {
        combo.style.webkitTextStroke = `${tier >= 4 ? 2 : 1}px rgba(255,255,255,0.4)`;
    }

    // Combo text + donor name below
    const nameSize = Math.max(12, baseFontSize * 0.22);
    combo.innerHTML = `${count}x ${msg}<br><span style="font-family:'Inter',sans-serif;font-size:${nameSize}px;letter-spacing:1px;opacity:0.8;-webkit-text-stroke:0">${username || ''}</span>`;

    // Position with slight randomness at higher tiers
    const jitterX = tier >= 3 ? (Math.random() - 0.5) * (tier * 5) : 0;
    const jitterY = tier >= 3 ? (Math.random() - 0.5) * (tier * 3) : 0;
    combo.style.left = `calc(${isLeft ? '15%' : '55%'} + ${jitterX}px)`;
    combo.style.top = `calc(15% + ${jitterY}px)`;

    // Duration scales with tier
    const duration = [600, 700, 800, 900, 1200][tier - 1];

    arena.appendChild(combo);
    setTimeout(() => combo.remove(), duration);
}

function updatePersistentCombo(isLeft, count, color) {
    const tier = getComboTier(count);
    let el = isLeft ? persistentComboLeft : persistentComboRight;

    if (!el) {
        el = document.createElement('div');
        el.className = 'combo-persistent';
        el.innerHTML = '<span class="combo-count"></span><span class="combo-label"></span>';
        el.style.top = '75%';
        el.style.left = isLeft ? '8%' : '78%';
        el.style.textAlign = isLeft ? 'left' : 'right';
        arena.appendChild(el);
        if (isLeft) persistentComboLeft = el;
        else persistentComboRight = el;

        // Fade in
        el.style.opacity = '0';
        requestAnimationFrame(() => {
            el.style.transition = 'opacity 0.3s, font-size 0.3s, color 0.2s';
            el.style.opacity = '1';
        });
    }

    // Update content
    const tierLabel = COMBO_TIERS.find(t => t.tier === tier)?.label || 'COMBO';
    el.querySelector('.combo-count').textContent = `${count}x`;
    el.querySelector('.combo-label').textContent = tierLabel;

    // Scale size with tier
    const fontSize = [28, 38, 52, 68, 90][tier - 1];
    el.style.fontSize = fontSize + 'px';
    el.style.color = color;

    // Glow intensity
    const glow = [15, 25, 40, 55, 80][tier - 1];
    const extraGlow = tier >= 4 ? `, 0 0 ${glow * 2}px ${color}` : '';
    const ultraGlow = tier >= 5 ? `, 0 0 ${glow * 3}px ${color}, 0 0 ${glow * 4}px #fff` : '';
    el.style.textShadow = `0 0 ${glow}px ${color}${extraGlow}${ultraGlow}`;

    if (tier >= 3) {
        el.style.webkitTextStroke = `${Math.min(tier - 2, 3)}px rgba(255,255,255,0.3)`;
    } else {
        el.style.webkitTextStroke = 'none';
    }

    // Shake animation - escalates with tier
    const shakeClass = ['shake-micro', 'shake-micro', 'shake-medium', 'shake-heavy', 'shake-insane'][tier - 1];
    el.classList.remove('shake-micro', 'shake-medium', 'shake-heavy', 'shake-insane');
    void el.offsetWidth;
    el.classList.add(shakeClass);

}

function hidePersistentCombo(isLeft) {
    const el = isLeft ? persistentComboLeft : persistentComboRight;
    if (!el) return;

    el.style.transition = 'opacity 0.5s, transform 0.5s';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-20px)';
    setTimeout(() => {
        el.remove();
        if (isLeft) persistentComboLeft = null;
        else persistentComboRight = null;
    }, 500);
}

function spawnLightning(color) {
    const wallRect = wall.getBoundingClientRect();
    const arenaRect = arena.getBoundingClientRect();

    // Flash the whole screen briefly
    const flash = document.createElement('div');
    flash.style.cssText = `
        position: absolute; inset: 0; z-index: 50;
        background: ${color}; opacity: 0; pointer-events: none;
    `;
    tiktokFrame.appendChild(flash);

    requestAnimationFrame(() => {
        flash.style.transition = 'opacity 0.05s';
        flash.style.opacity = '0.15';
        setTimeout(() => {
            flash.style.transition = 'opacity 0.3s';
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 300);
        }, 50);
    });
}

// ─── SHOCKWAVE ───
function spawnShockwave(x, y, color) {
    const ring = document.createElement('div');
    ring.style.cssText = `
        position: absolute; left: ${x}px; top: ${y}px;
        width: 10px; height: 10px; border-radius: 50%;
        border: 3px solid ${color};
        transform: translate(-50%, -50%) scale(1);
        pointer-events: none; z-index: 50;
        box-shadow: 0 0 15px ${color}, inset 0 0 15px ${color};
    `;
    tiktokFrame.appendChild(ring);

    ring.animate([
        { transform: 'translate(-50%, -50%) scale(1)', opacity: 0.9 },
        { transform: 'translate(-50%, -50%) scale(25)', opacity: 0 }
    ], { duration: 600, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' });

    setTimeout(() => ring.remove(), 600);
}

// ─── GIFT FLASH (big donation text across screen) ───
function showGiftFlash(isLeft, color, username) {
    const flash = document.createElement('div');
    flash.innerHTML = `🎁 REGALO! 🎁<br><span style="font-family:'Inter',sans-serif;font-size:28px;letter-spacing:4px;-webkit-text-stroke:0">${username || ''}</span>`;
    flash.style.cssText = `
        position: absolute; top: 50%;
        ${isLeft ? 'left: 30px; transform: translateY(-50%) scale(0); transform-origin: left center;' : 'right: 30px; transform: translateY(-50%) scale(0); transform-origin: right center;'}
        font-family: 'Bebas Neue', sans-serif;
        font-size: 80px; letter-spacing: 6px; text-align: center; line-height: 1.2;
        white-space: nowrap;
        color: ${color}; pointer-events: none; z-index: 55;
        text-shadow: 0 0 40px ${color}, 0 0 80px ${color}, 0 0 120px ${color};
        -webkit-text-stroke: 2px rgba(255,255,255,0.3);
    `;
    tiktokFrame.appendChild(flash);

    flash.animate([
        { transform: 'translateY(-50%) scale(0)', opacity: 0 },
        { transform: 'translateY(-50%) scale(1.1)', opacity: 1, offset: 0.2 },
        { transform: 'translateY(-50%) scale(1)', opacity: 1, offset: 0.4 },
        { transform: 'translateY(-50%) scale(1.05)', opacity: 0.8, offset: 0.7 },
        { transform: 'translateY(-50%) scale(0.9)', opacity: 0 }
    ], { duration: 1500, easing: 'ease-out', fill: 'forwards' });

    setTimeout(() => flash.remove(), 1500);
}

// ─── VISUALS ───
function updateVisuals() {
    const diff = leftPoints - rightPoints; // positive = left winning
    // Map diff to 0-100 position: 50 = center, 0 = left wins, 100 = right wins
    // Clamp diff to WIN_DIFF range
    const normalized = Math.max(-1, Math.min(1, diff / WIN_DIFF)); // -1 to 1
    const wallPos = 50 + normalized * 35; // 15% to 85% range

    const leftPctVal = Math.round(50 + normalized * 50);
    const rightPctVal = 100 - leftPctVal;

    leftBar.style.width = Math.max(leftPctVal, 2) + '%';
    rightBar.style.width = Math.max(rightPctVal, 2) + '%';
    leftPct.textContent = leftPctVal + '%';
    rightPct.textContent = rightPctVal + '%';

    // Wall + characters position
    wall.style.left = wallPos + '%';
    charLeft.style.left = `calc(${wallPos}% - 90px)`;
    charRight.style.left = `calc(${wallPos}% + 30px)`;

    // Character size scales with dominance (winner grows, loser shrinks)
    // normalized: -1 (right winning) to +1 (left winning)
    const leftScale = 1 + normalized * 0.3;   // 0.7 to 1.3
    const rightScale = 1 - normalized * 0.3;  // 1.3 to 0.7
    charLeft.style.fontSize = (70 * leftScale) + 'px';
    charRight.style.fontSize = (70 * rightScale) + 'px';

    // Glows follow characters
    leftGlow.style.left = `calc(${wallPos}% - 120px)`;
    rightGlow.style.left = `calc(${wallPos}% + 20px)`;

    // Glow intensity based on dominance
    const dominance = Math.abs(normalized);
    leftGlow.style.opacity = normalized > 0 ? 0.3 + dominance * 0.5 : 0.2;
    rightGlow.style.opacity = normalized < 0 ? 0.3 + dominance * 0.5 : 0.2;

    leftScoreEl.textContent = leftPoints + ' puntos';
    rightScoreEl.textContent = rightPoints + ' puntos';

    // Background gradient shift
    const cat = CATEGORIES[currentCategory];
    if (normalized > 0.2) {
        bgGradient.style.background = `radial-gradient(ellipse at 40% 50%, ${cat.leftColor}33, transparent 70%)`;
    } else if (normalized < -0.2) {
        bgGradient.style.background = `radial-gradient(ellipse at 60% 50%, ${cat.rightColor}33, transparent 70%)`;
    } else {
        bgGradient.style.background = `radial-gradient(ellipse at 50% 50%, ${cat.leftColor}15, ${cat.rightColor}15, transparent 70%)`;
    }

    // Edge glow when close to winning
    edgeLeft.classList.toggle('active', normalized > 0.5);
    edgeRight.classList.toggle('active', normalized < -0.5);
    edgeLeft.style.background = `linear-gradient(90deg, ${cat.leftColor}66, transparent)`;
    edgeRight.style.background = `linear-gradient(-90deg, ${cat.rightColor}66, transparent)`;

    // ─── DANGER ZONE (character-focused) ───
    const dangerDiff = WIN_DIFF * 0.65; // danger at 65% of win threshold
    const leftInDanger = diff <= -dangerDiff;
    const rightInDanger = diff >= dangerDiff;

    // Character CSS danger class
    charLeft.classList.toggle('in-danger', leftInDanger);
    charRight.classList.toggle('in-danger', rightInDanger);
    leftDangerActive = leftInDanger;
    rightDangerActive = rightInDanger;

    // Drum roll when someone is in danger
    if ((leftInDanger || rightInDanger) && !drumRollEl) {
        startDrumRoll();
    } else if (!leftInDanger && !rightInDanger && drumRollEl) {
        stopDrumRoll();
    }

    // Danger alarm sound (throttled)
    if ((leftInDanger || rightInDanger) && !dangerSoundPlaying) {
        dangerSoundPlaying = true;
        sfxDangerAlarm();
        // TTS danger (pick based on severity)
        const dangerGender = leftInDanger ? 'male' : 'female';
        const absDiff = Math.abs(leftPoints - rightPoints);
        if (absDiff >= WIN_DIFF * 0.85) {
            playTTS('danger_critical', dangerGender);
        } else {
            playTTS('danger_1', dangerGender);
        }
        setTimeout(() => { dangerSoundPlaying = false; }, 5000);
    }

    // ─── COMEBACK DETECTION ───
    // Left was losing badly and now came back to near even
    if (prevRatio < -0.5 && normalized >= -0.1 && !comebackShown.men) {
        triggerComeback(true, cat.leftColor, cat.leftName);
        comebackShown.men = true;
    }
    // Right was losing badly and now came back to near even
    if (prevRatio > 0.5 && normalized <= 0.1 && !comebackShown.women) {
        triggerComeback(false, cat.rightColor, cat.rightName);
        comebackShown.women = true;
    }
    prevRatio = normalized;
}

// ─── COMEBACK ───
function triggerComeback(isLeft, color, teamName) {
    sfxComeback();
    playTTSRandom('comeback', isLeft ? 'male' : 'female', true);
    playSFX('comeback_hit', 0.6);

    const banner = document.createElement('div');
    banner.className = 'comeback-banner';
    banner.innerHTML = `COMEBACK!<br><span style="font-size:0.4em;letter-spacing:4px;opacity:0.7">${teamName}</span>`;
    banner.style.color = color;
    banner.style.textShadow = `0 0 40px ${color}, 0 0 80px ${color}, 0 0 120px ${color}`;
    tiktokFrame.appendChild(banner);

    requestAnimationFrame(() => banner.classList.add('show'));
    setTimeout(() => banner.remove(), 1500);

    // Particle explosion from the side
    const x = isLeft ? canvas.width * 0.25 : canvas.width * 0.75;
    spawnParticleBurst(x, canvas.height / 2, color, 50, 7);
    setTimeout(() => spawnParticleBurst(x, canvas.height / 2, '#ffffff', 25, 5), 100);

    screenShake(30);
}

function sfxComeback() {
    // Dramatic reverse sweep + power chord + cymbal
    const now = audioCtx.currentTime;

    // Reverse sweep (high to low to high = tension release)
    const sweep = audioCtx.createOscillator();
    const sg = audioCtx.createGain();
    sweep.type = 'sawtooth';
    sweep.frequency.setValueAtTime(1500, now);
    sweep.frequency.exponentialRampToValueAtTime(100, now + 0.2);
    sweep.frequency.exponentialRampToValueAtTime(800, now + 0.5);
    sg.gain.setValueAtTime(0.1, now);
    sg.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
    sweep.connect(sg); sg.connect(masterGain);
    sweep.start(now); sweep.stop(now + 0.6);

    // Power chord
    [165, 220, 330, 440].forEach((f, i) => {
        setTimeout(() => playTone(f, 'triangle', 0.5, 0.1, 0), 150 + i * 30);
    });

    // Cymbal + sub
    setTimeout(() => {
        playNoise(0.8, 0.1, 7000, 0);
        playTone(55, 'sine', 0.5, 0.25, 0);
    }, 200);

    // Rising sparkles
    for (let i = 0; i < 6; i++) {
        setTimeout(() => playTone(800 + i * 200, 'sine', 0.1, 0.05, 0), 300 + i * 60);
    }
}

// ─── FINAL TENSION (last 30s) ───
let tensionStarted = false;

function startTension() {
    if (tensionStarted) return;
    tensionStarted = true;
    tensionActive = true;

    // TTS 30 seconds
    playTTS('tension_30s', null, true);

    tensionVignette.classList.add('active');
    document.querySelector('.progress-bar').classList.add('tension');

    // Heartbeat sound loop
    heartbeatInterval = setInterval(() => {
        if (gameOver || !tensionActive) { clearInterval(heartbeatInterval); return; }
        // Double beat: boom-boom
        playTone(50, 'sine', 0.12, 0.2, 0);
        playTone(70, 'sine', 0.08, 0.1, 0);
        setTimeout(() => {
            playTone(55, 'sine', 0.1, 0.15, 0);
            playTone(75, 'sine', 0.06, 0.08, 0);
        }, 150);
    }, Math.max(400, 800 - (30 - timeLeft) * 15)); // Accelerates as time runs out

    // Accelerating heartbeat: restart interval faster over time
    const accelInterval = setInterval(() => {
        if (gameOver || !tensionActive || timeLeft <= 0) { clearInterval(accelInterval); return; }
        clearInterval(heartbeatInterval);
        const speed = Math.max(300, 800 - (30 - timeLeft) * 18);
        heartbeatInterval = setInterval(() => {
            if (gameOver || !tensionActive) { clearInterval(heartbeatInterval); return; }
            playTone(50, 'sine', 0.12, 0.2, 0);
            playTone(70, 'sine', 0.08, 0.1, 0);
            setTimeout(() => {
                playTone(55, 'sine', 0.1, 0.15, 0);
                playTone(75, 'sine', 0.06, 0.08, 0);
            }, 150);
        }, speed);
    }, 3000);
}

function stopTension() {
    tensionActive = false;
    tensionStarted = false;
    clearInterval(heartbeatInterval);
    tensionVignette.classList.remove('active');
    document.querySelector('.progress-bar').classList.remove('tension');
    stopDrumRoll();
}

function checkWin() {
    const diff = leftPoints - rightPoints;

    if (diff >= WIN_DIFF) {
        endGame('left');
    } else if (diff <= -WIN_DIFF) {
        endGame('right');
    }
}

// ─── FLOATING POINTS ───
function spawnFloatingPoint(charEl, amount, color, username) {
    const rect = charEl.getBoundingClientRect();
    const arenaRect = arena.getBoundingClientRect();
    const x = rect.left - arenaRect.left + rect.width / 2;
    const y = rect.top - arenaRect.top - 10;
    const drift = (Math.random() - 0.5) * 40;

    // Points
    const fp = document.createElement('div');
    fp.className = 'floating-point' + (amount >= 5 ? ' big' : '');
    fp.textContent = '+' + amount;
    fp.style.color = color;
    fp.style.left = x + 'px';
    fp.style.top = y + 'px';

    fp.animate([
        { opacity: 1, transform: `translate(0, 0) scale(1)` },
        { opacity: 1, transform: `translate(${drift * 0.5}px, -40px) scale(1.3)`, offset: 0.4 },
        { opacity: 0, transform: `translate(${drift}px, -90px) scale(0.8)` }
    ], { duration: 900, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' });

    arena.appendChild(fp);
    setTimeout(() => fp.remove(), 900);

    // Donor name (appears below the points, drifts with it)
    if (username) {
        const dn = document.createElement('div');
        dn.className = 'donor-name';
        dn.textContent = username;
        dn.style.color = color;
        dn.style.textShadow = `0 0 8px ${color}`;
        dn.style.left = x + 'px';
        dn.style.top = (y + 30) + 'px';

        // Bigger name for bigger gifts
        if (amount >= 10) { dn.style.fontSize = '18px'; dn.style.textShadow = `0 0 15px ${color}, 0 0 30px ${color}`; }
        else if (amount >= 5) { dn.style.fontSize = '15px'; dn.style.textShadow = `0 0 12px ${color}`; }

        dn.animate([
            { opacity: 0.9, transform: `translate(0, 0) scale(1)` },
            { opacity: 0.7, transform: `translate(${drift * 0.4}px, -25px) scale(1)`, offset: 0.4 },
            { opacity: 0, transform: `translate(${drift * 0.6}px, -50px) scale(0.7)` }
        ], { duration: 700, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' });

        arena.appendChild(dn);
        setTimeout(() => dn.remove(), 700);
    }
}

// ─── END GAME ───
function endGame(winner) {
    gameOver = true;
    clearInterval(timerInterval);
    stopTension();

    const cat = CATEGORIES[currentCategory];
    const isLeft = winner === 'left';
    const color = isLeft ? cat.leftColor : cat.rightColor;

    // Update global wins
    globalWins[winner]++;
    updateScoreboard();

    // ─── CINEMATIC ROUND WIN ───
    stopBattleMusic();
    stopDrumRoll();
    playTTSRandom('round_win', isLeft ? 'male' : 'female', true);
    playSFX('round_win_fanfare', 0.5);

    // Impact sound: deep hit + reverse cymbal (different from everything else)
    playTone(80, 'sine', 0.5, 0.35, 0);
    playNoise(0.08, 0.2, 2000, 0);
    // Delayed clean tone
    setTimeout(() => {
        playTone(440, 'sine', 0.6, 0.08, 0);
        playTone(660, 'sine', 0.5, 0.06, 0);
    }, 300);

    // Cinematic black bars (top + bottom)
    const barTop = document.createElement('div');
    const barBot = document.createElement('div');
    const barCSS = `position:absolute;left:0;right:0;height:0;background:#000;z-index:80;pointer-events:none;`;
    barTop.style.cssText = barCSS + 'top:0;';
    barBot.style.cssText = barCSS + 'bottom:0;';
    tiktokFrame.appendChild(barTop);
    tiktokFrame.appendChild(barBot);

    barTop.animate([
        { height: '0px' },
        { height: '80px', offset: 0.15 },
        { height: '80px', offset: 0.8 },
        { height: '0px' }
    ], { duration: 2500, easing: 'ease-in-out', fill: 'forwards' });
    barBot.animate([
        { height: '0px' },
        { height: '80px', offset: 0.15 },
        { height: '80px', offset: 0.8 },
        { height: '0px' }
    ], { duration: 2500, easing: 'ease-in-out', fill: 'forwards' });
    setTimeout(() => { barTop.remove(); barBot.remove(); }, 2500);

    // Dim/desaturate the background briefly
    const dimmer = document.createElement('div');
    dimmer.style.cssText = `position:absolute;inset:0;background:rgba(0,0,0,0.5);z-index:75;pointer-events:none;`;
    tiktokFrame.appendChild(dimmer);
    dimmer.animate([
        { opacity: 0 },
        { opacity: 1, offset: 0.12 },
        { opacity: 1, offset: 0.75 },
        { opacity: 0 }
    ], { duration: 2500, easing: 'ease-in-out', fill: 'forwards' });
    setTimeout(() => dimmer.remove(), 2500);

    // Clean white text (NO glow, NO Bebas Neue, NO team color - completely different)
    const teamName = isLeft ? cat.leftName : cat.rightName;
    const winText = document.createElement('div');
    winText.innerHTML = `<span style="font-size:18px;letter-spacing:8px;opacity:0.5;display:block;margin-bottom:8px">RONDA ${roundNumber}</span>${teamName}`;
    winText.style.cssText = `
        position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        font-family: 'Inter', sans-serif;
        font-size: 52px; font-weight: 900; letter-spacing: 2px;
        color: white; pointer-events: none; z-index: 85;
        text-align: center; line-height: 1.3;
        white-space: nowrap;
    `;
    tiktokFrame.appendChild(winText);
    winText.animate([
        { opacity: 0, transform: 'translate(-50%, -50%) translateY(10px)' },
        { opacity: 1, transform: 'translate(-50%, -50%) translateY(0)', offset: 0.15 },
        { opacity: 1, transform: 'translate(-50%, -50%) translateY(0)', offset: 0.75 },
        { opacity: 0, transform: 'translate(-50%, -50%) translateY(-10px)' }
    ], { duration: 2500, easing: 'ease-in-out', fill: 'forwards' });
    setTimeout(() => winText.remove(), 2500);

    // Score underneath
    const scoreText = document.createElement('div');
    scoreText.textContent = `${globalWins.left} — ${globalWins.right}`;
    scoreText.style.cssText = `
        position: absolute; top: calc(50% + 50px); left: 50%;
        transform: translate(-50%, 0);
        font-family: 'Bebas Neue', sans-serif;
        font-size: 36px; letter-spacing: 6px;
        color: rgba(255,255,255,0.4); pointer-events: none; z-index: 85;
    `;
    tiktokFrame.appendChild(scoreText);
    scoreText.animate([
        { opacity: 0 },
        { opacity: 1, offset: 0.2 },
        { opacity: 1, offset: 0.75 },
        { opacity: 0 }
    ], { duration: 2500, easing: 'ease-in-out', fill: 'forwards' });
    setTimeout(() => scoreText.remove(), 2500);

    // Small color accent line under the text
    const accent = document.createElement('div');
    accent.style.cssText = `
        position: absolute; top: calc(50% + 32px); left: 50%;
        transform: translateX(-50%); width: 0; height: 2px;
        background: ${color}; z-index: 85; pointer-events: none;
    `;
    tiktokFrame.appendChild(accent);
    accent.animate([
        { width: '0px' },
        { width: '200px', offset: 0.15 },
        { width: '200px', offset: 0.75 },
        { width: '0px' }
    ], { duration: 2500, easing: 'ease-in-out', fill: 'forwards' });
    setTimeout(() => accent.remove(), 2500);

    // Check for glory moment
    if (globalWins[winner] >= GLORY_ROUNDS) {
        setTimeout(() => {
            triggerGloryMoment(winner);
        }, 2800);
    } else {
        // Quick next round
        setTimeout(() => {
            nextRound();
        }, AUTO_RESTART_DELAY);
    }
}

function endByTimer() {
    if (gameOver) return;
    if (leftPoints > rightPoints) {
        endGame('left');
    } else if (rightPoints > leftPoints) {
        endGame('right');
    } else {
        // Tie - extend 30s
        timeLeft = 30;
        timerEl.textContent = '0:30';
        timerEl.classList.add('urgent');
        screenShake(10);

        playTTS('empate', null, true);
        // Flash "EMPATE - TIEMPO EXTRA"
        const tie = document.createElement('div');
        tie.className = 'combo-text pop-in';
        tie.textContent = 'EMPATE!';
        tie.style.color = '#ffffff';
        tie.style.textShadow = '0 0 30px rgba(255,255,255,0.8)';
        tie.style.left = '35%';
        tie.style.top = '30%';
        tie.style.fontSize = '48px';
        arena.appendChild(tie);
        setTimeout(() => tie.remove(), 1200);
    }
}

// ─── ROUNDS ───
function nextRound() {
    roundNumber++;
    startRound();
}

function showCountdown() {
    const cat = CATEGORIES[currentCategory];
    const overlay = countdownOverlay;
    const numEl = cdNumber;
    const catEl = cdCategory;

    cdLabel.textContent = 'SIGUIENTE RONDA';
    catEl.textContent = cat.title;
    catEl.style.background = `linear-gradient(90deg, ${cat.leftColor}, #fff, ${cat.rightColor})`;
    catEl.style.webkitBackgroundClip = 'text';
    catEl.style.webkitTextFillColor = 'transparent';
    catEl.style.backgroundClip = 'text';

    overlay.classList.add('show');

    // Show category first
    catEl.classList.add('show');

    let count = COUNTDOWN_DURATION;

    function tick() {
        numEl.textContent = count > 0 ? count : 'GO!';
        numEl.classList.remove('pop');
        void numEl.offsetWidth;
        numEl.classList.add('pop');

        if (count > 0) {
            sfxCountdownTick();
            count--;
            setTimeout(tick, 700);
        } else {
            sfxCountdownGo();
            setTimeout(() => {
                overlay.classList.remove('show');
                catEl.classList.remove('show');
                startRound();
            }, 400);
        }
    }

    setTimeout(tick, 500);
}

function startRound() {
    const cat = CATEGORIES[currentCategory];

    // TTS round start + battle music
    playTTSRandom('round_start', null, true);
    startBattleMusic();

    leftPoints = 0;
    rightPoints = 0;
    gameOver = false;
    timeLeft = ROUND_SECONDS;
    // Reset independent streaks and flames
    for (const team of ['men', 'women']) {
        clearTimeout(streaks[team].decayTimer);
        streaks[team].count = 0;
        streaks[team].lastTime = 0;
        flameTargetIntensity[team] = 0;
        flameIntensity[team] = 0;
    }
    flameParticlesLeft.length = 0;
    flameParticlesRight.length = 0;

    // Clean persistent combos
    hidePersistentCombo(true);
    hidePersistentCombo(false);

    // Reset comeback / danger / tension
    prevRatio = 0.5;
    comebackShown = { men: false, women: false };
    charLeft.classList.remove('in-danger');
    charRight.classList.remove('in-danger');
    leftDangerActive = false;
    rightDangerActive = false;
    dangerSoundPlaying = false;
    stopTension();

    timerEl.classList.remove('urgent');
    edgeLeft.classList.remove('active');
    edgeRight.classList.remove('active');

    // Update UI for new category
    categoryLabel.textContent = cat.label;
    roundTitle.textContent = cat.title;
    roundTitle.style.background = `linear-gradient(90deg, ${cat.leftColor}, #ffffff, ${cat.rightColor})`;
    roundTitle.style.webkitBackgroundClip = 'text';
    roundTitle.style.webkitTextFillColor = 'transparent';
    roundTitle.style.backgroundClip = 'text';
    roundCounterEl.textContent = `Ronda ${roundNumber}`;

    charLeft.textContent = cat.left;
    charRight.textContent = cat.right;
    charLeft.style.filter = `drop-shadow(0 0 25px ${cat.leftColor}66)`;
    charRight.style.filter = `drop-shadow(0 0 25px ${cat.rightColor}66)`;

    leftGlow.style.background = `radial-gradient(circle, ${cat.leftColor}, transparent 70%)`;
    rightGlow.style.background = `radial-gradient(circle, ${cat.rightColor}, transparent 70%)`;

    leftBar.style.background = `linear-gradient(90deg, ${cat.leftColor}99, ${cat.leftColor})`;
    rightBar.style.background = `linear-gradient(90deg, ${cat.rightColor}, ${cat.rightColor}99)`;

    document.querySelectorAll('.labels .men-label')[0].textContent = cat.leftName;
    document.querySelectorAll('.labels .men-label')[0].style.color = cat.leftColor;
    document.querySelectorAll('.labels .women-label')[0].textContent = cat.rightName;
    document.querySelectorAll('.labels .women-label')[0].style.color = cat.rightColor;

    edgeLeft.style.background = `linear-gradient(90deg, ${cat.leftColor}66, transparent)`;
    edgeRight.style.background = `linear-gradient(-90deg, ${cat.rightColor}66, transparent)`;

    // Update gift button colors
    document.querySelectorAll('.men .gift-btn').forEach(btn => {
        btn.style.background = `linear-gradient(135deg, ${cat.leftColor}99, ${cat.leftColor})`;
        btn.style.boxShadow = `0 4px 15px ${cat.leftColor}44`;
    });
    document.querySelectorAll('.women .gift-btn').forEach(btn => {
        btn.style.background = `linear-gradient(135deg, ${cat.rightColor}99, ${cat.rightColor})`;
        btn.style.boxShadow = `0 4px 15px ${cat.rightColor}44`;
    });

    document.querySelectorAll('.men h3')[0].style.color = cat.leftColor;
    document.querySelectorAll('.women h3')[0].style.color = cat.rightColor;

    // Remove old confetti
    document.querySelectorAll('.confetti').forEach(c => c.remove());

    updateVisuals();
    startTimer();
}

// ─── TIMER ───
function startTimer() {
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        if (gameOver) return;
        timeLeft--;

        if (timeLeft <= 30) {
            timerEl.classList.add('urgent');
            startTension();
        }
        if (timeLeft <= 10 && timeLeft > 0) sfxTimerTick();
        if (timeLeft === 10) playTTS('tension_10s', null, true);

        const min = Math.floor(timeLeft / 60);
        const sec = timeLeft % 60;
        timerEl.textContent = `${min}:${sec.toString().padStart(2, '0')}`;

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            endByTimer();
        }
    }, 1000);
}

// ─── CONFETTI ───
function spawnConfetti(color) {
    const colors = [color, '#ffffff', '#ffdd44', '#44ffaa', color];
    for (let i = 0; i < 80; i++) {
        setTimeout(() => {
            const c = document.createElement('div');
            c.className = 'confetti';
            c.style.left = Math.random() * 100 + 'vw';
            c.style.background = colors[Math.floor(Math.random() * colors.length)];
            c.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
            const size = 4 + Math.random() * 12;
            c.style.width = size + 'px';
            c.style.height = size + 'px';
            c.style.opacity = '0.8';

            const duration = 2.5 + Math.random() * 3;
            const sway = (Math.random() - 0.5) * 200;
            c.animate([
                { top: '-20px', transform: `translateX(0) rotate(0deg)`, opacity: 1 },
                { top: '110vh', transform: `translateX(${sway}px) rotate(${360 + Math.random() * 720}deg)`, opacity: 0 }
            ], { duration: duration * 1000, easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)', fill: 'forwards' });

            tiktokFrame.appendChild(c);
            setTimeout(() => c.remove(), duration * 1000);
        }, i * 40);
    }
}

// ─── KEYBOARD SHORTCUTS ───
document.addEventListener('keydown', (e) => {
    if (gameOver) return;
    switch(e.key) {
        case '1': donate('men', 1); break;
        case '2': donate('men', 5); break;
        case '3': donate('men', 10); break;
        case '8': donate('women', 1); break;
        case '9': donate('women', 5); break;
        case '0': donate('women', 10); break;
    }
});

// ─── SCOREBOARD ───
const sbLeftPips = document.getElementById('sbLeftPips');
const sbRightPips = document.getElementById('sbRightPips');
const sbLeftWins = document.getElementById('sbLeftWins');
const sbRightWins = document.getElementById('sbRightWins');
const sbLeftSeries = document.getElementById('sbLeftSeries');
const sbRightSeries = document.getElementById('sbRightSeries');
const gloryOverlay = document.getElementById('gloryOverlay');
const gloryEmoji = document.getElementById('gloryEmoji');
const gloryTeam = document.getElementById('gloryTeam');
const glorySeries = document.getElementById('glorySeries');

function initScoreboard() {
    const cat = CATEGORIES[currentCategory];
    sbLeftPips.innerHTML = '';
    sbRightPips.innerHTML = '';
    for (let i = 0; i < GLORY_ROUNDS; i++) {
        const pl = document.createElement('div');
        pl.className = 'sb-pip';
        sbLeftPips.appendChild(pl);
        const pr = document.createElement('div');
        pr.className = 'sb-pip';
        sbRightPips.appendChild(pr);
    }
    updateScoreboard();
}

function updateScoreboard() {
    const cat = CATEGORIES[currentCategory];

    sbLeftWins.textContent = globalWins.left;
    sbLeftWins.style.color = cat.leftColor;
    sbRightWins.textContent = globalWins.right;
    sbRightWins.style.color = cat.rightColor;

    // Update pips
    const leftPips = sbLeftPips.querySelectorAll('.sb-pip');
    const rightPips = sbRightPips.querySelectorAll('.sb-pip');

    leftPips.forEach((pip, i) => {
        const shouldFill = i < globalWins.left;
        const wasFilled = pip.classList.contains('filled');
        pip.classList.toggle('filled', shouldFill);
        if (shouldFill) {
            pip.style.background = cat.leftColor;
            pip.style.boxShadow = `0 0 8px ${cat.leftColor}`;
            if (!wasFilled) {
                pip.classList.remove('just-filled');
                void pip.offsetWidth;
                pip.classList.add('just-filled');
            }
        } else {
            pip.style.background = 'transparent';
            pip.style.boxShadow = 'none';
        }
    });

    rightPips.forEach((pip, i) => {
        const shouldFill = i < globalWins.right;
        const wasFilled = pip.classList.contains('filled');
        pip.classList.toggle('filled', shouldFill);
        if (shouldFill) {
            pip.style.background = cat.rightColor;
            pip.style.boxShadow = `0 0 8px ${cat.rightColor}`;
            if (!wasFilled) {
                pip.classList.remove('just-filled');
                void pip.offsetWidth;
                pip.classList.add('just-filled');
            }
        } else {
            pip.style.background = 'transparent';
            pip.style.boxShadow = 'none';
        }
    });

    // Series trophies
    sbLeftSeries.textContent = seriesWins.left > 0 ? '🏆'.repeat(seriesWins.left) : '';
    sbRightSeries.textContent = seriesWins.right > 0 ? '🏆'.repeat(seriesWins.right) : '';
}

// ─── GLORY MOMENT ───
function sfxGlory() {
    const now = audioCtx.currentTime;

    // Epic fanfare - bigger than victory
    playTone(40, 'sine', 1, 0.4, 0);
    playTone(60, 'sine', 0.8, 0.3, 0);

    // Rising sweep
    const sweep = audioCtx.createOscillator();
    const sg = audioCtx.createGain();
    sweep.type = 'sawtooth';
    sweep.frequency.setValueAtTime(80, now);
    sweep.frequency.exponentialRampToValueAtTime(3000, now + 0.6);
    sg.gain.setValueAtTime(0.1, now);
    sg.gain.exponentialRampToValueAtTime(0.001, now + 0.65);
    sweep.connect(sg); sg.connect(masterGain);
    sweep.start(now); sweep.stop(now + 0.65);

    // Grand major chord staggered
    [130, 165, 196, 262, 330, 392, 524, 660, 784, 1048].forEach((f, i) => {
        setTimeout(() => {
            playTone(f, 'triangle', 0.8, 0.08, 0);
            playTone(f, 'sine', 0.6, 0.05, 0);
        }, i * 50);
    });

    // Massive cymbal
    setTimeout(() => playNoise(2, 0.15, 10000, 0), 300);

    // Sub boom at climax
    setTimeout(() => {
        playTone(30, 'sine', 1, 0.4, 0);
        playNoise(0.6, 0.2, 2000, 0);
    }, 500);

    // Sparkle cascade
    for (let i = 0; i < 15; i++) {
        setTimeout(() => playTone(1000 + Math.random() * 3000, 'sine', 0.15, 0.04, Math.random() * 2 - 1), 700 + i * 70);
    }

    // Second fanfare hit
    setTimeout(() => {
        [262, 330, 392, 524].forEach(f => playTone(f, 'triangle', 0.6, 0.1, 0));
        playNoise(1, 0.1, 8000, 0);
    }, 1200);
}

function triggerGloryMoment(winner) {
    gloryActive = true;
    const cat = CATEGORIES[currentCategory];
    const isLeft = winner === 'left';
    const color = isLeft ? cat.leftColor : cat.rightColor;

    // Update series
    if (isLeft) seriesWins.left++;
    else seriesWins.right++;

    // White flash
    const gloryFlash = document.getElementById('gloryFlash');
    gloryFlash.classList.remove('fire');
    void gloryFlash.offsetWidth;
    gloryFlash.classList.add('fire');

    // Set glory content
    const gloryBg = document.getElementById('gloryBg');
    gloryBg.style.background = `radial-gradient(ellipse at center, ${color}dd, ${color}88 40%, #000000ee 80%)`;

    gloryEmoji.textContent = isLeft ? cat.left : cat.right;
    gloryTeam.textContent = (isLeft ? cat.leftName : cat.rightName);
    gloryTeam.style.color = '#ffffff';
    gloryTeam.style.textShadow = `0 0 30px ${color}, 0 0 60px ${color}`;

    const totalSeries = seriesWins.left + seriesWins.right;
    const trophyCount = isLeft ? seriesWins.left : seriesWins.right;
    document.getElementById('gloryTrophies').textContent = '🏆'.repeat(trophyCount);
    glorySeries.textContent = `${cat.leftName} ${seriesWins.left} vs ${seriesWins.right} ${cat.rightName}`;

    gloryOverlay.classList.add('show');
    sfxGlory();
    stopBattleMusic();
    stopDrumRoll();
    playSFX('glory_anthem', 0.6);
    playTTSRandom('glory', isLeft ? 'male' : 'female', true);

    // Screen shake repeatedly
    screenShake(60);
    setTimeout(() => screenShake(40), 500);
    setTimeout(() => screenShake(30), 1000);

    // Massive gold confetti waves
    spawnConfetti('#ffd700');
    setTimeout(() => spawnConfetti(color), 400);
    setTimeout(() => spawnConfetti('#ffd700'), 800);
    setTimeout(() => spawnConfetti(color), 1200);
    setTimeout(() => spawnConfetti('#ffffff'), 1600);

    // Particle explosions staggered
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            const x = canvas.width * (0.2 + Math.random() * 0.6);
            const y = canvas.height * (0.2 + Math.random() * 0.6);
            spawnParticleBurst(x, y, i % 2 === 0 ? '#ffd700' : color, 40, 8);
        }, i * 300);
    }

    // Trophy rain
    for (let i = 0; i < 30; i++) {
        setTimeout(() => {
            const t = document.createElement('div');
            t.className = 'trophy-rain';
            t.textContent = ['🏆', '👑', '⭐', '🥇'][Math.floor(Math.random() * 4)];
            t.style.left = Math.random() * 100 + 'vw';
            t.style.fontSize = (20 + Math.random() * 30) + 'px';
            const dur = 2 + Math.random() * 2;
            const sway = (Math.random() - 0.5) * 150;
            t.animate([
                { top: '-40px', transform: `translateX(0) rotate(0deg)`, opacity: 1 },
                { top: '110vh', transform: `translateX(${sway}px) rotate(${360 + Math.random() * 360}deg)`, opacity: 0.6 }
            ], { duration: dur * 1000, easing: 'ease-in', fill: 'forwards' });
            tiktokFrame.appendChild(t);
            setTimeout(() => t.remove(), dur * 1000);
        }, i * 100);
    }

    // Lightning flashes
    setTimeout(() => spawnLightning('#ffd700'), 200);
    setTimeout(() => spawnLightning(color), 500);
    setTimeout(() => spawnLightning('#ffffff'), 800);

    // Auto reset after glory
    setTimeout(() => {
        gloryOverlay.classList.remove('show');
        globalWins = { left: 0, right: 0 };
        gloryActive = false;
        updateScoreboard();
        startRound();
    }, GLORY_DELAY);
}

// ─── INIT ───
initScoreboard();

// Start screen - required for audio unlock
const startScreen = document.createElement('div');
startScreen.style.cssText = `
    position: absolute; inset: 0; z-index: 999;
    background: radial-gradient(ellipse at center, #0f1028, #050510);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    cursor: pointer;
`;
const cat = CATEGORIES[currentCategory];
startScreen.innerHTML = `
    <div style="font-size:80px;margin-bottom:15px">${cat.left}⚔️${cat.right}</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:60px;letter-spacing:5px;
        background:linear-gradient(90deg,${cat.leftColor},#fff,${cat.rightColor});
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">
        ${cat.title}
    </div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:8px;
        color:rgba(255,255,255,0.3);margin-top:20px">TUG OF WAR</div>
    <div style="font-size:16px;color:rgba(255,255,255,0.15);margin-top:40px;
        letter-spacing:3px;animation:pulse 1.5s ease-in-out infinite alternate">
        CLICK PARA COMENZAR
    </div>
`;
tiktokFrame.appendChild(startScreen);

function startGame() {
    startScreen.remove();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    audioUnlocked = true;
    startRound();
}

startScreen.addEventListener('click', startGame);
document.addEventListener('keydown', function initKey(e) {
    if (startScreen.parentNode) {
        startGame();
        document.removeEventListener('keydown', initKey);
    }
});

// ─── SSE: RECIBIR EVENTOS DE TIKTOK LIVE ───
(function connectSSE() {
    const evtSource = new EventSource('/tugofwar/events/');

    evtSource.onmessage = function(event) {
        try {
            const evt = JSON.parse(event.data);
            if (evt.type === 'donation' && evt.data) {
                const d = evt.data;
                // Auto-start game if start screen is still showing
                if (startScreen.parentNode) startGame();
                donate(d.team, d.amount, d.username);
            }
        } catch (e) {
            console.error('[SSE] Error parsing event:', e);
        }
    };

    evtSource.onerror = function() {
        console.warn('[SSE] Connection lost, reconnecting in 3s...');
        evtSource.close();
        setTimeout(connectSSE, 3000);
    };
})();
