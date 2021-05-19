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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.ADT.graph import gr
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def newAnalyzer():
    try:
        analyzer = {'LandingPoint': None,'connections': None,'countrysInfo':None}

        analyzer['LandingPoint'] = mp.newMap(numelements=1290,maptype='PROBING',comparefunction=compareCountryNames)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',directed=False,size=3500,comparefunction=compareLanCableIds)
        #Cargar Vertices con ID-Cable

        analyzer['countriesInfo'] = mp.newMap(numelements=240, maptype='PROBING', comparefunction=compareCountryNames)
        #Cargar con Nombre Pais

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

# Funciones para agregar informacion al catalogo

def AddLandingPointsData(analyzer, Entry):
    entry = mp.get(analyzer['LandingPoint'], Entry['landing_point_id'])
    if entry is None:
        CaracEntry = CreateLandingInfo()
    else:
        CaracEntry = me.getValue(entry)
    lt.addLast(CaracEntry['lstData'], Entry)
    mp.put(analyzer['LandingPoint'],Entry['landing_point_id'],CaracEntry)
    return analyzer

def addLandingConnection(analyzer, Entry):
    try:
        origin = formatVertexOring(Entry)
        destination = formatVertexDestination(Entry)
        distance = CalculateDistance(Entry)
        addLandingVertex(analyzer, origin)
        addLandingVertex(analyzer, destination)
        addConnection(analyzer, origin, destination, distance)
        addLandingsRoutes(analyzer, Entry)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addLandingConnection')

def AddCountry(Analyzer,country):
    Name = country['CountryName']
    existName = mp.contains(Analyzer['countriesInfo'], Name)
    if existName:
        entry = mp.get(Analyzer['countriesInfo'], Name)
        NameCountry = me.getValue(entry)
    else:
        NameCountry = newCountryValues()
        mp.put(Analyzer['countriesInfo'], Name, NameCountry)
    lt.addLast(NameCountry['countriesInfo'], country)
    return Analyzer

def addLandingVertex(analyzer, LandingId):
    """
    Adiciona una estación como un vertice del grafo
    """
    try:
        if not gr.containsVertex(analyzer['connections'], LandingId):
            gr.insertVertex(analyzer['connections'], LandingId)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addLandingVertex')

def addLandingsRoutes(analyzer, Entry):
    entry = mp.get(analyzer['LandingPoint'], Entry['origin'])
    try:
        entry = me.getValue(entry)
        CableName = Entry['cable_name']
        if not lt.isPresent(entry['lstCables'], CableName):
            lt.addLast(entry['lstCables'], CableName)
        mp.put(analyzer['LandingPoint'], Entry['origin'], entry)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:InexistenciaLanding')


def addConnection(analyzer, origin, destination, distance):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(analyzer['connections'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connections'], origin, destination, distance)
    return analyzer

# Funciones para creacion de datos

def CreateLandingInfo():
    entry = {'lstData':None,'lstCables':None}
    entry['lstData'] = lt.newList()
    entry['lstCables'] = lt.newList(cmpfunction=compareCableName)
    return entry

def newCountryValues():
    Values = {"countriesInfo": None}
    Values['countriesInfo'] = lt.newList('ARRAY_LIST')
    return Values

def formatVertexOring(Entry):
    name = Entry['origin'] + '-'
    name = name + Entry['cable_name']
    return name
    
def formatVertexDestination(Entry):
    name = Entry['destination'] + '-'
    name = name + Entry['cable_name']
    return name

# Funciones de consulta

def InfoCatalog(analyzer):
    sizeCountries = lt.size(mp.keySet(analyzer['countriesInfo']))
    totLandingPoints= lt.size(mp.keySet(analyzer['LandingPoint']))
    totConections=0
    return sizeCountries,totLandingPoints,totConections

def CalculateDistance(Entry):
    oring = Entry['origin']
    destination = Entry['destination']
    pass

#Funciones Comparacion

def compareLanCableIds(LanCable, keyvalueLanCable):
    LanCablecode = keyvalueLanCable['key']
    if (LanCable == LanCablecode):
        return 0
    elif (LanCable > LanCablecode):
        return 1
    else:
        return -1

def compareroutes(connection1, connection2):
    if (connection1 == connection2):
        return 0
    elif (connection1 > connection2):
        return 1
    else:
        return -1

def compareCountryNames(Name1, Name2):
    Name = me.getKey(Name2)
    if (Name1 == Name):
        return 0
    elif (Name1 > Name):
        return 1
    else:
        return -1

def compareCableName(Cable1, Cable2):
    if (Cable1 == Cable2):
        return 0
    elif (Cable1 > Cable2):
        return 1
    else:
        return -1