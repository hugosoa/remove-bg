import requests

# L'adresse de ton API (locale pour l'instant)
url = "http://localhost:8000/remove-bg"

# Le chemin de ton image
image_path = "mon_chat.jpg"
save_path = "mon_chat_detoure.png"

print("⏳ Envoi de l'image en cours...")

# On ouvre le fichier en mode binaire ('rb')
with open(image_path, "rb") as f:
    # On prépare le "paquet" à envoyer (multipart/form-data)
    # 'file' correspond au nom du paramètre dans ton API (file: UploadFile)
    files = {"file": ("image.jpg", f, "image/jpeg")}
    
    # On envoie la requête POST
    response = requests.post(url, files=files)

# Vérification du résultat
if response.status_code == 200:
    print("✅ Succès ! L'image détourée a été reçue.")
    # On sauvegarde le contenu binaire reçu dans un fichier
    with open(save_path, "wb") as f_out:
        f_out.write(response.content)
    print(f"📁 Image sauvegardée sous : {save_path}")
else:
    print(f"❌ Erreur : {response.status_code}")
    print(response.text)