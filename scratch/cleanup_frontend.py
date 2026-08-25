import shutil
import os

dst = r"a:\Projects\PSB\frontend"

# Unused directories to clean up
unused_dirs = [
    "app/create-craft",
    "app/passport",
    "app/product-match",
    "app/verify",
    "app/weaveproof",
    "app/weaver"
]

for d in unused_dirs:
    target_path = os.path.join(dst, d)
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
        print(f"Removed unused folder: {d}")

print("Cleaned up unused Handloom folders.")
