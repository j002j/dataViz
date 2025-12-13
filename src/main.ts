// Alles aus src/ wird nicht direkt im HTML verlinkt, sondern immer über den Entry hier 
import './styles/main.css'
import { basicSetUp } from './graph/initGraph'

document.addEventListener('DOMContentLoaded', () => {
    const { div } = basicSetUp()
    document.body.appendChild(div)
})