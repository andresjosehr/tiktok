import {
  getCustomProperty,
  incrementCustomProperty,
  setCustomProperty,
} from "./updateCustomProperty.js"

const SPEED = 0.02 // Slower than ground for parallax effect
const cloudElems = document.querySelectorAll("[data-cloud]")

function randomNumberBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min)
}

export function setupCloud() {
  cloudElems.forEach((cloud, index) => {
    const leftPos = index * 40 + randomNumberBetween(0, 30)
    const topPos = randomNumberBetween(5, 25)
    setCustomProperty(cloud, "--left", leftPos)
    setCustomProperty(cloud, "--top", topPos)
  })
}

export function updateCloud(delta, speedScale) {
  cloudElems.forEach(cloud => {
    incrementCustomProperty(cloud, "--left", delta * speedScale * SPEED * -1)

    if (getCustomProperty(cloud, "--left") <= -20) {
      const newLeft = 200 + randomNumberBetween(0, 50)
      const newTop = randomNumberBetween(5, 25)
      setCustomProperty(cloud, "--left", newLeft)
      setCustomProperty(cloud, "--top", newTop)
    }
  })
}
