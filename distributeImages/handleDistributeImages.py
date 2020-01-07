from pathlib import Path
import re
import sys
import shutil


class HandleDistrubuteImages():

    def __init__(self, structure, folder_aer_view='teste', folder_view1='teste', folder_view2='tste'):
        self.folders = []
        self.structure = structure
        self.aer_view = folder_aer_view
        self.view1 = folder_view1
        self.view2 = folder_view2

    def create_folder(self):
        path = Path(self.structure)
        self.folders = [x for x in path.rglob(
            '*') if x.is_dir() and re.match(r'\w\w-\w\w-0*\d+', x.parts[-1])]
        for folder in self.folders:
            self.folders.append(folder.parts[-1])
            Path(folder / '7_Imagens_Monografia').mkdir(exist_ok=True)

    def distribute_images(self):
        for folder in self.folders:
            point = folder.parts[-1]
            try:
                shutil.copy(str(Path(self.aer_view / f'{point}.jpg')), str(
                    folder / '7_Imagens_Monografia' / f'{point}_AEREA.jpg'))
                shutil.copy(str(Path(self.view1 / f'{point}.jpg')), str(
                    folder / '7_Imagens_Monografia' / f'{point}_MUNICIPIO.jpg'))
                shutil.copy(str(Path(self.view2 / f'{point}.jpg')), str(
                    folder / '7_Imagens_Monografia' / f'{point}_ESTADO.jpg'))
            except IOError:
                print(
                    'Verifique se todas as vistas aéreas foram corretamente geradas no formato jpg')


if __name__ == "__main__":
    handle = HandleDistrubuteImages(sys.argv[1])
    handle.create_folder()
