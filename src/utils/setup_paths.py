from pathlib import Path
from .constants import parent_dir

def create_directories():
    subdirs = ['flood', 'earthquake', 'landslide', 'deforestation', 'cyclone', 'coastal_erosion']
    for subdir in subdirs:
        Path(parent_dir / f'./output_data/{subdir}').mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    create_directories()