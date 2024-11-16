import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from .settings import api_settings as settings
from . import utils

# Load font with specified path and size from settings
FONT = ImageFont.truetype(settings.CAPTCHA_FONT_PATH, settings.CAPTCHA_FONT_SIZE)


def filter_default(image):
    """Apply a smooth filter to the image."""
    return utils.filter_smooth(image, ImageFilter.SMOOTH)


def noise_default(image, draw):
    """Add noise to the image without obstructing readability."""
    draw = utils.noise_dots(draw, image, settings.CAPTCHA_FOREGROUND_COLOR)
    draw = utils.noise_arcs(draw, image, settings.CAPTCHA_FOREGROUND_COLOR)


def getsize(font, text):
    """Get the bounding box width and height for the given text with the specified font."""
    bbox = font.getbbox(text)
    width = bbox[2] - bbox[0]  # Width from bounding box
    height = bbox[3] - bbox[1] + 15  # Height from bounding box
    return width, height


def makeimg(size):
    """Create a blank image with either RGB or RGBA mode depending on settings."""
    if settings.CAPTCHA_BACKGROUND_COLOR == "transparent":
        return Image.new("RGBA", size)
    return Image.new("RGB", size, settings.CAPTCHA_BACKGROUND_COLOR)


def generate_image(word):
    """Generate a CAPTCHA image for the provided word with improved readability."""
    font = FONT
    size = settings.CAPTCHA_IMAGE_SIZE
    xpos = 20  # Start with a larger horizontal padding to avoid cropping
    from_top = 10  # Start with a larger top margin

    # Initialize the base image
    image = makeimg(size)

    # Determine the total width required for the word (with padding) and the height of the characters
    total_width = 0
    total_height = 0
    char_images = []
    for char in word:
        charimage = Image.new("L", getsize(font, f" {char} "), "#000000")
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((0, 0), f" {char} ", font=font, fill="#ffffff")

        # Apply subtle random rotation for readability
        if settings.CAPTCHA_LETTER_ROTATION:
            angle = random.uniform(-10, 10)  # Limited rotation for better readability
            charimage = charimage.rotate(angle, expand=False, resample=Image.BICUBIC)

        charimage = charimage.crop(charimage.getbbox())  # Crop to actual character size
        char_images.append(charimage)
        total_width += charimage.size[0] + 10  # Add some spacing between characters
        total_height = max(
            total_height, charimage.size[1]
        )  # Track the max character height

    # Resize the image to accommodate all characters with space around them
    image_width = max(
        total_width, size[0]
    )  # Ensure the image width is at least the specified width
    image_height = max(
        total_height + 20, size[1]
    )  # Ensure the image height is large enough
    image = makeimg((image_width, image_height))

    xpos = (image_width - total_width) // 2  # Center the characters horizontally

    for charimage in char_images:
        # Create foreground and character images
        fgimage = Image.new(
            "RGB", (image_width, image_height), settings.CAPTCHA_FOREGROUND_COLOR
        )
        maskimage = Image.new("L", (image_width, image_height))

        # Position the character in the final image
        maskimage.paste(charimage, (xpos, from_top))
        image = Image.composite(fgimage, image, maskimage)
        xpos += (
            charimage.size[0] + 10
        )  # Move xpos forward by character width and spacing

    # Draw any additional elements and apply filters/noise
    draw = ImageDraw.Draw(image)
    settings.FILTER_FUNCTION(image)  # Apply smoother filter
    settings.NOISE_FUNCTION(image, draw)  # Apply noise

    # Save image to a BytesIO buffer in PNG format
    out = BytesIO()
    image.save(out, "PNG")
    content = out.getvalue()

    return content
