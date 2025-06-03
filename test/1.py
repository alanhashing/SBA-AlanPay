import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import asyncer

def timeit(loop: int = 1):
    """Decorator to time a function."""
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            for _ in range(loop):
                func(*args, **kwargs)
            end_time = time.time()
            print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
        return wrapper
    return decorator

def async_timeit(loop: int = 1):
    """Decorator to time a function."""
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            for _ in range(loop):
                await func(*args, **kwargs)
            end_time = time.time()
            print(f"Async function {func.__name__} took {end_time - start_time:.4f} seconds")
        return wrapper
    return decorator

@timeit(loop=100)
def create_qr_code_as_base64(string: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(string)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgImage)
    buffer = BytesIO()
    img.save(buffer)
    svg_data = buffer.getvalue()
    base64_svg = base64.b64encode(svg_data).decode('utf-8')
    return base64_svg

a = asyncer.asyncify(create_qr_code_as_base64)

@async_timeit(loop=100)
async def asyncify_create_qr_code_as_base64(string: str):
    return await a(string)

create_qr_code_as_base64("https://example.com")

import anyio
anyio.run(asyncify_create_qr_code_as_base64, "https://example.com")
