import os

target_dir = r"E:\script\min\20230704\min"

files = os.listdir(target_dir)
print(files)
for file in files:
    if file.startswith("s"):
        src = os.path.join(os.path.abspath(target_dir), file)
        dst = os.path.join(os.path.abspath(target_dir), file[2:])
        os.rename(src, dst)

print("end==============================")
