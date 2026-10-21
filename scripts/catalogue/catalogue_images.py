"""Reuse compact, high-resolution catalogue imagery without changing originals."""
from functools import lru_cache
from io import BytesIO
from PIL import Image, ImageOps


@lru_cache(maxsize=64)
def image_bytes(path):
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original).convert('RGBA')
        background = Image.new('RGBA', image.size, 'white')
        background.alpha_composite(image)
        image = background.convert('RGB')
        image.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
        stream = BytesIO()
        image.save(stream, 'JPEG', quality=86, optimize=True)
        return stream.getvalue()
