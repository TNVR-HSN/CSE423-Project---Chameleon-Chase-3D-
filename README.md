# Chameleon Chase 3D

## Game Overview

**Chameleon Chase 3D** is a multiplayer hide-and-seek style game developed using PyOpenGL and GLUT. Players can take the role of either a **Hunter** or a **Prop**. Props can disguise themselves as objects in the environment to avoid detection, while Hunters attempt to locate and tag them. The game emphasizes stealth, strategy, and quick reflexes, with special abilities added to make gameplay dynamic and engaging.

A third-person camera provides a clear view of the environment, allowing Props to blend seamlessly into the world and Hunters to track their targets efficiently. The game features multiple rounds, score tracking, and environmental interactions for immersive gameplay.

---

## Core Gameplay Features

### Player Control

- Two roles: **Hunter** and **Prop**, each with distinct abilities and controls  
- Hunters move using **W, A, S, D** and can dash with **E** to quickly close distance or evade hazards  
- Props move using **W, A, S, D** and can rotate freely to align with objects in the environment  
- Props can become temporarily invisible using **Middle Mouse** to avoid detection  
- Props can spawn decoys using **Right Mouse / Q** to distract Hunters  
- Smooth movement animations for both roles, including idle, walking, and ability activation  
- All player actions update in real time, including collision responses and ability cooldowns  

---

### Platforms & Environment

- Multiple platform areas with varied elevation, obstacles, and interactive objects  
- Grid-based floor forming the base of the arena with clearly defined boundaries  
- Props can transform into environmental objects such as crates, barrels, or furniture  
- Hunters navigate platforms using standard movement and dash ability  
- Falling off platforms or leaving boundaries resets the player to their spawn location  
- Environmental hazards like moving walls and rotating platforms increase challenge  
- Visual cues such as floor color changes and object highlights help player orientation  

---

### Abilities & Interactions

- **Dash (Hunter):** Short burst of speed for closing gaps or evading danger  
- **Invisibility (Prop):** Temporarily hides the Prop from Hunters  
- **Decoy (Prop):** Spawns a fake object to mislead Hunters  
- **Ping (Prop):** Briefly highlights nearby Props to support team coordination  
- **Collision Mechanics:** Detects interactions with platforms, objects, and players  
- **Score Tracking:**  
  - Props earn points by surviving rounds  
  - Hunters earn points by tagging Props  

---

## Camera System

- Third-person camera smoothly follows the player  
- Camera rotation controlled with **LEFT / RIGHT arrow keys**  
- Camera height adjustable using **UP / DOWN arrow keys**  
- Automatic orientation toward player movement while maintaining depth perception  
- Enables Props to align naturally with objects  
- Allows Hunters to track movement efficiently  

---

## Game Mechanics

- Hide-and-seek gameplay with defined round timers and win conditions  
- Hunters detect Props within a specific radius, triggering tag events  
- Props rely on abilities like invisibility and decoys to evade detection  
- Ability cooldowns encourage strategic use  
- Environmental interactions require precise movement  
- Physics-based gameplay includes gravity and collision detection  
- Real-time game logic updates movement, abilities, and scoring  

---

## Visual & Technical Details

- Fully 3D environment rendered using Unity’s standard rendering pipeline  
- Player, Prop, and environment models created using primitives and custom textures  
- Object transformations handled through Unity’s **Transform** component  
- Smooth animations enhance immersion  
- HUD displays score, cooldowns, timers, and round results  
- Optimized for real-time multiplayer performance with minimal lag  
