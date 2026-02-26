# Quantum Tic-Tac-Toe

A quantum twist on the classic Tic-Tac-Toe, built with **Python**, **Qiskit**, and **Streamlit**.  
Each move places a piece in **quantum superposition** across N cells simultaneously. Pieces only collapse to a definite position when entanglement cycles or saturation thresholds are reached or when the board is full (depending on the settings), simulated on a real 9-qubit quantum circuit.

---

## Features

- **Quantum superposition mechanics** — each turn, a player places their mark across two cells at once via a Hadamard + CNOT gate sequence
- **Entanglement & collapse** — pieces collapse when saturation or entanglement cycles are detected, simulated via Qiskit Aer
- **4 AI algorithms** — Random baseline, Grover search heuristic, QAOA + Grover, and Quantum Minimax (alpha-beta pruning)
- **ELO tournament** — round-robin tournament between all 4 AIs with live ranking and ELO evolution graph
- **Live circuit visualization** — the quantum gate sequence updates in real time as moves are played
- **Customizable rules** — adjustable saturation threshold N, toggle saturation and cycle-based collapse
- **Player customization** — names, colors, and icons for each player

---

## Project Structure

```
├── app.py                  # Entry point — routing and global CSS
├── quantum_engine.py       # Core quantum logic (circuits, collapse, AI algorithms, ELO)
├── page_menu.py            # Main menu with panels
├── page_jeu_local.py       # Local 2-player game
├── page_jeu_ia.py          # Player vs AI
├── page_jeu_ia_vs_ia.py    # AI vs AI spectator mode
├── page_tournoi.py         # ELO round-robin tournament
├── page_infos.py           # Project documents (énoncé, rapport)
├── page_common.py          # Shared game utilities (move logic, history, win detection)
├── interface_game.py       # Grid rendering, cell states, winner banner
├── visualizer.py           # Move history display and quantum circuit rendering
├── retour.py               # Navigation bar (back button, reset)
├── styles.py               # Global CSS and menu button animations
├── enonce.pdf              
└── rapport.pdf             
```

---

## Getting Started

### Copy and paste this in the shell
```bash

git clone https://github.com/Gavide/Morpion-quantique.git
cd Morpion-quantique
python -m venv env #macOS / Linux: python -m venv env
.\env\Scripts\activate #macOS / Linux: source env/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

The app will open automatically at `http://localhost:8501`.


---

## Requirements

Main dependencies (see `requirements.txt` for full list):

| Package | Purpose |
|---|---|
| `streamlit` | Web interface |
| `qiskit` | Quantum circuit construction |
| `qiskit-aer` | Quantum simulation backend |
| `numpy` | Numerical computation |
| `pandas` | Data display (history, rankings) |
| `plotly` | ELO evolution graph |

---

## Game Rules

1. Each turn, a player selects **N cells** (default N=2) to place their mark in superposition
2. The mark exists simultaneously in all selected cells until collapse
3. **Collapse is triggered** when:
   - A cell accumulates N marks from the same player *(always enforced)*
   - A cell reaches N total marks from any players *(if saturation mode is on)*
   - An entanglement cycle is detected in the mark graph *(if cycle mode is on)*
4. On collapse, Qiskit simulates the circuit and each mark lands on one definite cell
5. **Win condition** — first to align 3 collapsed marks in a row, column, or diagonal

---

## AI Algorithms

| Algorithm | Description |
|---|---|
| **Random** | Picks a valid pair of cells at random |
| **Grover** | Uses a Grover-inspired amplitude amplification over a heuristic scoring function |
| **QAOA** | QAOA evaluates cell quality; Grover selects the best pair |
| **Minimax Q** | Quantum-adapted minimax with alpha-beta pruning over superposition states |
