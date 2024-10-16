import tkinter as tk
import requests
from PIL import Image, ImageTk
import threading
import cairosvg  # Library to convert SVG to PNG
import io

# API endpoint
API_URL = "http://127.0.0.1:5000/position"

# UI dimensions
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
CIRCLE_RADIUS = 10

# Background image file path (SVG file)
BACKGROUND_IMAGE_PATH = "/home/jan/Desktop/SICK Hackathon/floorplan.svg"

class MovingObjectApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moving Object Visualization")

        # Load background SVG and convert it to PNG for Tkinter
        try:
            self.background_photo = self.load_svg_as_image(BACKGROUND_IMAGE_PATH)
        except Exception as e:
            print(f"Error loading SVG: {e}")
            return

        # Create canvas
        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()

        # Add background image to canvas
        self.bg = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_photo)

        # Create a blue circle representing the object
        self.circle = self.canvas.create_oval(
            CANVAS_WIDTH // 2 - CIRCLE_RADIUS,
            CANVAS_HEIGHT // 2 - CIRCLE_RADIUS,
            CANVAS_WIDTH // 2 + CIRCLE_RADIUS,
            CANVAS_HEIGHT // 2 + CIRCLE_RADIUS,
            fill="blue"
        )

        # Start querying the API every second
        self.update_position()

    def load_svg_as_image(self, svg_path):
        """Convert an SVG image to a PNG and load it for Tkinter."""
        try:
            with open(svg_path, "rb") as svg_file:
                svg_data = svg_file.read()
            
            # Convert SVG to PNG using cairosvg
            png_data = cairosvg.svg2png(bytestring=svg_data)

            # Open the PNG data as a Pillow image
            png_image = Image.open(io.BytesIO(png_data))

            # Debug: Show image size and mode for verification
            print(f"Image loaded successfully. Size: {png_image.size}, Mode: {png_image.mode}")

            # Convert it to a format Tkinter can use
            return ImageTk.PhotoImage(png_image)

        except Exception as e:
            raise Exception(f"Failed to load SVG: {e}")

    def update_position(self):
        # Fetch the current position from the API
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
            position = data.get("position", [0, 0])  # Default to [0, 0] if not provided
        except Exception as e:
            print(f"Error fetching position: {e}")
            position = [0, 0]

        # Update the UI with the new position
        self.move_background(position)

        # Schedule the next update after 1 second (1000 ms)
        self.root.after(10, self.update_position)

    def move_background(self, position):
        """Moves the background and the circle based on the current position."""
        # Get the current coordinates of the background
        bg_coords = self.canvas.coords(self.bg)
        bg_x, bg_y = bg_coords[0], bg_coords[1]

        # Calculate new position for the background based on the object position
        new_x = CANVAS_WIDTH // 2 - position[0] * 100
        new_y = CANVAS_HEIGHT // 2 - position[1] * 100

        # Move the background image to new coordinates
        self.canvas.move(self.bg, new_x - bg_x, new_y - bg_y)

        # Move the blue circle to the center of the canvas
        self.canvas.coords(
            self.circle,
            CANVAS_WIDTH // 2 - CIRCLE_RADIUS,
            CANVAS_HEIGHT // 2 - CIRCLE_RADIUS,
            CANVAS_WIDTH // 2 + CIRCLE_RADIUS,
            CANVAS_HEIGHT // 2 + CIRCLE_RADIUS,
        )

def start_app():
    root = tk.Tk()
    app = MovingObjectApp(root)
    root.mainloop()

if __name__ == "__main__":
    # Start the app in a separate thread to prevent blocking
    threading.Thread(target=start_app).start()
