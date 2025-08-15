import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from streamlit_drawable_canvas import st_canvas
from PIL import Image

# ====== Config ======
NOTES_FILE = Path("notes.csv")
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Notebook App", page_icon="📓", layout="wide")
st.title("Notebook App")

# ====== Load Notes ======
if "notes" not in st.session_state:
    if NOTES_FILE.exists():
        notes_df = pd.read_csv(NOTES_FILE)
        st.session_state.notes = notes_df["note"].tolist()
    else:
        st.session_state.notes = []

# ====== Save Notes ======
def save_notes():
    pd.DataFrame({"note": st.session_state.notes}).to_csv(NOTES_FILE, index=False)

# ====== Add Text Note ======
st.subheader("✍️ Add a Text Note")
text_col, btn_col = st.columns([4, 1])
with text_col:
    note_text = st.text_area("Write your note:", key="new_note")
with btn_col:
    if st.button("💾 Save Note"):
        if note_text.strip():
            st.session_state.notes.append(note_text.strip())
            save_notes()
            st.session_state.new_note = ""
            st.rerun()

# ====== Drawing Canvas ======
st.subheader("🎨 Drawing Board")

# Pick pen color and thickness
pen_color = st.color_picker("Pick a pen color", "#000000")
pen_width = st.slider("Pen width", 1, 20, 3)

# Canvas component
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 1)",  # Background fill
    stroke_width=pen_width,               # Variable thickness
    stroke_color=pen_color,               # Color from picker
    background_color="#ffffff",
    height=300,
    drawing_mode="freedraw",
    key="canvas",
)

# Save drawing
if st.button("💾 Save Drawing"):
    if canvas_result.image_data is not None:
        img = Image.fromarray((canvas_result.image_data).astype("uint8"), "RGBA")
        filename = IMAGES_DIR / f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        st.success(f"Drawing saved as {filename.name}")

# ====== Show Notes with Delete ======
st.subheader("📝 Your Notes")
if st.session_state.notes:
    for idx, note in enumerate(st.session_state.notes):
        col1, col2 = st.columns([8, 1])
        col1.markdown(f"**{idx+1}.** {note}")
        if col2.button("❌", key=f"delete_note_{idx}"):
            st.session_state.notes.pop(idx)
            save_notes()
            st.rerun()
else:
    st.info("No notes yet.")

# ====== Show Saved Images with Delete ======
st.subheader("🖼️ Saved Drawings")
image_files = sorted(IMAGES_DIR.glob("*.png"), reverse=True)
if image_files:
    for img_path in image_files:
        col1, col2 = st.columns([8, 1])
        col1.image(str(img_path), use_container_width=True)
        if col2.button("🗑️", key=f"delete_img_{img_path}"):
            img_path.unlink()
            st.rerun()
else:
    st.info("No drawings saved yet.")
