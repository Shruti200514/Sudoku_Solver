import streamlit as st
import random

#  1. THEME: CYBER-CHALKBOARD 
st.set_page_config(page_title="Sudoku Solver Pro", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        background-image: radial-gradient(#1f2937 1px, transparent 1px);
        background-size: 30px 30px;
    }
    /* Cell Button Styling */
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 22px !important;
        font-weight: 800;
        background-color: #161b22;
        color: #00f2ff;
        border: 2px solid #30363d;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        border-color: #00f2ff;
        box-shadow: 0 0 15px #00f2ff;
    }
    /* Locked/Fixed Cell Styling */
    div.stButton > button:disabled {
        background-color: #0d1117 !important;
        color: #ffffff !important;
        border: 2px solid #21262d !important;
        opacity: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BACKEND: THE ALGORITHMIC CORE 
class SudokuEngine:
    """
    Handles Sudoku validation, recursive backtracking solving, 
    and procedural puzzle generation.
    """
    @staticmethod
    def is_valid(board, r, c, n, size):
        for i in range(size):
            if board[r][i] == n or board[i][c] == n: return False
        b_s = int(size**0.5)
        rs, cs = b_s * (r // b_s), b_s * (c // b_s)
        for i in range(b_s):
            for j in range(b_s):
                if board[rs + i][cs + j] == n: return False
        return True

    @staticmethod
    def solve(board, size):
        """Recursive Backtracking (DFS) Implementation"""
        for r in range(size):
            for c in range(size):
                if board[r][c] == 0:
                    nums = list(range(1, size + 1))
                    random.shuffle(nums)
                    for n in nums:
                        if SudokuEngine.is_valid(board, r, c, n, size):
                            board[r][c] = n
                            if SudokuEngine.solve(board, size): return True
                            board[r][c] = 0
                    return False
        return True

    @staticmethod
    def generate_puzzle(size, diff):
        """Generates a solvable board and stores the solution key"""
        board = [[0]*size for _ in range(size)]
        SudokuEngine.solve(board, size)
        solution = [row[:] for row in board]
        
        # Difficulty scaling
        ratios = {"Easy": 0.35, "Medium": 0.55, "Hard": 0.72}
        removals = int((size * size) * ratios[diff])
        while removals > 0:
            r, c = random.randint(0, size-1), random.randint(0, size-1)
            if board[r][c] != 0:
                board[r][c] = 0
                removals -= 1
        return board, solution

# 3. STATE MANAGEMENT 
if 'size' not in st.session_state: st.session_state.size = 4
if 'diff' not in st.session_state: st.session_state.diff = "Easy"
if 'board' not in st.session_state:
    b, s = SudokuEngine.generate_puzzle(4, "Easy")
    st.session_state.board, st.session_state.sol, st.session_state.orig = b, s, [r[:] for r in b]
if 'mistakes' not in st.session_state: st.session_state.mistakes = []
if 'game_over' not in st.session_state: st.session_state.game_over = False

#  4. SIDEBAR & FEATURES 
st.sidebar.title("🎮 Sudoku Solver Pro")
st.sidebar.markdown("---")

# Feature: Grid Level Toggle
level = st.sidebar.radio("Grid Size", [4, 9], horizontal=True, format_func=lambda x: f"{x}x{x}")

# Feature: Difficulty Selector
difficulty = st.sidebar.select_slider("Level", ["Easy", "Medium", "Hard"], value=st.session_state.diff)

# Reset logic for setting changes
if level != st.session_state.size or difficulty != st.session_state.diff:
    st.session_state.size, st.session_state.diff = level, difficulty
    b, s = SudokuEngine.generate_puzzle(level, difficulty)
    st.session_state.board, st.session_state.sol, st.session_state.orig = b, s, [r[:] for r in b]
    st.session_state.mistakes, st.session_state.game_over = [], False
    st.rerun()

if st.sidebar.button("✨ New Game"):
    b, s = SudokuEngine.generate_puzzle(st.session_state.size, st.session_state.diff)
    st.session_state.board, st.session_state.sol, st.session_state.orig = b, s, [r[:] for r in b]
    st.session_state.mistakes, st.session_state.game_over = [], False
    st.rerun()

#  5. RESULT & VALIDATION UI 
st.title("Sudoku Solver")
sz = st.session_state.size

if st.sidebar.button("🔍 Check Solution"):
    mistakes = []
    for r in range(sz):
        for c in range(sz):
            val = st.session_state.board[r][c]
            if val != 0 and val != st.session_state.sol[r][c]:
                mistakes.append((r, c))
    
    st.session_state.mistakes = mistakes
    
    # Check if complete and correct
    is_filled = all(val != 0 for row in st.session_state.board for val in row)
    if is_filled and not mistakes:
        st.balloons()
        st.success("### 🎉 CONGRATS! You solved it correctly!")
        st.session_state.game_over = True
    elif mistakes:
        st.error(f"### ⚠️ Opps! Found {len(mistakes)} errors. Check the red boxes!")
    else:
        st.info("Looking good! Keep filling those empty cells.")

#  6. THE INTERACTIVE GRID 
col_cfg = [1, 2, 1] if sz == 4 else [1, 5, 1]
_, grid_col, _ = st.columns(col_cfg)

with grid_col:
    for r in range(sz):
        cols = st.columns(sz)
        for c in range(sz):
            val = st.session_state.board[r][c]
            is_fixed = st.session_state.orig[r][c] != 0
            label = str(val) if val != 0 else ""
            
            # Error Highlight Styling
            if (r, c) in st.session_state.mistakes:
                st.markdown(f"<style>button[key='cell-{r}-{c}'] {{ border: 2px solid #ff4b4b !important; color: #ff4b4b !important; }}</style>", unsafe_allow_html=True)

            if cols[c].button(label, key=f"cell-{r}-{c}", disabled=is_fixed or st.session_state.game_over):
                st.session_state.board[r][c] = (val + 1) % (sz + 1)
                if (r, c) in st.session_state.mistakes: st.session_state.mistakes.remove((r, c))
                st.rerun()

#  7. COMPARISON / REVEAL FEATURE 
if st.session_state.mistakes or st.sidebar.button("💡 Reveal AI Solution"):
    st.divider()
    st.subheader("🕵️ Knowledge Base: AI Solution Comparison")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Your Progress**")
        st.table(st.session_state.board)
    with c2:
        st.write("**Target Solution**")
        st.table(st.session_state.sol)