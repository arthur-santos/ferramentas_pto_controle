# -*- coding: utf-8 -*-

"""
/***************************************************************************
 PontoControle
                                 A QGIS plugin
 Ferramentas para a gerência de pontos de controle
                              -------------------
        begin                : 2019-12-04
        copyright            : (C) 2019 by 1CGEO/DSG
        email                : eliton.filho@eb.mil.br
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

__author__ = '1CGEO/DSG'
__date__ = '2019-12-04'
__copyright__ = '(C) 2019 by 1CGEO/DSG'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import csv
import re
from pathlib import Path

class HandleLoadToBPC():

    def __init__(self, folderin, folderout):
        self.folder = folderin
        self.output = folderout
        
    def getPointsFromCSV(self):
        points = ''
        for root, dirs, files in os.walk(self.folder):
            for f in files:
                if f.endswith(".csv"):
                    with open(os.path.join(root, f)) as csv_file:
                        csv_reader = csv.DictReader(csv_file)
                        for row in csv_reader:
                            self.gerenatezip(root, row['cod_ponto'])
                            points += "'{}',".format(row['cod_ponto'])
        self.points = points
        return "WHERE cod_ponto IN ({})".format(points[:-1])

    @staticmethod
    def gerenatezip(root, cod_ponto):
        #Get files who are going to be zipped
        path = Path(root, cod_ponto)
        files = [
            path / '1_Formato_Nativo' / '{}.T01'.format(cod_ponto),
            path / '2_RINEX' / '{}.zip'.format(cod_ponto),
            path / '7_Processamento_TBC_RBMC' / '{}_ACURACIA_PRE.pdf'.format(cod_ponto)
        ]
        path_ppp = path / '6_Processamento_PPP'
        path_pre = path / '7_Processamento_TBC_RBMC'
        for child in path_ppp.iterdir():
            if child.suffix == '.pdf':
                files.append(child)
        
        # Checks if files exists
        
        # for root, dirs, files in os.walk(folder):
        #     for f in files:
        #         if f.endswith(".csv"):
        #             with open(os.path.join(root, f)) as csv_file:
        #                 csv_reader = csv.DictReader(csv_file)
        #                 for row in csv_reader:
        #                     gerenatezip(root, f)
        #                     points += "'{}',".format(row['cod_ponto'])
        # return "WHERE cod_ponto IN ({})".format(points[:-1])