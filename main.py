from tkinter import *
from tkinter.ttk import Combobox
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageFont, ImageTk

# Global variables
original_img = None
watermarked_img = None
tk_img = None
selected_color = (255, 255, 255)
PREVIEW_WIDTH = 450
PREVIEW_HEIGHT = 450

# Upload and display the selected image
def upload_image():
    global original_img, watermarked_img
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        original_img = Image.open(file_path).convert("RGBA")
        watermarked_img = original_img.copy()
        show_preview(watermarked_img)

# Open color picker dialog
def pick_color():
    global selected_color
    color = colorchooser.askcolor(title="Choose Watermark Color")
    if color[0]:
        selected_color = tuple(int(c) for c in color[0])

# Create rotated watermark text as an image layer
def create_rotated_text(text, font, fill, angle):
    dummy_img = Image.new('RGBA', (500, 500), (255, 255, 255, 0))
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_layer = Image.new('RGBA', (text_width + 10, text_height + 10), (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    draw.text((5, 5), text, font=font, fill=fill)

    return text_layer.rotate(angle, expand=1)

# Apply the watermark based on direction
def add_watermark():
    global watermarked_img
    if original_img is None:
        messagebox.showerror("Error", "Please upload an image first.")
        return

    text = watermark_text_input.get()
    if not text:
        messagebox.showerror("Error", "Please enter watermark text.")
        return

    direction = direction_combo.get()

    try:
        per_line = int(per_line_entry.get())
        num_lines = int(num_lines_entry.get())
        if per_line < 1 or num_lines < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Enter positive integers for watermark count and lines.")
        return

    watermarked_img = original_img.copy()
    draw = ImageDraw.Draw(watermarked_img)

    try:
        font_size = int(font_size_combo.get())
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        # Fallback to default font if arial.ttf is unavailable
        font = ImageFont.load_default()

    opacity = int(opacity_scale.get())
    fill = selected_color + (opacity,)
    img_w, img_h = watermarked_img.size

    # Horizontal watermarks
    if direction == "Horizontal":
        v_spacing = img_h // (num_lines + 1)
        h_spacing = img_w // (per_line + 1)
        for row in range(1, num_lines + 1):
            y = v_spacing * row
            for col in range(1, per_line + 1):
                x = h_spacing * col
                draw.text((x, y), text, font=font, fill=fill)

    # Diagonal watermarks
    elif direction == "Diagonal":
        angle = 45
        rotated_text = create_rotated_text(text, font, fill, angle)
        w, _ = rotated_text.size
        x_spacing = img_w // per_line
        y_spacing = img_h // num_lines

        for i in range(0, img_w + x_spacing, x_spacing):
            for j in range(0, img_h + y_spacing, y_spacing):
                if i < img_w and j < img_h:
                    watermarked_img.paste(rotated_text, (i, j), rotated_text)

    show_preview(watermarked_img)

# Save the final watermarked image
def save_image():
    if watermarked_img is None:
        messagebox.showerror("Error", "No watermarked image to save.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if path:
        watermarked_img.save(path)
        messagebox.showinfo("Saved", "Watermarked image saved successfully!")

# Show image preview in canvas
def show_preview(image):
    global tk_img
    canvas.delete("all")
    img_copy = image.copy()
    img_copy.thumbnail((PREVIEW_WIDTH, PREVIEW_HEIGHT))
    tk_img = ImageTk.PhotoImage(img_copy)
    x = (PREVIEW_WIDTH - img_copy.width) // 2
    y = (PREVIEW_HEIGHT - img_copy.height) // 2
    canvas.create_image(x, y, anchor=NW, image=tk_img)

# ---------------------------- UI SETUP ------------------------------------
window = Tk()
window.title("Watermark App")
window.config(padx=20, pady=20)

# Upload Image Button
image_button=Button(text="Upload Image", command=upload_image)
image_button.grid(row=0, column=0, pady=10, sticky=W)

# Watermark Text Input
watermark_text_label=Label(text="Watermark Text:")
watermark_text_label.grid(row=1, column=0, sticky=W)

watermark_text_input = Entry(window, width=40)
watermark_text_input.grid(row=1, column=1, columnspan=3, sticky=W, pady=5)

# Font Size
font_size_label=Label(text="Font Size:")
font_size_label.grid(row=2, column=0, sticky=W)

font_sizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40]
font_size_combo = Combobox(window, values=font_sizes, state="normal", width=8)
font_size_combo.set(12)
font_size_combo.grid(row=2, column=1, sticky=W, pady=5)

# Opacity Scale
opacity_label=Label(text="Opacity (0–255):")
opacity_label.grid(row=3, column=0, sticky=W)

opacity_scale = Scale(window, from_=0, to=255, orient=HORIZONTAL)
opacity_scale.set(128)
opacity_scale.grid(row=3, column=1, sticky=W, pady=5)

# Direction ComboBox
direction_label=Label(text="Direction:")
direction_label.grid(row=4, column=0, sticky=W)

direction_combo = Combobox(window, values=["Horizontal", "Diagonal"], state="readonly", width=13)
direction_combo.set("Diagonal")
direction_combo.grid(row=4, column=1, sticky=W, pady=5)

# Watermarks per line
per_line_label=Label(text="Watermarks Per Line:")
per_line_label.grid(row=5, column=0, sticky=W)

per_line_entry = Entry(window, width=10)
per_line_entry.insert(0, "5")
per_line_entry.grid(row=5, column=1, sticky=W, pady=5)

# Number of lines
num_lines_label=Label(text="Number of Lines:")
num_lines_label.grid(row=6, column=0, sticky=W)

num_lines_entry = Entry(window, width=10)
num_lines_entry.insert(0, "3")
num_lines_entry.grid(row=6, column=1, sticky=W, pady=5)

# Pick color
color_button=Button(text="Pick Text Color", command=pick_color)
color_button.grid(row=7, column=0, sticky=W)

# Add watermark
add_watermark_button=Button(text="Add Watermark", command=add_watermark, bg="#90EE90", width=20)
add_watermark_button.grid(row=8, column=0, pady=15)

# save buttons
save_button=Button(text="Save Image", command=save_image, bg="#D3D3D3", width=20)
save_button.grid(row=8, column=1, pady=15)

# Preview Canvas
canvas = Canvas(window, width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT, bg="lightgray", relief="sunken", bd=2)
canvas.create_text(PREVIEW_WIDTH // 2, PREVIEW_HEIGHT // 2, text="Preview will appear here", fill="gray")
canvas.grid(row=0, column=4, rowspan=10, padx=20)

window.mainloop()
