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

    def getPointsFromCSV(self):
        ''' 
        Gets every row from CSV to prepare the commit on database 
        '''
        points = []
        for root, dirs, files in os.walk(self.pasta):
            for f in files:
                if f.endswith(".csv"):
                    with open(os.path.join(root, f)) as csv_file:
                        csv_reader = csv.DictReader(csv_file)
                        for row in csv_reader:
                            points.append(row)
        return createTimeStamp(points)

    def getCoordsFromRinex(self, points):
        '''
        Reads RINEX and gets coordinates
        '''
        for root, dirs, files in os.walk(self.pasta):
            for f in files:
                if re.search(r'.[0-9][0-9]o$', f):
                    with open(os.path.join(root, f)) as rinex:
                        lines = rinex.readlines()
                        point_name = lines[4].split(' ')[0]
                        x, y, z = lines[8].strip().split(' ')[0:3]
                        results = transform(x, y, z)
                        for point in points:
                            if point['cod_ponto'] == point_name:
                                point['latitude'], point['longitude'], point['altitude_ortometrica'] = results
        return points

    def upsert(self, points):
        for point in points:
            str_key = ''
            str_value = ''
            lista = list(point.items())
            print(lista[0])
            for key, value in lista:
                str_key += '{},'.format(key)
                str_value += "'{}',".format(value)
            self.cursor.execute(u"""
            INSERT INTO bpc.ponto_controle_p ({keys}, geom)
            VALUES ({values}, ST_GeomFromText('POINT({latitude} {longitude})', 4674))
            ON CONFLICT (cod_ponto)
            DO
            UPDATE
                SET medidor = '{medidor}', tipo_situacao = 2
                WHERE ponto_controle_p.cod_ponto = '{cod_ponto}' AND (ponto_controle_p.tipo_situacao = 1 OR ponto_controle_p.tipo_situacao = 2 OR ponto_controle_p.tipo_situacao = 3);
            """.format(keys=str_key[:-1], values=str_value[:-1], **point))
        self.conn.commit()


    def fetch(self):
        cursor = self.conn.cursor()
        cursor.execute(u"""
        SELECT nome FROM controle.ponto_controle_p
        """)
        points = self.cursor.fetchall()
        print(points)

def createTimeStamp(points):
    for point in points:
        point['inicio_rastreio'] = '{} {} {}'.format(point['data_visita'], point['inicio_rastreio'], -3)
        point['fim_rastreio'] = '{} {} {}'.format(point['data_visita'], point['fim_rastreio'], -3)
        point['altura_antena'] = point['altura_antena'].replace(',', '.')
        point['altura_objeto'] = point['altura_objeto'].replace(',', '.')
    return points

def transform(x, y, z):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    return pyproj.transform(ecef, lla, x, y, z, radians=False)

if __name__ == '__main__':
    atualiza_db = HandleRefreshDB(sys.argv[1], sys.argv[2],
                                  sys.argv[3], sys.argv[4],
                                  sys.argv[5], sys.argv[6])
    points = atualiza_db.getPointsFromCSV()
    points2 = atualiza_db.getCoordsFromRinex(points)
    atualiza_db.upsert(points2)
