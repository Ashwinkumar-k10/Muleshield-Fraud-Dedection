import shutil
import os

src = r"A:\Projects\Handloom\frontend"
dst = r"a:\Projects\PSB\frontend"

# Ensure destination exists
os.makedirs(dst, exist_ok=True)

# Rename old index.html to backup
old_index = os.path.join(dst, "index.html")
backup_index = os.path.join(dst, "index_v1_backup.html")
if os.path.exists(old_index) and not os.path.exists(backup_index):
    os.rename(old_index, backup_index)
    print("Backed up old index.html to index_v1_backup.html")

# Copy individual files
config_files = ["package.json", "package-lock.json", "tsconfig.json", "next.config.js", "tailwind.config.js", "postcss.config.js", "Dockerfile"]
for f in config_files:
    src_file = os.path.join(src, f)
    dst_file = os.path.join(dst, f)
    if os.path.exists(src_file):
        shutil.copy2(src_file, dst_file)
        print(f"Copied {f}")

# Copy folders
folders = ["app", "components", "public"]
for folder in folders:
    src_folder = os.path.join(src, folder)
    dst_folder = os.path.join(dst, folder)
    if os.path.exists(src_folder):
        if os.path.exists(dst_folder):
            shutil.rmtree(dst_folder)
        shutil.copytree(src_folder, dst_folder)
        print(f"Copied folder: {folder}")

print("Next.js project structure copied successfully.")
