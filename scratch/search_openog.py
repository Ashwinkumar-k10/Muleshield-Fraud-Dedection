import os

for root, dirs, files in os.walk('.'):
    # Skip directories like .git, node_modules, .next
    if any(p in root for p in ['.git', 'node_modules', '.next', 'brain', 'tasks', 'logs']):
        continue
    for f in files:
        if f.endswith(('.py', '.html', '.ts', '.tsx', '.json', '.md', '.txt')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    if 'openog' in content.lower():
                        print(f"Found in {path}")
                        # print the line
                        for line_no, line in enumerate(content.splitlines(), 1):
                            if 'openog' in line.lower():
                                print(f"  Line {line_no}: {line.strip()}")
            except Exception as e:
                pass
