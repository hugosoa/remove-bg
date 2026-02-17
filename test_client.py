import requests

url = "http://localhost:8000/remove-bg"

image_path = "img_test.jpg"
save_path = "img_test_bg_removed.png"

print("⏳ Envoi de l'image en cours...")

with open(image_path, "rb") as f:
    files = {"file": ("image.jpg", f, "image/jpeg")}
    
    response = requests.post(url, files=files)

if response.status_code == 200:
    print("✅ Succès ! L'image détourée a été reçue.")
    
    with open(save_path, "wb") as f_out:
        f_out.write(response.content)
    print(f"📁 Image sauvegardée sous : {save_path}")
else:
    print(f"❌ Erreur : {response.status_code}")
    print(response.text)
