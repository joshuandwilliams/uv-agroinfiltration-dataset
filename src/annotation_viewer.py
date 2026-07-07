"""
Tools for viewing and saving CDA annotations overlaid on source agroinfiltration images.

Two entry points:
  view_annotations()         — interactive Tkinter viewer, mode='cda' or mode='raw'
  save_all_annotation_images() — headless batch export of annotated JPEGs
"""

import os
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import messagebox

import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageTk

SCORER_COLORS_TK = {1: "purple", 2: "white", 3: "blue"}
SCORER_COLORS_PIL = {1: (128, 0, 128), 2: (255, 255, 255), 3: (0, 0, 255)}
LABEL_GREY_TK = "gray70"
LABEL_GREY_PIL = (160, 160, 160)


def _draw_score_label_pil(draw, row, label_x, label_y, font, font_size):
    """Draw a [s1,s2,s3] label with per-scorer colours at (label_x, label_y)."""
    scores = [row[f"Score{i}"] for i in range(1, 4)]

    def char_width(text):
        try:
            return int(font.getlength(text))
        except AttributeError:
            return int(len(text) * font_size * 0.6)

    sequence = [("[", LABEL_GREY_PIL)]
    colors = [SCORER_COLORS_PIL[i] for i in range(1, 4)]
    for j, (score, color) in enumerate(zip(scores, colors, strict=False)):
        sequence.append((str(int(score)) if not pd.isna(score) else "-", color))
        if j < 2:
            sequence.append((",", LABEL_GREY_PIL))
    sequence.append(("]", LABEL_GREY_PIL))

    cursor = label_x
    for text, color in sequence:
        draw.text((cursor, label_y), text, fill=color, font=font)
        cursor += char_width(text)


def _draw_score_label_tk(canvas, row, label_x, label_y, tk_font_obj):
    """Draw a [s1,s2,s3] label with per-scorer colours at (label_x, label_y)."""
    scores = [row[f"Score{i}"] for i in range(1, 4)]

    sequence = [("[", LABEL_GREY_TK)]
    colors = [SCORER_COLORS_TK[i] for i in range(1, 4)]
    for j, (score, color) in enumerate(zip(scores, colors, strict=False)):
        sequence.append((str(int(score)) if not pd.isna(score) else "-", color))
        if j < 2:
            sequence.append((",", LABEL_GREY_TK))
    sequence.append(("]", LABEL_GREY_TK))

    cursor = label_x
    for text, color in sequence:
        canvas.create_text(
            cursor, label_y, text=text, fill=color, font=("Helvetica", "20", "bold"), anchor="nw"
        )
        cursor += tk_font_obj.measure(text)


