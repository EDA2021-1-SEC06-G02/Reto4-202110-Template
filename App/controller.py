"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

import config as cf
import model
import csv


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo del analizador

def newAnalyzer():
    return model.newAnalyzer()

# Funciones para la carga de datos

def loadData(analyzer):
    Primer_elemento=True
    File = "connections.csv"
    File2= "countries.csv"
    File3= "landing_points.csv"
    File = cf.data_dir + File
    File2 = cf.data_dir + File2
    File3 = cf.data_dir + File3
    input_file = csv.DictReader(open(File2, encoding="utf-8"), delimiter=",")
    for Entry in input_file:
        model.AddCountry(analyzer, Entry)
        InfoUltimo=Entry
    input_file = csv.DictReader(open(File3, encoding="utf-8"), delimiter=",")
    for Entry in input_file:
        model.AddLandingPointsData(analyzer, Entry)
        if Primer_elemento==True:
            InfoPrimero=Entry
            Primer_elemento = False
    input_file = csv.DictReader(open(File, encoding="utf-8-sig"), delimiter=",")
    for Entry in input_file:
        model.addLandingConnection(analyzer, Entry)
    model.addRouteConnections(analyzer)
    #model.addInternalConnections(analyzer)
    InfoPrimerLanding="Identificador: "+InfoPrimero['landing_point_id']+". Nombre: "+InfoPrimero['name']+". Latitud: "+InfoPrimero['latitude']+". Longitud: "+InfoPrimero['longitude']
    InfoUltimoPais="Pais: "+InfoUltimo['CountryName']+". Población: "+InfoUltimo['Population']+". Usuarios Internet: "+InfoUltimo['Internet users']
    return analyzer,InfoPrimerLanding,InfoUltimoPais

# Funciones de ordenamiento

def GenerarComponentesConectados(catalog):
    return model.GenerarComponentesConectados(catalog)

def mismoCluster(catalog, landing1, landing2):
    return model.mismoCluster(catalog, landing1, landing2)

def LandingMoreCables(catalog):
    return model.LandingMoreCables(catalog)

# Funciones de consulta sobre el catálogo

def InfoCatalog(analyzer):
    return model.InfoCatalog(analyzer)

def NumSCC(catalog):
    return model.NumSCC(catalog)