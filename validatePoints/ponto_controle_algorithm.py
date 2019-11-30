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

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import re
from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterType)
from qgis.PyQt.QtCore import QCoreApplication
from .valida_estrutura_pto_controle import EvaluateStructure


class PontoControleAlgorithm(QgsProcessingAlgorithm):
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
    OPERATORS = 'OPERATORS'
    DATE = 'DATE'
    FUSE = 'FUSE'
    FILE_DST = 'FILE_DST'

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

        param = ValidationString(
            self.OPERATORS,
            description=self.tr(
                'Insert the operators\'s names, separated by ;')
        )
        self.addParameter(param)

        self.addParameter(
            QgsProcessingParameterString(
                self.DATE,
                self.tr('Insert the date')
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.FUSE,
                self.tr('Insert the fuse'),
                defaultValue=-3
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.FILE_DST,
                self.tr('Insert the output folder')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        folder = self.parameterAsFile(parameters, self.FOLDER, context)
        operators = self.parameterAsString(parameters, self.OPERATORS, context)
        date = self.parameterAsString(parameters, self.DATE, context)
        fuse = self.parameterAsInt(parameters, self.OPERATORS, context)
        file_dst = self.parameterAsFileOutput(
            parameters, self.FILE_DST, context)

        evaluate = EvaluateStructure(
            folder, operators, date, fuse, ignora_processamento=True)
        results = evaluate.evaluate()
        with open(file_dst, 'w') as f:
            erros_text = "\n".join(results)
            f.write(erros_text)

        return {self.OUTPUT: results}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '2- Data Validation'

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
        return PontoControleAlgorithm()


class ValidationString(QgsProcessingParameterString):
    '''
    Auxiliary class for pre validation on measurer's names.
    '''
    #__init__ not necessary
    def __init__(self, name, description=''):
        super().__init__(name, description)

    def checkValueIsAcceptable(self, value, context=None):
        if re.match(r'([a-z]+)(?:;|$)', value):
            return True
