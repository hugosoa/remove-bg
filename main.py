from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image, UnidentifiedImageError
import io
from starlette.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/remove-bg")
async def process_image(
    file: UploadFile = File(...),
    alpha_matting: bool = Query(False, description="Active le détourage fin")
):
    
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Fichier invalide. Envoyez une image (JPEG, PNG, WEBP).")

    try:
        image_data = await file.read()
        input_image = Image.open(io.BytesIO(image_data))
        
        output_image = remove(input_image, alpha_matting=alpha_matting)

        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return StreamingResponse(img_byte_arr, media_type="image/png")

    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="L'image est corrompue.")
    except Exception as e:
        print(f"Erreur interne : {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur lors du traitement.")