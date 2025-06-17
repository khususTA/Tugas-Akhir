import os
from ultralytics import YOLO

MODEL_FOLDER = "model"  # Folder tempat menyimpan semua .pt

print("============================")
print("🔍 Pemeriksaan Semua Model")
print("============================")

if not os.path.exists(MODEL_FOLDER):
    print(f"❌ Folder '{MODEL_FOLDER}' tidak ditemukan. Buat folder tersebut dan letakkan file .pt di dalamnya.")
    exit()

pt_files = [f for f in os.listdir(MODEL_FOLDER) if f.endswith(".pt")]

if not pt_files:
    print(f"❌ Tidak ada file .pt di folder '{MODEL_FOLDER}'.")
    exit()

for pt_file in pt_files:
    model_path = os.path.join(MODEL_FOLDER, pt_file)
    print(f"\n=== {pt_file} ===")
    try:
        model = YOLO(model_path)
        class_names = model.names

        for class_id, class_name in class_names.items():
            print(f"[{class_id}] {class_name}")
        print(f"Total: {len(class_names)} kelas")

    except Exception as e:
        print(f"❌ Gagal memuat {pt_file}: {e}")
