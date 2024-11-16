import random
from rest_captcha import VERSION
from .settings import api_settings

cache_template = api_settings.CAPTCHA_CACHE_KEY


def get_cache_key(captcha_key):
    cache_key = cache_template.format(key=captcha_key, version=VERSION.major)
    return cache_key


def random_char_challenge(length):
    chars = "abcdefghijklmnopqrstuvwxyz"
    ret = ""
    for i in range(length):
        ret += random.choice(chars)
    return ret.upper()


def filter_smooth(image, filter_code):
    return image.filter(filter_code)


def noise_dots(draw, image, fill):
    """Reduce noise dots by lowering the density."""
    size = image.size
    dot_count = int(size[0] * size[1] * 0.02)  # Reduce density to 2% of image area
    for p in range(dot_count):
        x = random.randint(0, size[0])
        y = random.randint(0, size[1])
        draw.point((x, y), fill=fill)
    return draw


def noise_arcs(draw, image, fill):
    """Reduce noise arcs and lines for less obtrusiveness."""
    size = image.size
    # Draw fewer arcs and lines, ensuring they are not too centered or distracting
    draw.arc(
        [
            random.randint(-50, -10),
            random.randint(-50, -10),
            random.randint(size[0] - 10, size[0] + 10),
            random.randint(size[1] - 10, size[1] + 10),
        ],
        random.randint(0, 45),
        random.randint(135, 295),
        fill=fill,
    )
    draw.line(
        [
            random.randint(-20, -10),
            random.randint(0, size[1]),
            random.randint(size[0] - 10, size[0]),
            random.randint(size[1] - 20, size[1] + 10),
        ],
        fill=fill,
    )
    draw.line(
        [
            random.randint(-20, -10),
            random.randint(0, size[1]),
            random.randint(size[0] - 10, size[0]),
            random.randint(size[1] - 20, size[1] + 10),
        ],
        fill=fill,
    )
    return draw
