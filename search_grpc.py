import os

keywords = ["google.generativeai", "genai", "import grpc", "from grpc"]
found = []

for root, dirs, files in os.walk("."):
    # Skip venv and git folders
    if "venv" in dirs:
        dirs.remove("venv")
    if ".git" in dirs:
        dirs.remove(".git")
        
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for kw in keywords:
                        if kw in content:
                            found.append((path, kw))
            except Exception as e:
                pass

if found:
    print("Found potential gRPC/GenAI imports:")
    for path, kw in found:
        print(f"{path}: contains '{kw}'")
else:
    print("No gRPC or GenAI imports found in .py files (excluding venv).")
