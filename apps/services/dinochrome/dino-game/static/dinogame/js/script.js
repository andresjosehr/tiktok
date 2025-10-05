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

setPixelToWorldScale()
window.addEventListener("resize", setPixelToWorldScale)

// Iniciar juego automáticamente después de la animación de revelación
setTimeout(() => {
  handleStart()
}, 3000)

let lastTime
let speedScale
let score
function update(time) {
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
  scoreElem.textContent = Math.floor(score)
}

function handleStart() {
  lastTime = null
  speedScale = 1.5
  score = 0
  setupCloud()
  setupGround()
  setupDino()
  setupCactus()
  window.requestAnimationFrame(update)
}

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
