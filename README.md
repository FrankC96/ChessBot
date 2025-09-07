
# CHESS AI

---
In this repository I am using chess as an example for the minimax alpha-beta pruning algorithm.
I am using HTML to print/align the board where the board pieces are displayed as unicode characters.

# Deployment

---

At first, I was going to fully visualize the board in the terminal. But I came across some 
board/pieces alignment issues due to the font of each terminal. It seems that different 
terminals render the same character differently. For example this pawn &#2659; character 
is rendered differently than the empty square character &#2022;. The solution was to deploy 
and render with streamlit to a user-friendly browser.

# TODO:

---

- Add king castling
- Add pawn promotion
- Add human player

# Docs:

---
To build the documentation with mkdocs run `mkdocs serve` in the project directory.