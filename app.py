from fastapi import FastAPI, Request, File, Form, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from PIL import Image, ImageFilter, ImageEnhance
from io import BytesIO

app = FastAPI()

app.mount("/assets", StaticFiles(directory="site/assets"), name="assets")

templates = Jinja2Templates(directory="site")


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
    
    """
    for i in range(50):
        with BytesIO() as output:
            edited_image.save(output, format="JPEG", quality=50)
            output.seek(0)
            # Open the compressed image from memory
            edited_image = Image.open(output)
    """
    
    # Save the processed image to memory
    output_buffer = BytesIO()
    edited_image.save(output_buffer, format="JPEG")
    
    # Return the processed image
    return StreamingResponse(BytesIO(output_buffer.getvalue()), media_type="image/jpeg")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)