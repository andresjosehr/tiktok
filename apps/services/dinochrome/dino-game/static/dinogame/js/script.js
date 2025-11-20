import { updateGround, setupGround } from "./ground.js"
import { updateDino, setupDino, getDinoRect, setDinoLose, triggerJump } from "./dino.js"
import { updateCactus, setupCactus, getCactusRects } from "./cactus.js"
import { updateCloud, setupCloud } from "./cloud.js"

const WORLD_WIDTH = 100
const WORLD_HEIGHT = 30
const SPEED_SCALE_INCREASE = 0.00002
const AUTO_JUMP_DISTANCE = 150

const worldElem = document.querySelector("[data-world]")
const scoreElem = document.querySelector("[data-score]")
const highScoreElem = document.querySelector("[data-high-score]")
const pointSound = document.getElementById('point-sound')

let highScore = localStorage.getItem('dinoHighScore') || 0
highScoreElem.textContent = Math.floor(highScore)
let lastPointMilestone = 0

setPixelToWorldScale()
window.addEventListener("resize", setPixelToWorldScale)

// Inicializar posiciones de elementos al cargar
setupCloud()
setupGround()
setupDino()

// Iniciar juego automáticamente después de la animación de revelación
setTimeout(() => {
  handleStart()
}, 3000)

let lastTime
let speedScale
let score
let isGameRunning = false
function update(time) {
  if (!isGameRunning) return

  if (lastTime == null) {
    lastTime = time
    window.requestAnimationFrame(update)
    return
  }
  const delta = time - lastTime

  updateCloud(delta, speedScale)
  updateGround(delta, speedScale)
  updateDino(delta, speedScale)
  updateCactus(delta, speedScale)
  // updateSpeedScale(delta) // Velocidad constante
  updateScore(delta)
  autoJump()
  // if (checkLose()) return handleLose() // Dinosaurio inmortal

  lastTime = time
  window.requestAnimationFrame(update)
}

function checkLose() {
  const dinoRect = getDinoRect()
  return getCactusRects().some(rect => isCollision(rect, dinoRect))
}

function isCollision(rect1, rect2) {
  return (
    rect1.left < rect2.right &&
    rect1.top < rect2.bottom &&
    rect1.right > rect2.left &&
    rect1.bottom > rect2.top
  )
}

function updateSpeedScale(delta) {
  speedScale += delta * SPEED_SCALE_INCREASE
}

function updateScore(delta) {
  score += delta * 0.01
  const currentScore = Math.floor(score)
  scoreElem.textContent = currentScore

  // Reproducir sonido cada 100 puntos
  const currentMilestone = Math.floor(currentScore / 100) * 100
  if (currentMilestone > lastPointMilestone && currentMilestone > 0) {
    if (pointSound) {
      pointSound.currentTime = 0
      pointSound.play().catch(e => console.log('Error reproduciendo sonido de puntos:', e))
    }
    lastPointMilestone = currentMilestone
  }

  if (currentScore > highScore) {
    highScore = currentScore
    highScoreElem.textContent = highScore
    localStorage.setItem('dinoHighScore', highScore)
  }
}

function handleStart() {
  lastTime = null
  speedScale = 1.5
  score = 0
  lastPointMilestone = 0
  isGameRunning = true
  setupCactus()
  window.requestAnimationFrame(update)
}

export function restartGame() {
  // DETENER el juego completamente
  isGameRunning = false
  lastTime = null
  speedScale = 0
  score = 0
  lastPointMilestone = 0
  scoreElem.textContent = 0

  // Limpiar cactus existentes
  document.querySelectorAll("[data-cactus]").forEach(cactus => {
    cactus.remove()
  })

  // Reiniciar posiciones
  setupCloud()
  setupGround()
  setupDino()

  // Crear y mostrar cortina de nuevo
  const curtain = document.createElement('div')
  curtain.className = 'restart-curtain'
  worldElem.appendChild(curtain)

  // Después de 2 segundos, animar la cortina
  setTimeout(() => {
    curtain.classList.add('reveal')
  }, 2000)

  // Después de 3 segundos (cuando termina la animación), iniciar el juego
  setTimeout(() => {
    isGameRunning = true
    speedScale = 1.5
    setupCactus()
    window.requestAnimationFrame(update)

    // Remover la cortina después de que termine la animación
    setTimeout(() => {
      curtain.remove()
    }, 1000)
  }, 3000)
}

// Hacer la función accesible globalmente
window.restartGame = restartGame

function autoJump() {
  const cactusRects = getCactusRects()
  const dinoRect = getDinoRect()

  cactusRects.forEach(cactusRect => {
    const distance = cactusRect.left - dinoRect.right
    if (distance > 0 && distance < AUTO_JUMP_DISTANCE) {
      triggerJump()
    }
  })
}

function setPixelToWorldScale() {
  let worldToPixelScale
  if (window.innerWidth / window.innerHeight < WORLD_WIDTH / WORLD_HEIGHT) {
    worldToPixelScale = window.innerWidth / WORLD_WIDTH
  } else {
    worldToPixelScale = window.innerHeight / WORLD_HEIGHT
  }

  worldElem.style.width = `${WORLD_WIDTH * worldToPixelScale}px`
  worldElem.style.height = `${WORLD_HEIGHT * worldToPixelScale}px`
}
