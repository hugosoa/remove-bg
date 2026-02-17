1. Structure des fichiers
Créez un dossier racine pour votre projet et placez-y les fichiers suivants :

Plaintext
removebg-api/
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── main.py
├── requirements.txt
└── README.md
2. Le code de l'API (main.py)
Ce fichier contient la logique FastAPI, le traitement d'image et la gestion des erreurs.

Python
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image, UnidentifiedImageError
import io
from starlette.responses import StreamingResponse

app = FastAPI(title="AI Background Remover API")

# Configuration CORS : Autorise les requêtes depuis votre futur site de scrapbooking
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production (ex: ["https://votre-site.com"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Limite de taille optionnelle (ex: 10 Mo)
MAX_FILE_SIZE = 10 * 1024 * 1024 

@app.post("/remove-bg")
async def process_image(
    file: UploadFile = File(...),
    alpha_matting: bool = Query(False, description="Active le détourage fin pour les détails complexes")
):
    # 1. Vérification du format
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Format invalide. JPEG, PNG ou WEBP requis.")

    try:
        # 2. Lecture et vérification de la taille
        image_data = await file.read()
        if len(image_data) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Fichier trop lourd (max 10 Mo).")

        # 3. Ouverture de l'image
        input_image = Image.open(io.BytesIO(image_data))
        
        # 4. Traitement par l'IA
        # alpha_matting améliore les cheveux/poils mais consomme plus de CPU
        output_image = remove(input_image, alpha_matting=alpha_matting)

        # 5. Préparation de la réponse en PNG (supporte la transparence)
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return StreamingResponse(img_byte_arr, media_type="image/png")

    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="L'image est corrompue.")
    except Exception as e:
        print(f"Erreur serveur: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne lors du traitement.")
3. Dépendances et Recette Docker
requirements.txt

Plaintext
fastapi
uvicorn
python-multipart
rembg
onnxruntime
pillow
Dockerfile

Dockerfile
# Utilisation d'une image légère avec Python pré-installé
FROM python:3.9-slim

# Installation des dépendances système nécessaires à OpenCV et au traitement d'image
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation des librairies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY main.py .

# Exposition du port interne
EXPOSE 8000

# Commande de lancement
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
4. Orchestration (docker-compose.yml)
Ce fichier permet de lancer l'application avec les volumes pour éviter de retélécharger l'IA à chaque démarrage.

YAML
services:
  api-removebg:
    build: .
    ports:
      - "8000:8000"
    volumes:
      # Synchronisation du code en direct pour le développement
      - ./:/app
      # Conservation du modèle d'IA (170 Mo) sur votre machine
      - u2net_data:/root/.u2net
    # Commande avec --reload pour que le serveur redémarre à chaque sauvegarde de main.py
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  u2net_data:
5. Gestion de la propreté (.gitignore & .dockerignore)
.gitignore (Pour GitHub)

Plaintext
__pycache__/
*.pyc
.DS_Store
.vscode/
venv/
*.jpg
*.png
.dockerignore (Pour l'Image Docker)

Plaintext
.git
.gitignore
docker-compose.yml
Dockerfile
.dockerignore
__pycache__
README.md
6. Documentation (README.md)
Markdown
# ✂️ Background Remover API

Microservice de suppression d'arrière-plan utilisant FastAPI et Rembg.

## Lancement
```bash
docker compose up --build
Accès
API : http://localhost:8000

Documentation interactive : http://localhost:8000/docs

Utilisation
Envoyez un fichier via une requête POST sur /remove-bg avec la clé file.


---

### Procédure de lancement final
1. Ouvrez votre terminal dans le dossier du projet.
2. Lancez la commande : `docker compose up --build`.
3. Une fois le message "Uvicorn running" affiché, rendez-vous sur `http://localhost:8000/docs`.
4. Testez l'endpoint avec une image locale.
