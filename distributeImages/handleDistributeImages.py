from pathlib import Path
import re
import sys

def create_folder(structure):
    path = Path(structure)
    folders = [x for x in path.rglob('*') if x.is_dir() and re.match(r'\w\w-\w\w-0*\d+', x.parts[-1])]
    for folder in folders:
        print(folder)
        Path(folder / '7_Imagens_Monografia').mkdir(exist_ok = True)
            
if __name__ == "__main__":
    create_folder(sys.argv[1])