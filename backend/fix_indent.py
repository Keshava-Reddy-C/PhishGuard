import re

with open('phishingUrlDetectionApp/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove any tabs
content = content.replace('\t', '    ')

# Fix lines that start with 9 spaces followed by non-space
content = re.sub(r'^         ([^ ])', r'        \1', content, flags=re.MULTILINE)

# Write back
with open('phishingUrlDetectionApp/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed indentation in views.py")



