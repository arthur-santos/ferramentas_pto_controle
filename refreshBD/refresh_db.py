# -*- coding: utf-8 -*-

"""
/***************************************************************************
 PontoControle
                                 A QGIS plugin
 Ferramentas para a gerência de pontos de controle
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
__revision__ = '$Format:%H$'

from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean)
from qgis.PyQt.QtCore import QCoreApplication
from .wrapper import MyWidgetWrapper
from .atualiza_bd import AtualizaBD


class RefreshBD(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    OUTPUT = 'OUTPUT'
    FOLDER = 'FOLDER'
    SERVERIP = 'SERVERIP'
    PORT = 'PORT'
    BDNAME = 'BDNAME'
    USER = 'USER'
    PASSWORD = 'PASSWORD'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER,
                self.tr('Insert Folder'),
                behavior=QgsProcessingParameterFile.Folder
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.SERVERIP,
                self.tr('Insert the machine\'s ip')
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.PORT,
                self.tr('Insert the port')
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.BDNAME,
                self.tr('Insert the DB name'),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.USER,
                self.tr('Insert the username'),
            )
        )

        password = QgsProcessingParameterString(
                self.PASSWORD,
                self.tr('Insert the password'),
            )
        password.setMetadata({
            'widget_wrapper': 'ferramentas_pto_controle.refreshBD.wrapper.MyWidgetWrapper'}
        )

        self.addParameter(password)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        folder = self.parameterAsFile(parameters, self.FOLDER, context)
        server_ip = self.parameterAsString(parameters, self.SERVERIP, context)
        port = self.parameterAsInt(parameters, self.PORT, context)
        bdname = self.parameterAsString(parameters, self.BDNAME, context)
        user = self.parameterAsString(parameters, self.USER, context)
        password = self.parameterAsString(parameters, self.PASSWORD, context)

        refresh = AtualizaBD(folder, server_ip, port, bdname, user, password)
        points = refresh.getPontosFromCSV()
        refresh.atualiza(points)

        return {self.OUTPUT: ''}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '3- Refresh DB'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return None

    def shortHelpString(self):
        """
        Retruns a short helper string for the algorithm
        """
        return self.tr('Insert description here!')

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RefreshBD()
