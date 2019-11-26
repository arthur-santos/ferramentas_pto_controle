# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Atualiza banco de dados de ponto de controle
Description          : Atualiza a situação dos pontos medidos no banco de dados de ponto de controle
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
##DSG=group
##servidor=string
##porta=string
##nome_bd=string
##usuario=string
##senha=string
##pasta=folder

import os
import sys
import csv
import psycopg2
from pathlib import Path


class AtualizaBD():
    def __init__(self, pasta, servidor, porta, nome_bd, usuario, senha):
        self.pasta = pasta
        conn_string = "host='{0}' port='{1}' dbname='{2}' user='{3}' password='{4}'".format(
            servidor, porta, nome_bd, usuario, senha)
        self.conn = psycopg2.connect(conn_string)
        self.cursor = self.conn.cursor()

    def getPontosFromCSV(self):
        pontos = []
        for root, dirs, files in os.walk(self.pasta):
            for f in files:
                if f.endswith(".csv"):
                    with open(os.path.join(root, f)) as csv_file:
                        csv_reader = csv.DictReader(csv_file)
                        for row in csv_reader:
                            aux = {}
                            if "cod_ponto" in row:
                                aux["cod_ponto"] = row["cod_ponto"]
                            if "operador_levantamento" in row:
                                aux["operador_levantamento"] = row["operador_levantamento"]
                            if "data" in row:
                                aux["data"] = row["data"]
                            pontos.append(aux)
        return pontos

    def atualiza(self, pontos):
        rowcount = 0
        for ponto in pontos:
            if "cod_ponto" in ponto and "operador_levantamento" in ponto and "data" in ponto:
                self.cursor.execute(u"""
                    UPDATE controle.ponto_controle_p
                    SET medidor = %s, data_medicao = %s, tipo_situacao_id = 4
                    WHERE nome = %s AND (tipo_situacao_id = 1 OR tipo_situacao_id = 2 OR tipo_situacao_id = 3 OR tipo_situacao_id = 6);
                """, (ponto["operador_levantamento"], ponto["data"], ponto["cod_ponto"]))
                if self.cursor.rowcount == 0:
                    print('O ponto {0} nao esta presente no banco de dados ou teve medição duplicada.'.format(
                        ponto["cod_ponto"]))
                else:
                    rowcount += self.cursor.rowcount
        self.conn.commit()
        return rowcount


if __name__ == '__builtin__':

    from qgis.gui import QgsMessageBar
    from qgis.core import QgsMessageLog
    from qgis.utils import iface

    try:
        atualiza_db = AtualizaBD(
            pasta, servidor, porta, nome_bd, usuario, senha)
        pontos = atualiza_db.getPontosFromCSV()
        atualiza_db.atualiza(pontos)
        iface.messageBar().pushMessage(u'Situacao', "Banco de dados atualizado com sucesso",
                                       level=QgsMessageBar.INFO, duration=20)
    except Exception as e:
        QgsMessageLog.logMessage(u"Erro: {0}".format(
            e), tag="Atualiza banco de dados", level=QgsMessageLog.CRITICAL)
        iface.messageBar().pushMessage(u'Situacao', "Erro na execução do script.",
                                       level=QgsMessageBar.CRITICAL, duration=20)


if __name__ == '__main__':
    if len(sys.argv) >= 6:
        atualiza_db = AtualizaBD(sys.argv[1], sys.argv[2],
                                sys.argv[3], sys.argv[4],
                                sys.argv[5], sys.argv[6])

        pontos = atualiza_db.getPontosFromCSV()
        total = atualiza_db.atualiza(pontos)
        print(u'Foram atualizados {0} pontos de controle!'.format(total))
    else:
        print(u'Parametros incorretos!')

