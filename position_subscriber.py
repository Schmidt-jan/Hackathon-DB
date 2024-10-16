import tkinter as tk
import requests
from PIL import Image, ImageTk
import threading
import cairosvg  # Library to convert SVG to PNG
import io

SENSOR_OFFSET_X = 0.52 * 100
SENSOR_OFFSET_Y = 0.59 * 100

OFFSET_X = -2.0
OFFSET_Y = -1

# API endpoint
API_URL = "http://127.0.0.1:5000/position"

# UI dimensions
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
CIRCLE_RADIUS = 10

# Background image file path (SVG file)
BACKGROUND_IMAGE_PATH = "/home/jan/Desktop/SICK Hackathon/floorplan.svg"
ARROW_LEFT_PATH = "/home/jan/Desktop/SICK Hackathon/images/icons8-left-arrow-50.png"
ARROW_RIGHT_PATH = "/home/jan/Desktop/SICK Hackathon/images/icons8-right-arrow-50.png"
ARROW_FORWARD_PATH = "/home/jan/Desktop/SICK Hackathon/images/icons8-arrow-up-50.png"

class MovingObjectApp:
    def __init__(self, root):
        self.root = root
        self.root.bind("<Key>", self.key_handler)
        self.state = 0
        self.root.title("Moving Object Visualization")
        self.arrow_image_id = None

        # Load background SVG and convert it to PNG for Tkinter
        try:
            self.background_photo = self.load_svg_as_image(BACKGROUND_IMAGE_PATH)
            # self.arrow_left = self.load_svg_as_image(ARROW_LEFT_PATH)
            # self.arrow_right = self.load_svg_as_image(ARROW_RIGHT_PATH)
            # self.arrow_forward = self.load_svg_as_image(ARROW_FORWARD_PATH)
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
        
    def key_handler(self, event):
        if self.arrow_image_id is not None:
            self.canvas.delete(self.arrow_image_id)
        # use w, a, s, d to move the object
        if event.char == 'w':
            # load png image
            arrow = tk.PhotoImage(file = ARROW_FORWARD_PATH)
            
            self.arrow_image_id = self.canvas.create_image(CANVAS_WIDTH // 2, 
                                     CANVAS_HEIGHT // 2 - 60 , 
                                     anchor=tk.NW, 
                                     image=arrow)
            
            # set arrow to up
        elif event.char == 'a':
            arrow = tk.PhotoImage(file = ARROW_LEFT_PATH)
            self.arrow_image_id = self.canvas.create_image(CANVAS_WIDTH // 2, 
                                     CANVAS_HEIGHT // 2 - 60 , 
                                        image=arrow)
        elif event.char == 'd':
            # delete arrow
            arrow = tk.PhotoImage(file = ARROW_RIGHT_PATH)
            self.arrow_image_id = self.canvas.create_image(CANVAS_WIDTH // 2 - 15, 
                                     CANVAS_HEIGHT // 2 - 60 , 
                                        anchor=tk.NW,
                                        image=arrow)
            

    def load_svg_as_image(self, svg_path):
        """Convert an SVG image to a PNG and load it for Tkinter."""
        try:
            with open(svg_path, "rb") as svg_file:
                svg_data = svg_file.read()
        
            png_data = cairosvg.svg2png(bytestring=svg_data)
            png_image = Image.open(io.BytesIO(png_data))

            # Debug: Show image size and mode for verification
            print(f"Image loaded successfully. Size: {png_image.size}, Mode: {png_image.mode}")

            # Convert it to a format Tkinter can use
            return ImageTk.PhotoImage(png_image)

        except Exception as e:
            raise Exception(f"Failed to load SVG: {e}")

    def update_position(self):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
            position = data.get("position", [0, 0])  # Default to [0, 0] if not provided
        except Exception as e:
            print(f"Error fetching position: {e}")
            position = [0, 0]

        self.move_background(position)
        self.root.after(10, self.update_position)

    def move_background(self, position):
        """Moves the background and the circle based on the current position."""
        # Get the current coordinates of the background
        bg_coords = self.canvas.coords(self.bg)
        bg_x, bg_y = bg_coords[0], bg_coords[1]

        # Calculate new position for the background based on the object position
        new_x = (OFFSET_X + position[1]) * 100 # + CANVAS_WIDTH // 2 
        new_y = (OFFSET_Y + position[0]) * 100 # + CANVAS_HEIGHT // 2

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
