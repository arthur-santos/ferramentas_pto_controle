# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Prepara estrutura de pastas para o processamento
Description          : Cria pastas e compacta arquivos para iniciar o processamento PPP e TBC
Version              : 1.0
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
import re
import zipfile
import sys


def criaPastas(pasta):
    pto_regex = r"^([A-Z]{2})-(HV|Base)-[1-9]+[0-9]*$" # todo: define new regex
    date_regex = r"\d{4}-\d{2}-\d{2}"
    for root, dirs, files in os.walk(pasta):
        if re.match(pto_regex, root.split('\\')[-1]):
            if not "6_Processamento_PPP" in dirs:
                os.mkdir(os.path.join(root, "6_Processamento_PPP"))
            if not "7_Processamento_TBC_RBMC" in dirs:
                os.mkdir(os.path.join(root, "7_Processamento_TBC_RBMC"))
        if re.match(date_regex, root.split('\\')[-1].split("_")[-1]) and root.split('\\')[-1].split("_")[-1] == root.split('\\')[-2]:
            nome_pasta = "_Processamento_TBC_{0}".format(root.split('\\')[-1])
            if not nome_pasta in dirs:
                os.mkdir(os.path.join(root, nome_pasta))
        if re.match(date_regex, root.split('\\')[-1]):
            if not "_Processamento_RBMC" in dirs:
                os.mkdir(os.path.join(root, "_Processamento_RBMC"))
            if not "_Revisao" in dirs:
                os.mkdir(os.path.join(root, "_Revisao"))


def zipaPPP(pasta):
    for root, dirs, files in os.walk(pasta):
        if root.split('\\')[-1] == "2_RINEX":
            pto = root.split('\\')[-2]
            if (pto + ".18n") in files and (pto + ".18o") in files and not (pto + ".zip") in files:
                zf = zipfile.ZipFile(os.path.join(
                    root, pto + ".zip"), "w", zipfile.ZIP_DEFLATED)
                zf.write(os.path.join(root, pto + ".18n"), pto + ".18n")
                zf.write(os.path.join(root, pto + ".18o"), pto + ".18o")


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        criaPastas(sys.argv[1])
        zipaPPP(sys.argv[1])
    else:
        print(u'Parametros incorretos!')
