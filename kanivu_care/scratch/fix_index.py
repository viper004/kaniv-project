import os

file_path = r'c:\Users\jagan\Desktop\kaniv\kanivu_care\kanivu_care\templates\index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

target = 'show_volunteer_cta %}'
replacement = 'show_volunteer_cta and request.user.userprofile.role not in "office_staff principal chairman" %}'

for i in range(len(lines)):
    if target in lines[i]:
        lines[i] = lines[i].replace(target, replacement)
        print(f"Replaced in line {i+1}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
