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


def getPointsFromCSV(folder):
    points = ''
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith(".csv"):
                with open(os.path.join(root, f)) as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        points += "'{}',".format(row['cod_ponto'])
    return "WHERE cod_ponto IN ({})".format(points[:-1])