def save_annotation_image(
    basename: str,
    rows: pd.DataFrame,
    raw_folder_path: str | Path,
    output_path: str | Path,
    skip_existing: bool = False,
) -> None:
    """
    Save a single annotated JPEG for a source agroinfiltration image.

    Opens Scorer1's copy of the image, draws all bounding boxes and score labels
    for every CDA in rows, and saves to output_path.

    Parameters
    ----------
    basename : str
        Source image filename (e.g. 'DSC_0103.TIF').
    rows : pd.DataFrame
        All annotation rows belonging to this basename.
    raw_folder_path : Union[str, Path]
        Folder containing scorer-specific subfolders on the shared drive.
    output_path : Union[str, Path]
        Destination path for the JPEG output.
    skip_existing : bool
        If True, skip saving if output_path already exists.
    """
    if skip_existing and Path(output_path).exists():
        return
    scorer = rows.iloc[0]["Scorer1"]
    raw_path = Path(raw_folder_path) / scorer / basename

    img = Image.open(raw_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Scale line width and font to match how the original Tkinter viewer looked.
    # The viewer displayed images at ~90% of screen width (~1440px), so full-resolution
    # equivalents are proportionally larger. img.width // 400 gives ~10px for a 4000px image.
    line_width = max(3, img.width // 200)
    font_size = max(40, img.width // 25)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except OSError:
        font = ImageFont.load_default()

    for _, row in rows.iterrows():
        top_y, left_x = [], None
        for i in range(1, 4):
            if pd.isna(row[f"X1_{i}"]):
                continue
            x1, x2 = sorted([int(row[f"X1_{i}"]), int(row[f"X2_{i}"])])
            y1, y2 = sorted([int(row[f"Y1_{i}"]), int(row[f"Y2_{i}"])])
            draw.rectangle([x1, y1, x2, y2], outline=SCORER_COLORS_PIL[i], width=line_width)
            top_y.append(y1)
            if left_x is None:
                left_x = x1

        if top_y:
            _draw_score_label_pil(
                draw,
                row,
                label_x=left_x,
                label_y=min(top_y) - font_size - 4,
                font=font,
                font_size=font_size,
            )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "JPEG", quality=85)


def save_all_annotation_images(
    data: pd.DataFrame,
    raw_folder_path: str | Path,
    output_dir: str | Path,
    skip_existing: bool = False,
) -> None:
    """
    Save annotation JPEGs for every unique source image in data.

    Parameters
    ----------
    data : pd.DataFrame
        Annotation data (output of 03_checking_collected_coords).
    raw_folder_path : Union[str, Path]
        Folder containing scorer-specific subfolders on the shared drive.
    output_dir : Union[str, Path]
        Directory to write <stem>_annotations.jpg files into.
    skip_existing : bool
        If True, skip images whose output file already exists.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for basename, rows in data.groupby("Basename"):
        output_path = output_dir / f"{Path(basename).stem}_annotations.jpg"
        if skip_existing and output_path.exists():
            print(f"Skipping {output_path.name} (already exists)")
            continue
        save_annotation_image(basename, rows, raw_folder_path, output_path)
        print(f"Saved {output_path.name}")


def view_annotations(
    data_path: str | Path,
    raw_folder_path: str | Path,
    mode: str = "cda",
    starting_row: int = 0,
) -> None:
    """
    Interactively view CDA annotations overlaid on source agroinfiltration images.

    Parameters
    ----------
    data_path : Union[str, Path]
        Path to the annotation CSV (output of 02_combining_cdascorer_outputs).
    raw_folder_path : Union[str, Path]
        Folder containing scorer-specific subfolders on the shared drive.
    mode : str
        'cda' — step through one CDA at a time (arrow keys).
        'raw' — step through one full agroinfiltration image at a time.
    starting_row : int
        Unit index to start from.

    Note: Requires a display and connection to the network drive.
    Press spacebar to save the current view as a JPEG in the working directory.
    """
    if mode not in ("cda", "raw"):
        raise ValueError(f"mode must be 'cda' or 'raw', got '{mode}'")

    data = pd.read_csv(data_path)

    if mode == "raw":
        grouped = data.groupby("Basename", sort=False)
        units = list(grouped.groups.keys())
    else:
        units = None

    n_units = len(units) if units is not None else len(data)

    if not (0 <= starting_row < n_units):
        raise ValueError(
            f"starting_row {starting_row} is out of bounds (dataset has {n_units} units)."
        )

    def get_unit(idx):
        """Return (filename, rows_df) for the given unit index."""
        if mode == "raw":
            filename = units[idx]
            return filename, grouped.get_group(filename)
        row = data.iloc[idx]
        return row["Basename"], pd.DataFrame([row])

    current_idx = [starting_row - 1]
    current_filename = [None]
    img_tk_ref = [None]

    def show_image(direction):
        current_idx[0] += direction

        if current_idx[0] < 0:
            messagebox.showinfo("Beginning of Data", "Cannot go back any further.")
            current_idx[0] = 0
            return
        if current_idx[0] >= n_units:
            messagebox.showinfo("End of Data", "No more annotations to display.")
            root.quit()
            return

        filename, rows = get_unit(current_idx[0])
        current_filename[0] = filename

        scorer = rows.iloc[0]["Scorer1"]
        raw_path = os.path.join(raw_folder_path, scorer, filename)

        if not os.path.exists(raw_path):
            messagebox.showwarning("File Not Found", f"'{raw_path}' not found.")
            return

        img = Image.open(raw_path)
        screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
        scale = min(screen_w / img.width, screen_h / img.height) * 0.9
        display_w = round(img.width * scale)
        display_h = round(img.height * scale)

        img_tk_ref[0] = ImageTk.PhotoImage(img.resize((display_w, display_h)))
        canvas.config(width=display_w, height=display_h)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk_ref[0])

        if mode == "cda":
            r = rows.iloc[0]
            label = f"Filename: {filename}  Row: {r['Row']}  Col: {r['Col']}  Pos: {r['Pos']}"
        else:
            label = f"Filename: {filename}  ({current_idx[0] + 1}/{n_units})"

        canvas.create_text(200, 20, text=label, fill="red", font=("Helvetica", "20", "bold"))

        for _, row in rows.iterrows():
            top_y, left_x = [], None
            for i in range(1, 4):
                if pd.isna(row[f"X1_{i}"]):
                    continue
                x1 = int(row[f"X1_{i}"] * scale)
                y1 = int(row[f"Y1_{i}"] * scale)
                x2 = int(row[f"X2_{i}"] * scale)
                y2 = int(row[f"Y2_{i}"] * scale)
                canvas.create_rectangle(x1, y1, x2, y2, outline=SCORER_COLORS_TK[i], width=3)
                top_y.append(y1)
                if left_x is None:
                    left_x = x1

            if top_y:
                _draw_score_label_tk(
                    canvas,
                    row,
                    label_x=left_x,
                    label_y=min(top_y) - 28,
                    tk_font_obj=tk_font_obj[0],
                )

    def save_current(event=None):
        if current_filename[0] is None:
            return
        _, rows = get_unit(current_idx[0])
        output_path = Path(current_filename[0]).stem + "_annotations.jpg"
        save_annotation_image(current_filename[0], rows, raw_folder_path, output_path)
        messagebox.showinfo("Saved", f"Saved as {output_path}")

    root = tk.Tk()
    root.title(f"CDA Annotation Viewer — {mode} mode")
    root.geometry("+100+100")

    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack()

    tk_font_obj = [tkfont.Font(family="Helvetica", size=20, weight="bold")]

    root.bind("<Right>", lambda e: show_image(1))
    root.bind("<Left>", lambda e: show_image(-1))
    root.bind("<space>", save_current)
    root.protocol(
        "WM_DELETE_WINDOW",
        lambda: root.destroy() if messagebox.askokcancel("Quit", "Quit?") else None,
    )

    show_image(1)
    root.mainloop()
