from fastapi import FastAPI, Request, File, Form, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
from io import BytesIO
from random import randint

app = FastAPI()

app.mount("/assets", StaticFiles(directory="site/assets"), name="assets")

templates = Jinja2Templates(directory="site")


def bulge(image, strength=20):
    width, height = image.size
    bulged_image = Image.new('RGB', (width, height))
    
    # Generate random coordinates for the center of the bulge
    center_x = randint(0, width - 1)
    center_y = randint(0, height - 1)
    
    for y in range(height):
        for x in range(width):
            dx = x - center_x
            dy = y - center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            # Check if the current pixel is within the boundaries of the original image
            if 0 <= x < width and 0 <= y < height:
                if distance < width / 2:
                    theta = 1 - distance / (width / 2)
                    theta **= 2
                    new_x = x - dx * theta * strength
                    new_y = y - dy * theta * strength
                    if 0 <= new_x < width and 0 <= new_y < height:
                        bulged_image.putpixel((x, y), image.getpixel((int(new_x), int(new_y))))
                else:
                    # Preserve the original pixel if it's outside the bulge radius
                    bulged_image.putpixel((x, y), image.getpixel((x, y)))
            else:
                # Preserve the original pixel if it's outside the boundaries of the original image
                bulged_image.putpixel((x, y), image.getpixel((x, y)))
    return bulged_image


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )
    
@app.post("/deepfry")
async def post_deepfry(image: UploadFile):
    image_contents = await image.read()
    edited_image = Image.open(BytesIO(image_contents))
    edited_image = edited_image.filter(ImageFilter.SHARPEN)
    edited_image = ImageEnhance.Contrast(edited_image).enhance(2)
    edited_image = ImageEnhance.Brightness(edited_image).enhance(2)
    
    edited_image = bulge(edited_image, 1)
    
    for i in range(10):
        with BytesIO() as output:
            edited_image.save(output, format="JPEG", quality=1)
            output.seek(0)
            # Open the compressed image from memory
            compressed_image = Image.open(output)
            # Convert the image to RGB mode if needed
            if compressed_image.mode != 'RGB':
                compressed_image = compressed_image.convert('RGB')
            
            # Get the pixel data from the compressed image
            pixels = compressed_image.load()
            
            # Do any further processing here if needed
            
            # You can also overwrite the original edited_image if desired
            edited_image = compressed_image.copy()
    
    # Save the processed image to memory
    output_buffer = BytesIO()
    edited_image.save(output_buffer, format="JPEG")
    
    # Return the processed image
    return StreamingResponse(BytesIO(output_buffer.getvalue()), media_type="image/jpeg")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)