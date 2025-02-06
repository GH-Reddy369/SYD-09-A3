import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")

        # Initialize variables
        self.image = None
        self.cv_image = None
        self.tk_image = None
        self.crop_rect = None
        self.history = []  # For undo/redo functionality
        self.redo_stack = []  # For redo functionality

        # Create canvas for displaying images
        self.canvas = tk.Canvas(root, width=600, height=400, cursor="cross")
        self.canvas.pack()

        # Frame for buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        # Buttons
        tk.Button(btn_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Save Image", command=self.save_image).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Crop Image", command=self.crop_image).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Undo", command=self.undo).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Redo", command=self.redo).pack(side=tk.LEFT)

        # Slider for resizing
        self.slider = tk.Scale(root, from_=1, to=200, orient=tk.HORIZONTAL, command=self.resize_image)
        self.slider.set(100)  # Default scale
        self.slider.pack()

        # Bind mouse events for cropping
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Keyboard shortcuts
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Control-s>", lambda event: self.save_image())

    def load_image(self):
        """Load an image from file."""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.cv_image = cv2.imread(file_path)
            self.update_image()
            self.history.append(self.cv_image.copy())  # Save to history

    def update_image(self):
        """Update the displayed image on the canvas."""
        if self.cv_image is not None:
            self.image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)
            self.image = Image.fromarray(self.image)
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(300, 200, image=self.tk_image)

    def resize_image(self, value):
        """Resize the image based on the slider value."""
        if self.cv_image is not None:
            scale_percent = int(value)
            width = int(self.cv_image.shape[1] * scale_percent / 100)
            height = int(self.cv_image.shape[0] * scale_percent / 100)
            self.cv_image = cv2.resize(self.cv_image, (width, height))
            self.update_image()

    def save_image(self):
        """Save the modified image to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path and self.cv_image is not None:
            cv2.imwrite(file_path, self.cv_image)

    def on_button_press(self, event):
        """Handle mouse button press for cropping."""
        self.start_x = event.x
        self.start_y = event.y
        self.crop_rect = None

    def on_mouse_drag(self, event):
        """Handle mouse drag for cropping."""
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red")

    def on_button_release(self, event):
        """Handle mouse button release for cropping."""
        if self.crop_rect:
            self.end_x = event.x
            self.end_y = event.y

    def crop_image(self):
        """Crop the image based on the selected rectangle."""
        if self.crop_rect and self.cv_image is not None:
            # Get coordinates of the rectangle
            x1, y1, x2, y2 = self.start_x, self.start_y, self.end_x, self.end_y

            # Convert canvas coordinates to image coordinates
            scale_x = self.cv_image.shape[1] / self.canvas.winfo_width()
            scale_y = self.cv_image.shape[0] / self.canvas.winfo_height()
            x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
            y1, y2 = int(y1 * scale_y), int(y2 * scale_y)

            # Ensure coordinates are within bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(self.cv_image.shape[1], x2), min(self.cv_image.shape[0], y2)

            # Crop the image
            self.cv_image = self.cv_image[y1:y2, x1:x2]
            self.update_image()
            self.history.append(self.cv_image.copy())  # Save to history

    def undo(self):
        """Undo the last operation."""
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())  # Move current state to redo stack
            self.cv_image = self.history[-1].copy()  # Restore previous state
            self.update_image()

    def redo(self):
        """Redo the last undone operation."""
        if self.redo_stack:
            self.history.append(self.redo_stack.pop())  # Move redo state to history
            self.cv_image = self.history[-1].copy()  # Restore redo state
            self.update_image()

# Run the application
root = tk.Tk()
app = ImageEditor(root)
root.mainloop()