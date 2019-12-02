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

import os
import sys
import csv
import psycopg2
import re
import pyproj


class HandleRefreshDB():
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

    def getCoordsFromRinex(self):
        points = []
        coords = []
        for root, dirs, files in os.walk(self.pasta):
            for f in files:
                if f.endswith('.csv'):
                    with open(os.path.join(root, f)) as csv:
                        csv_reader = csv.DictReader(csv)
                        for row in csv_reader:
                            aux = {}
                            if "cod_ponto" in row:
                                aux["cod_ponto"] = row["cod_ponto"]
                            if "operador_levantamento" in row:
                                aux["operador_levantamento"] = row["operador_levantamento"]
                            if "data" in row:
                                aux["data"] = row["data"]
                            points.append(aux)
                if re.search(r'.[0-9][0-9]o$', f):
                    with open(os.path.join(root, f)) as rinex:
                        lines = rinex.readlines()
                        point = lines[4].split(' ')[0]
                        x, y, z = lines[8].strip().split(' ')[0:3]
                        results = transform(x, y, z)
                        aux = {}
                        aux['nome'] = point
                        aux['lat'] = results[0]
                        aux['lon'] = results[1]
                        coords.append(aux)
                        

    def insertPoints(self, pontos):
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

    def checkPoints(self):
        self.cursor.execute(u"""
        INSERT INTO controle.pto_controle_p (POINT, ...DATA)
        VALUES ({0}, {1})
        ON CONFLIT (POINT)
        DO
        UPDATE
            SET medidor = %s, data_medicao = %s, tipo_situacao_id = 4
            WHERE nome = %s AND (tipo_situacao_id = 1 OR tipo_situacao_id = 2 OR tipo_situacao_id = 3 OR tipo_situacao_id = 6);
        """.format())
        points = self.cursor.fetchall()
        print(points)

    def upinsert(self):
        cursor = self.conn.cursor()
        cursor.execute(u"""
        SELECT nome FROM controle.ponto_controle_p
        """)
        points = self.cursor.fetchall()
        print(points)

def transform (x, y, z):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    return pyproj.transform(ecef, lla, x, y, z, radians=False)

if __name__ == '__main__':
    atualiza_db = AtualizaBD(sys.argv[1], sys.argv[2],
                            sys.argv[3], sys.argv[4],
                            sys.argv[5], sys.argv[6])
    atualiza_db.getCoordsFromRinex()
    # if len(sys.argv) >= 6:
    #     atualiza_db = AtualizaBD(sys.argv[1], sys.argv[2],
    #                             sys.argv[3], sys.argv[4],
    #                             sys.argv[5], sys.argv[6])

    #     pontos = atualiza_db.getPontosFromCSV()
    #     total = atualiza_db.atualiza(pontos)
    #     print(u'Foram atualizados {0} pontos de controle!'.format(total))
    # else:
    #     print(u'Parametros incorretos!')

