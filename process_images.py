from PIL import Image
import os

def remove_background(image_path):
    print(f"Processing {image_path}...")
    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")
        
        datas = img.getdata()
        
        # On suppose que la couleur du pixel en haut à gauche (0,0) est la couleur de fond
        background_color = datas[0]
        # On ne garde que RGB, on ignore l'alpha pour la comparaison
        bg_rgb = background_color[:3]
        
        new_data = []
        
        threshold = 30 # Tolérance
        
        for item in datas:
            # item est (R, G, B, A)
            # Distance euclidienne simple ou différence absolue
            diff = sum([abs(item[i] - bg_rgb[i]) for i in range(3)])
            
            if diff < threshold:
                # C'est du fond -> Transparent
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        
        img.putdata(new_data)
        img.save(image_path, "PNG")
        print(f"Done: {image_path}")
        
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

def main():
    folder = "images"
    if not os.path.exists(folder):
        print(f"Folder '{folder}' not found.")
        return

    for filename in os.listdir(folder):
        if filename.lower().endswith(".png"):
            # On ignore les fichiers déjà traités si besoin, mais ici on overwrite
            full_path = os.path.join(folder, filename)
            remove_background(full_path)

if __name__ == "__main__":
    main()
