# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Organiza arquivos processados do PPP
Description          : Descompacta e distribui na estrutura de pastas os arquivos processados do PPP
Version              : 1.1
copyright            : 1ºCGEO / DSG
reference:
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from re import search
import zipfile
import sys
import shutil


def extraiZip(zip, estrutura):
    zip_ref = zipfile.ZipFile(zip, 'r')
    zip_ref.extractall(estrutura)
    zip_ref.close()
    if len(os.listdir(estrutura)) == 1:
        source = os.path.join(estrutura, os.listdir(estrutura)[0])
        if os.path.isdir(source):
            for f in os.listdir(source):
                shutil.move(os.path.join(source, f), estrutura)
            shutil.rmtree(source)


def organizePPP(estrutura_pasta, pasta_ppp):
    errors = []
    pto_regex = r"^(RS|PR|SC|SP)-(HV|Base)-[1-9]+[0-9]*$" # refazer regex
    zipfiles = {f.split("_")[1][:-4]: os.path.join(pasta_ppp, f) for f in os.listdir(pasta_ppp) if os.path.isfile(
        os.path.join(pasta_ppp, f)) and f.endswith('.zip') and len(f.split("_")) == 4 and search(pto_regex, f.split("_")[1][:-4])}
    ptos_estrutura = {}
    for root, dirs, files in os.walk(estrutura_pasta):
        if search(pto_regex, root.split('\\')[-1]):
            if "6_Processamento_PPP" in dirs:
                ptos_estrutura[root.split(
                    '\\')[-1]] = os.path.join(root, "6_Processamento_PPP")

    for zip_pto in zipfiles:
        if zip_pto in ptos_estrutura:
            extraiZip(zipfiles[zip_pto], ptos_estrutura[zip_pto])

    if set(zipfiles.keys()) - set(ptos_estrutura.keys()):
        errors.append('Pontos nao encontrados na estrutura: {}'.format(repr(list(set(zipfiles.keys()) - set(ptos_estrutura.keys())))))
    if set(ptos_estrutura.keys()) - set(zipfiles.keys()):
        errors.append('Pontos que não possuem zip: {}'.format(repr(list(set(ptos_estrutura.keys()) - set(zipfiles.keys())))))

    return errors

if __name__ == '__main__':
    if len(sys.argv) == 3:
        organizePPP(sys.argv[1], sys.argv[2])
    else:
        print(u'Parametros incorretos!')
