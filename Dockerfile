FROM python:3.9-slim

# Correction ici : on utilise les nouveaux paquets compatibles Debian Trixie/Bookworm
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

WORKDIR /app

COPY requirements.txt .

# On installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Si tu n'utilises pas l'extension VS Code et que tu veux lancer l'app :
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]