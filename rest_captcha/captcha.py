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
    """Add noise to the image."""
    draw = utils.noise_dots(draw, image, settings.CAPTCHA_FOREGROUND_COLOR)
    draw = utils.noise_arcs(draw, image, settings.CAPTCHA_FOREGROUND_COLOR)


def getsize(font, text):
    """Get the bounding box width and height for the given text with the specified font."""
    bbox = font.getbbox(text)
    if hasattr(font, "getlength"):
        # Convert length to an integer and use it as the width
        width = int(font.getlength(text))
        height = bbox[3] - bbox[1]  # Height is calculated from bounding box
        return (width, height)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def makeimg(size):
    """Create a blank image with either RGB or RGBA mode depending on settings."""
    if settings.CAPTCHA_BACKGROUND_COLOR == "transparent":
        return Image.new("RGBA", size)
    return Image.new("RGB", size, settings.CAPTCHA_BACKGROUND_COLOR)


def generate_image(word):
    """Generate a CAPTCHA image for the provided word."""
    font = FONT
    size = settings.CAPTCHA_IMAGE_SIZE
    xpos = 2
    from_top = 4

    # Initialize the base image
    image = makeimg(size)

    for char in word:
        # Create foreground and character images
        fgimage = Image.new("RGB", size, settings.CAPTCHA_FOREGROUND_COLOR)
        charimage = Image.new("L", getsize(font, f" {char} "), "#000000")
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((0, 0), f" {char} ", font=font, fill="#ffffff")

        # Apply random rotation if enabled
        if settings.CAPTCHA_LETTER_ROTATION:
            angle = random.randrange(*settings.CAPTCHA_LETTER_ROTATION)
            charimage = charimage.rotate(angle, expand=False, resample=Image.BICUBIC)

        charimage = charimage.crop(charimage.getbbox())  # Crop to actual character size

        # Position the character in the final image
        maskimage = Image.new("L", size)
        xpos2 = xpos + charimage.size[0]
        from_top2 = from_top + charimage.size[1]
        maskimage.paste(charimage, (xpos, from_top, xpos2, from_top2))

        image = Image.composite(fgimage, image, maskimage)
        xpos += 2 + charimage.size[0]

    # Center CAPTCHA if specified
    if settings.CAPTCHA_IMAGE_SIZE:
        tmpimg = makeimg(size)
        xpos2 = int((size[0] - xpos) / 2)
        from_top2 = int((size[1] - charimage.size[1]) / 2 - from_top)
        tmpimg.paste(image, (xpos2, from_top2))
        image = tmpimg.crop((0, 0, size[0], size[1]))
    else:
        image = image.crop((0, 0, xpos + 1, size[1]))

    # Draw any additional elements and apply filters/noise
    draw = ImageDraw.Draw(image)
    settings.FILTER_FUNCTION(image)
    settings.NOISE_FUNCTION(image, draw)

    # Save image to a BytesIO buffer in PNG format
    out = BytesIO()
    image.save(out, "PNG")
    content = out.getvalue()

    return content

