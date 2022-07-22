# -*- coding: utf-8 -*-

"""
/***************************************************************************
 PontoControle
                                 A QGIS plugin
 Ferramentas para a gerência de pontos de controle
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-11-18
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
__date__ = '2019-11-18'
__copyright__ = '(C) 2019 by 1CGEO/DSG'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import csv
import sys
import codecs
import json
from os import listdir, sep
from os.path import isdir, isfile, join
from re import search
from datetime import datetime
from pathlib import Path


class EvaluateStructure():
    def __init__(self, pasta, medidores, data, fuso_horario, ignora_processamento, settings):
        self.erros = []
        self.pasta = pasta
        self.medidores = medidores.split(";")
        self.data = data
        self.fuso_horario = int(fuso_horario)
        self.ignora_processamento = ignora_processamento
        with open(settings) as setting:
            self.rules = json.load(setting)
        self.rinex_data = {}
        self.csv_data = {}

    def evaluate(self):
        self.erros += self.no_files(self.pasta)
        subpastas = [f for f in listdir(
            self.pasta) if isdir(join(self.pasta, f))]
        if len(subpastas) < 1:
            self.erros.append(
                u"A pasta {0} deveria ter subpastas.".format(self.pasta))
        else:
            for p in subpastas:
                if p not in [u"{0}_{1}".format(m, self.data) for m in self.medidores]:
                    if not self.ignora_processamento or p != "_Revisao":
                        self.erros.append(
                            u"A pasta {0}{1}{2} não segue o padrão de nomenclatura (medidor_YYYY-MM-DD).".format(self.pasta, sep, p))
                else:
                    erros_pasta = self.evaluate_first_level(
                        join(self.pasta, p))

                    erros_pasta += self.compare_csv_rinex(join(self.pasta, p))
                    self.rinex_data = {}
                    self.csv_data = {}

                    if len(erros_pasta) == 0:
                        self.erros.append(
                            u"A pasta {0}{1}{2} não contém erros.".format(self.pasta, sep, p))
                    else:
                        self.erros += erros_pasta
                self.erros.append(u"\n")

        return self.erros

    def evaluate_first_level(self, pasta):
        erros = []
        ptos_csv = []
        ptos_pasta = []

        medidor, data = pasta.split(sep)[-1].split("_")
        csv_name = "metadados_{0}_{1}.csv".format(medidor, data)
        files = [f for f in listdir(pasta) if isfile(join(pasta, f))]

        if csv_name in files:
            erros += self.evaluate_csv(pasta, csv_name)
            csv_data = self.get_data_csv(pasta, csv_name)
            ptos_csv = [x["cod_ponto"] for x in csv_data]
            for pto in csv_data:
                self.csv_data[pto["cod_ponto"]] = pto
        else:
            erros.append(u"A pasta {0} deveria conter o arquivo CSV de informações dos pontos do dia (metadados_{1}_{2}.csv).".format(
                pasta, medidor, data))

        if len(set(files).difference([csv_name, "Thumbs.db", "desktop.ini"])) > 0:
            for f in set(files).difference([csv_name]):
                erros.append(
                    u"A pasta {0} não deveria conter o arquivo {1}.".format(pasta, f))

        subpastas = [f for f in listdir(pasta) if isdir(join(pasta, f))]

        if len(subpastas) < 1:
            erros.append(u"A pasta {0} deveria ter subpastas.".format(pasta))
        else:
            for p in subpastas:
                if self.evaluate_nome_ponto(p):
                    ptos_pasta.append(p)
                    erros += self.evaluate_second_level(
                        join(pasta, p), p, data)
                else:
                    erros.append(
                        u"A pasta {0}{1}{2} não segue o padrão de nomenclatura para pontos de controle.".format(pasta, sep, p))
            for pto in set(ptos_pasta).difference(ptos_csv):
                erros.append(
                    u"{0} CSV - O ponto {1} possui pasta porém não está presente no CSV.".format(pasta, pto))
            for pto in set(ptos_csv).difference(ptos_pasta):
                erros.append(
                    u"{0} CSV - O ponto {1} está presente no CSV porém não possui pasta.".format(pasta, pto))
        return erros

    def evaluate_second_level(self, pasta, pto, data):
        erros = []
        erros += self.no_files(pasta)
        subpastas = [f for f in listdir(pasta) if isdir(join(pasta, f))]

        if self.ignora_processamento:
            if "6_Processamento_PPP" in subpastas:
                subpastas.remove("6_Processamento_PPP")

        pastas_incorretas = set(subpastas).difference(
            ["1_Formato_Nativo", "2_RINEX", "3_Foto_Rastreio", "4_Croqui", "5_Foto_Auxiliar"])
        pastas_faltando = set(["1_Formato_Nativo", "2_RINEX",
                               "3_Foto_Rastreio", "4_Croqui"]).difference(subpastas)
        pastas_ok = set(["1_Formato_Nativo", "2_RINEX", "3_Foto_Rastreio",
                         "4_Croqui", "5_Foto_Auxiliar"]).intersection(subpastas)

        if len(pastas_incorretas) > 0:
            for p in pastas_incorretas:
                erros.append(
                    u"A pasta {0}{1}{2} não está prevista para estar na estrutura.".format(pasta, sep, p))

        if len(pastas_faltando) > 0:
            for p in pastas_faltando:
                erros.append(
                    u"A pasta {0} deveria ter a subpasta {1}.".format(pasta, p))

        if "1_Formato_Nativo" in pastas_ok:
            erros += self.evaluate_formato_nativo(
                join(pasta, "1_Formato_Nativo"), pto)
        if "2_RINEX" in pastas_ok:
            erros += self.evaluate_rinex(join(pasta, "2_RINEX"), pto, data)
        if "3_Foto_Rastreio" in pastas_ok:
            erros += self.evaluate_foto_rastreio(
                join(pasta, "3_Foto_Rastreio"), pto)
        if "4_Croqui" in pastas_ok:
            erros += self.evaluate_croqui(join(pasta, "4_Croqui"), pto)
        if "5_Foto_Auxiliar" in pastas_ok:
            erros += self.evaluate_foto_auxiliar(
                join(pasta, "5_Foto_Auxiliar"), pto)

        return erros

    @staticmethod
    def no_files(pasta):
        erros = []
        files = [f for f in listdir(pasta) if isfile(
            join(pasta, f)) and f != "Thumbs.db" and f != "desktop.ini"]
        if len(files) > 0:
            for f in files:
                try:
                    erros.append(
                        u"A pasta {0} não deve conter o arquivo {1}.".format(pasta, f))
                except:
                    pass

        return erros

    @staticmethod
    def no_folders(pasta):
        erros = []
        subpastas = [f for f in listdir(pasta) if isdir(join(pasta, f))]
        if len(subpastas) > 0:
            for s in subpastas:
                erros.append(
                    u"A pasta {0} não deve conter a subpasta {1}.".format(pasta, s))
        return erros

    @staticmethod
    def evaluate_nome_ponto(nome):
        pto_regex = "^[A-Z][A-Z]-(HV|Base)-[1-9]+[0-9]*$"
        if search(pto_regex, nome):
            return True
        else:
            return False

    def evaluate_csv(self, pasta, nome):
        erros = []

        data = nome[:-4].split("_")[-1]

        # Padronized CSV based on SQL. Contains every field from SQL + fuso_horario + data_rastreio
        fields = ["cod_ponto", "medidor", "tipo_ref", "latitude", "longitude", "meridiano_central", "fuso", "norte", "leste"
                  "altitude_ortometrica", "altitude_geometrica", "sistema_geodesico", "outra_ref_plan", "referencial_altim", "outro_ref_alt", "data_rastreio",
                  "tipo_situacao", "reserva", "lote", "latitude_planejada", "longitude_planejada", "fuso_horario", "precisao_vertical_esperada",
                  "inicio_rastreio", "fim_rastreio", "classificacao_ponto", "metodo_posicionamento", "ponto_base", "materializado", "altura_antena",
                  "tipo_medicao_altura", "referencia_medicao_altura", "altura_objeto", "mascara_elevacao", "taxa_gravacao", "modelo_gps", "modelo_antena", "numero_serie_gps",
                  "numero_serie_antena", "modelo_geoidal", "precisao_horizontal_esperada", "freq_processada", "data_processamento", "orbita", "orgao_executante", "observacao",
                  "projeto", "engenheiro_responsavel", "crea_engenheiro_responsavel", "geometria_aproximada", "tipo_pto_ref_geod_topo", "tipo_marco_limite", "rede_referencia",
                  "referencial_grav", "situacao_marco", "data_visita", "valor_gravidade", "monografia", "numero_fotos", "possui_croqui", "possui_arquivo_rastreio"]

        # Columns required for validation
        required = ["cod_ponto", "medidor", "data_rastreio", "inicio_rastreio", "fim_rastreio", "observacao", "materializado", "altura_antena",
                    "tipo_medicao_altura", "referencia_medicao_altura", "altura_objeto", "numero_serie_gps", "numero_serie_antena"]

        optional = ["tipo_ref", "meridiano_central", "fuso", "sistema_geodesico", "outra_ref_plan", "fuso_horario", "precisao_vertical_esperada",
                    "referencial_altim", "outro_ref_alt", "reserva", "lote", "latitude_planejada", "longitude_planejada", "metodo_posicionamento",
                    "ponto_base", "mascara_elevacao", "taxa_gravacao", "modelo_gps", "modelo_antena", "modelo_geoidal", "precisao_horizontal_esperada",
                    "orgao_executante", "projeto", "engenheiro_responsavel", "crea_engenheiro_responsavel", "geometria_aproximada", "tipo_pto_ref_geod_topo",
                    "tipo_marco_limite", "rede_referencia", "referencial_grav", "situacao_marco", "data_visita", "valor_gravidade", "classificacao_ponto"]

        ptos = []

        with open(join(pasta, nome), encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            headers = csv_reader.fieldnames
            if set(headers).difference(required):
                for col in set(headers).difference(required):
                    if col in optional:
                        erros.append(
                            u"{0} CSV - A coluna {1} existe no CSV, mas não é obrigatória. Só a utilize caso seu projeto necessite deste campo ou se o campo não for generalizável com o atributo default do JSON".format(pasta, col))
                    else:
                        erros.append(
                            u"{0} CSV - A coluna {1} está presente no CSV porém não é padrão.".format(pasta, col))
            if set(required).difference(headers):
                for col in set(required).difference(headers):
                    erros.append(
                        u"{0} CSV - A coluna {1} não está presente no CSV.".format(pasta, col))

            for row in csv_reader:
                if "inicio_rastreio" in row and "fim_rastreio" in row:
                    try:
                        tdelta = self.parse_date(
                            row["fim_rastreio"]) - self.parse_date(row["inicio_rastreio"])
                        minutes = tdelta.seconds/60
                        if minutes < self.rules['validacao']['dur_min']:
                            erros.append(u"{0} CSV - O ponto {1} foi medido por menos de {3} min ({2} min).".format(
                                pasta, row["cod_ponto"], minutes, self.rules['validacao']['dur_min']))
                    except Exception as e:
                        erros.append(
                            u"{0} CSV - O ponto {1} possui valores invalidos para inicio_rastreio ou fim_rastreio.".format(pasta, row["cod_ponto"]))
                if "altura_antena" in row:
                    try:
                        altura = float(row["altura_antena"].replace(',', '.'))
                        if altura > self.rules['validacao']['alt_max_ant']:
                            erros.append(u"{0} CSV - O ponto {1} possui altura maior que {3} metros ({2}).".format(
                                pasta, row["cod_ponto"], row["altura_antena"], self.rules['alt_max_ant']))
                    except:
                        erros.append(u"{0} CSV - O ponto {1} possui valores inválidos para altura da antena ({2}).".format(
                            pasta, row["cod_ponto"], row["altura_antena"]))
                if "altura_antena" in row and "altura_objeto" in row:
                    try:
                        altura_antena = float(
                            row["altura_antena"].replace(',', '.'))
                        altura_objeto = float(
                            row["altura_objeto"].replace(',', '.'))
                        if altura_objeto > altura_antena:
                            erros.append(u"{0} CSV - O ponto {1} possui altura do objeto ({2}) maior que a altura da antena ({3}).".format(
                                pasta, row["cod_ponto"], row["altura_objeto"], row["altura_antena"]))
                    except:
                        erros.append(u"{0} CSV - O ponto {1} possui valores inválidos para altura do objeto ({2}) ou da antena ({3}).".format(
                            pasta, row["cod_ponto"], row["altura_objeto"], row["altura_antena"]))

                if "cod_ponto" in row:
                    if row["cod_ponto"] in ptos:
                        erros.append(
                            u"{0} CSV - O ponto {1} está duplicado no CSV.".format(pasta, row["cod_ponto"]))
                    else:
                        ptos.append(row["cod_ponto"])
                if "data_rastreio" in row:
                    if row["data_rastreio"] != data:
                        erros.append(
                            u"{0} CSV - Data do ponto {1} esta incompativel.".format(pasta, row["cod_ponto"]))
        return erros

    @staticmethod
    def get_data_csv(pasta, nome):
        ptos = []
        with open(join(pasta, nome)) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                aux = {}
                if "cod_ponto" in row:
                    aux["cod_ponto"] = row["cod_ponto"]
                if "numero_serie_gps" in row:
                    aux["numero_serie_gps"] = row["numero_serie_gps"]
                if "numero_serie_antena" in row:
                    aux["numero_serie_antena"] = row["numero_serie_antena"]
                if "inicio_rastreio" in row:
                    aux["inicio_rastreio"] = row["inicio_rastreio"]
                if "fim_rastreio" in row:
                    aux["fim_rastreio"] = row["fim_rastreio"]
                if "data_rastreio" in row:
                    aux["data_rastreio"] = row["data_rastreio"]
                if "altura_antena" in row:
                    aux["altura_antena"] = row["altura_antena"]
                ptos.append(aux)
        return ptos

    @staticmethod
    def get_rinex_data(pasta, nome):
        rinex_info = {}
        with open(join(pasta, nome)) as rinex_file:
            lines = rinex_file.readlines()
            rinex_info["cod_ponto_1"] = lines[3].split(' ')[0]
            rinex_info["cod_ponto_2"] = lines[4].split(' ')[0]
            rinex_info["nr_serie_receptor"] = lines[6].split(' ')[0]
            rinex_info["modelo_receptor"] = [
                x for x in lines[6].split('  ') if x][1].strip()
            rinex_info["nr_serie_antena"] = lines[7].split(' ')[0].strip()
            if "NONE" in lines[7]:
                rinex_info["modelo_none"] = True
            else:
                rinex_info["modelo_none"] = False
            rinex_info["modelo_antena"] = [
                x for x in lines[7].split('  ') if x][1].strip()
            rinex_info["altura_antena"] = lines[9].strip().split(' ')[0]
            aux_inicio = [x for x in lines[12].strip().split(' ') if x]
            rinex_info["data_rastreio_1"] = "{0}-{1}-{2}".format(
                aux_inicio[0], aux_inicio[1].zfill(2), aux_inicio[2].zfill(2))
            rinex_info["hora_inicio_rastreio"] = "{0}:{1}".format(
                aux_inicio[3], aux_inicio[4])
            aux_fim = [x for x in lines[13].strip().split(' ') if x]
            rinex_info["data_rastreio_2"] = "{0}-{1}-{2}".format(
                aux_fim[0], aux_fim[1].zfill(2), aux_fim[2].zfill(2))
            rinex_info["hora_fim_rastreio"] = "{0}:{1}".format(
                aux_fim[3], aux_fim[4])

        return rinex_info

    @staticmethod
    def parse_date(text):
        for fmt in ('%H:%M', '%H:%M:00'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    def evaluate_formato_nativo(self, pasta, pto):
        erros = []
        erros += self.no_folders(pasta)
        files = [f.replace(".DAT", ".dat").replace(".T01", ".t01")
                 for f in listdir(pasta) if isfile(join(pasta, f))]
        arquivos_incorretos = set(files).difference(
            ["{0}.dat".format(pto), "{0}.t01".format(pto), "desktop.ini"])
        arquivos_faltando = set(["{0}.t01".format(pto)]).difference(files)
        if len(arquivos_incorretos) > 0:
            for a in arquivos_incorretos:
                erros.append(
                    u"A pasta {0} não deve conter o arquivo {1}.".format(pasta, a))
        if len(arquivos_faltando) > 0:
            for a in arquivos_faltando:
                erros.append(
                    u"A pasta {0} deve conter o arquivo {1}.".format(pasta, a))
        return erros

    def evaluate_rinex(self, pasta, pto, data):
        erros = []
        erros += self.no_folders(pasta)
        ano = data[2:4]
        files = [f for f in listdir(pasta) if isfile(join(pasta, f))]

        if self.ignora_processamento and '{0}.zip'.format(pto) in files:
            files.remove('{0}.zip'.format(pto))

        arquivos_incorretos = set(files).difference(
            ["{0}.{1}n".format(pto, ano), "{0}.{1}o".format(pto, ano), "desktop.ini"])
        arquivos_faltando = set(
            ["{0}.{1}n".format(pto, ano), "{0}.{1}o".format(pto, ano)]).difference(files)
        if len(arquivos_incorretos) > 0:
            for a in arquivos_incorretos:
                erros.append(
                    u"A pasta {0} não deve conter o arquivo {1}.".format(pasta, a))
        if len(arquivos_faltando) > 0:
            for a in arquivos_faltando:
                erros.append(
                    u"A pasta {0} deve conter o arquivo {1}.".format(pasta, a))
        else:
            rinex_name = "{0}.{1}o".format(pto, ano)
            self.rinex_data[pto] = self.get_rinex_data(pasta, rinex_name)

        return erros

    def evaluate_foto_rastreio(self, pasta, pto):
        erros = []
        erros += self.no_folders(pasta)
        files = [f for f in listdir(pasta) if isfile(join(pasta, f))]
        fotos_ok = []
        foto_regex = "^{0}_(360|3[0-5][0-9]|[0-2][0-9][0-9])_FOTO.(jpg|JPG|jpeg|JPEG)$".format(pto)

        for f in files:
            if search(foto_regex, f):
                fotos_ok.append(f)
            elif f == "Thumbs.db" or f == "desktop.ini":
                pass
            else:
                erros.append(
                    u"A pasta {0} não deve conter o arquivo {1}.".format(pasta, f))

        if len(fotos_ok) != 4:
            erros.append(
                u"A pasta {0} deve conter exatamente 4 fotos.".format(pasta))

        return erros

    def evaluate_foto_auxiliar(self, pasta, pto):
        erros = []
        erros += self.no_folders(pasta)
        files = [f for f in listdir(pasta) if isfile(join(pasta, f))]
        foto_regex = r"^{0}_\d+_FOTO_AUX.(jpg|JPG|jpeg|JPEG)$".format(pto)
        for f in files:
            if search(foto_regex, f):
                pass
            elif f == "Thumbs.db" or f == "desktop.ini":
                pass
            else:
                erros.append(
                    u"A pasta {0} não deve conter o arquivo {1}.".format(pasta, f))

        return erros

    def evaluate_croqui(self, pasta, pto):
        erros = []
        erros += self.no_folders(pasta)
        files = [f.replace(".JPG", ".jpg").replace(".JPEG", ".jpg").replace(".jpeg", ".jpg")
                 for f in listdir(pasta) if isfile(join(pasta, f))]
        arquivos_incorretos = set(files).difference(
            ["Thumbs.db", "desktop.ini", "{0}_CROQUI.jpg".format(pto)])
        arquivos_faltando = set(
            ["{0}_CROQUI.jpg".format(pto)]).difference(files)
        if len(arquivos_incorretos) > 0:
            for a in arquivos_incorretos:
                erros.append(
                    u"A pasta {0} não deve conter o arquivo {1}.".format(pasta, a))
        if len(arquivos_faltando) > 0:
            for a in arquivos_faltando:
                erros.append(
                    u"A pasta {0} deve conter o arquivo {1}.".format(pasta, a))
        return erros

    def compare_csv_rinex(self, pasta):
        erros = []
        for key in self.rinex_data:
            if self.rinex_data[key]['modelo_none']:
                erros.append(u"{0}: O arquivo RINEX do ponto {1} contém NONE no modelo da antena.".format(
                    pasta, self.rinex_data[key]["cod_ponto_1"]))

        for key in self.csv_data:
            if key in self.rinex_data:
                if self.rinex_data[key]["cod_ponto_1"] != self.csv_data[key]["cod_ponto"] or self.rinex_data[key]["cod_ponto_2"] != self.csv_data[key]["cod_ponto"]:
                    erros.append(u"{0}: O arquivo RINEX do ponto {1} está com o nome de ponto incorreto.".format(
                        pasta, self.csv_data[key]["cod_ponto"]))

                if self.rinex_data[key]["nr_serie_receptor"] != self.csv_data[key]["numero_serie_gps"]:
                    erros.append(u"{0}: O arquivo RINEX do ponto {1} está com o número de série do receptor diferente do CSV.".format(
                        pasta, self.csv_data[key]["cod_ponto"]))

                if self.rinex_data[key]["nr_serie_antena"] != self.csv_data[key]["numero_serie_antena"]:
                    erros.append(u"{0}: O arquivo RINEX do ponto {1} está com o número de série da antena diferente do CSV.".format(
                        pasta, self.csv_data[key]["cod_ponto"]))

                if self.rinex_data[key]["data_rastreio_1"] != self.csv_data[key]["data_rastreio"] or self.rinex_data[key]["data_rastreio_2"] != self.csv_data[key]["data_rastreio"]:
                    erros.append(u"{0}: O arquivo RINEX do ponto {1} está com a data de rastreio incorreta.".format(
                        pasta, self.csv_data[key]["cod_ponto"]))

                altura_rinex = float(
                    self.rinex_data[key]["altura_antena"].replace(',', '.'))
                altura_csv = float(
                    self.csv_data[key]["altura_antena"].replace(',', '.'))
                if abs(altura_rinex - altura_csv) > 0.01:
                    erros.append(u"{0}: O arquivo RINEX do ponto {1} está com a altura antena diferente do CSV.".format(
                        pasta, self.csv_data[key]["cod_ponto"]))

                try:
                    tdelta = self.parse_date(self.rinex_data[key]["hora_fim_rastreio"]) - self.parse_date(
                        self.rinex_data[key]["hora_inicio_rastreio"])
                    minutes = tdelta.seconds/60
                    if minutes < self.rules['validacao']['dur_min']:
                        erros.append(u"{0} RINEX - O ponto {1} foi medido por menos de {3} min ({2} min).".format(
                            pasta, self.csv_data[key]["cod_ponto"], minutes, self.rules['validacao']['dur_min']))
                    else:
                        delta_rinex_csv_i = self.parse_date(
                            self.rinex_data[key]["hora_inicio_rastreio"]) - self.parse_date(self.csv_data[key]["inicio_rastreio"])
                        delta_rinex_csv_f = self.parse_date(
                            self.rinex_data[key]["hora_fim_rastreio"]) - self.parse_date(self.csv_data[key]["fim_rastreio"])

                        minutes_i = delta_rinex_csv_i.seconds/60 + 60*self.fuso_horario
                        minutes_f = delta_rinex_csv_f.seconds/60 + 60*self.fuso_horario

                        if abs(minutes_i) > 5:
                            erros.append(u"{0} - O ponto {1} tem diferença maior que 5 min entre o RINEX e o CSV para a hora_inicio_rastreio".format(
                                pasta, self.csv_data[key]["cod_ponto"]))
                        if abs(minutes_f) > 5:
                            erros.append(u"{0} - O ponto {1} tem diferença maior que 5 min entre o RINEX e o CSV para a hora_fim_rastreio".format(
                                pasta, self.csv_data[key]["cod_ponto"]))

                except Exception:
                    erros.append(u"{0} RINEX - O ponto {1} está possui valores inválidos para fim_rastreio ou inicio_rastreio".format(
                        pasta, self.csv_data[key]["cod_ponto"]))

            else:
                erros.append(u"{0}: Não foi encontrado informações do RINEX compatíveis com o ponto {1}.".format(
                    pasta, self.csv_data[key]["cod_ponto"]))
        return erros
