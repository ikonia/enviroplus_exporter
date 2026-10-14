#!/usr/bin/python3

import logging
import signal
import sys
import time
import socket
from datetime import datetime

import st7735
from PIL import Image, ImageDraw, ImageFont

# Debian fonts-roboto; replaces the PyPI `fonts`/`font-roboto` packages
FONT_PATH = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf"

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")

logging.info("lcd.py - Time display on 0.96\" LCD")

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle SIGTERM from systemd."""
    global shutdown_requested
    logging.info("Received shutdown signal")
    shutdown_requested = True


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)  # Keep Ctrl+C support

# Create LCD class instance.
disp = st7735.ST7735(
    port=0,
    cs=1,
    dc="GPIO9",
    backlight="GPIO12",
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display.
disp.begin()

# Width and height to calculate text position.
WIDTH = disp.width
HEIGHT = disp.height

# New canvas to draw on.
img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

# Text settings.
font_size = 25
font = ImageFont.truetype(FONT_PATH, font_size)
text_colour = (255, 255, 255)
back_colour = (0, 170, 170)


def draw_time():
    """Draw the current time on the display."""
    hostname = socket.gethostname()
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    message = f"{hostname} {time_str}"

    # Calculate text position
    x1, y1, x2, y2 = font.getbbox(message)
    size_x = x2 - x1
    size_y = y2 - y1
    x = (WIDTH - size_x) / 2
    y = (HEIGHT / 2) - (size_y / 2)

    # Draw background rectangle and write text.
    draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
    draw.text((x, y), message, font=font, fill=text_colour)
    disp.display(img)


# Initial display
draw_time()

# Keep running until shutdown requested
logging.info("Time display started. Press Ctrl+C or send SIGTERM to stop.")

try:
    while not shutdown_requested:
        time.sleep(1)
        draw_time()

except Exception as e:
    logging.error(f"Error: {e}")
    raise

finally:
    # Turn off backlight on exit
    disp.set_backlight(0)
    logging.info("Display turned off. Goodbye!")
