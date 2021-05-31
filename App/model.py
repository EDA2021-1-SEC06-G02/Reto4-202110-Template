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
import math
from DISClib.Algorithms.Sorting import mergesort as Merge
import haversine as hs
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def newAnalyzer():
    try:
        analyzer = {'LandingPointI': None, 'LandingPointN': None, 'connectionsDistance': None, 'connectionsCapacity': None, 'countrysInfo':None, 'components': None,}

        analyzer['LandingPointI'] = mp.newMap(numelements=1290,maptype='PROBING',comparefunction=compareCountryNames)

        analyzer['LandingPointN'] = mp.newMap(numelements=1290,maptype='PROBING',comparefunction=compareCountryNames)

        analyzer['connectionsDistance'] = gr.newGraph(datastructure='ADJ_LIST',directed=True,size=3500,comparefunction=compareLanCableIds)

        analyzer['connectionsCapacity'] = gr.newGraph(datastructure='ADJ_LIST',directed=True,size=3500,comparefunction=compareLanCableIds)

        analyzer['countriesInfo'] = mp.newMap(numelements=240, maptype='PROBING', comparefunction=compareCountryNames)

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

# Funciones para agregar informacion al catalogo

def AddLandingPointsData(analyzer, Entry):
    entry = mp.get(analyzer['LandingPointI'], Entry['landing_point_id'])
    if entry is None:
        CaracEntry = CreateLandingInfo()
    else:
        CaracEntry = me.getValue(entry)
    lt.addLast(CaracEntry['lstData'], Entry)
    mp.put(analyzer['LandingPointI'],Entry['landing_point_id'],CaracEntry)
    mp.put(analyzer['LandingPointN'],Entry['name'],CaracEntry)
    return analyzer

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
    entry = mp.get(Analyzer['LandingPointI'], Name)
    if entry is None:
        CaracEntry = CreateLandingInfo()
    else:
        CaracEntry = me.getValue(entry)
    lt.addLast(CaracEntry['lstData'], country)
    mp.put(Analyzer['LandingPointI'],Name,CaracEntry)
    mp.put(Analyzer['LandingPointN'],Name,CaracEntry)
    addLandingVertexDistance(Analyzer, Name)
    return Analyzer

def addLandingConnection(analyzer, Entry):
    try:
        origin = formatVertexOring(Entry)
        destination = formatVertexDestination(Entry)
        distance = CalculateDistance(analyzer,Entry)
        addLandingVertexDistance(analyzer, origin)
        addLandingVertexDistance(analyzer, destination)
        addLandingVertexCapacity(analyzer, origin)
        addLandingVertexCapacity(analyzer, destination)
        addConnectionDistance(analyzer, origin, destination, distance)
        capacity = Entry['capacityTBPS']
        addConnectionCapacity(analyzer, origin, destination,capacity)
        addLandingsRoutes(analyzer, Entry)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addLandingConnection')

def addLandingVertexDistance(analyzer, LandingId):
    try:
        if not gr.containsVertex(analyzer['connectionsDistance'], LandingId):
            gr.insertVertex(analyzer['connectionsDistance'], LandingId)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addLandingVertex')

def addLandingVertexCapacity(analyzer, LandingId):
    try:
        if not gr.containsVertex(analyzer['connectionsCapacity'], LandingId):
            gr.insertVertex(analyzer['connectionsCapacity'], LandingId)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addLandingVertex')

def addLandingsRoutes(analyzer, Entry):
    entry = mp.get(analyzer['LandingPointI'], Entry['origin'])
    try:
        entry = me.getValue(entry)
        CableName = Entry['cable_name']
        CapacityValue = Entry['capacityTBPS']
        Value = (CableName,CapacityValue)
        if not lt.isPresent(entry['lstCables'], Value):
            lt.addLast(entry['lstCables'], Value)
        mp.put(analyzer['LandingPointI'], Entry['origin'], entry)
        mp.put(analyzer['LandingPointN'], Entry['origin'], entry)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:InexistenciaLanding')

def addRouteConnections(analyzer):
    lststops = mp.keySet(analyzer['LandingPointI'])
    for key in lt.iterator(lststops):
        lstCables = mp.get(analyzer['LandingPointI'], key)
        lstCables = me.getValue(lstCables)['lstCables']
        lstCables = CapacityOrder(lstCables)
        capitalInfo = ObtenerPais(analyzer,key)
        CapitalDistance = CalculateDistanceCapital(analyzer,key,capitalInfo)
        prevCableName = None
        for CableName in lt.iterator(lstCables):
            CableName = key + '-' + CableName[0]
            capacity = lt.getElement(lstCables,1)[1]
            if prevCableName is not None:
                addConnectionDistance(analyzer, prevCableName, CableName, 100)
                addConnectionCapacity(analyzer, prevCableName, CableName, capacity)
                addConnectionDistance(analyzer, prevCableName, capitalInfo, CapitalDistance)
                addConnectionCapacity(analyzer, prevCableName, capitalInfo, capacity)
                addConnectionDistance(analyzer, CableName, capitalInfo, CapitalDistance)
                addConnectionCapacity(analyzer, CableName, capitalInfo, capacity)
            prevCableName = CableName

def addConnectionDistance(analyzer, origin, destination, distance):
    edge = gr.getEdge(analyzer['connectionsDistance'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connectionsDistance'], origin, destination, distance)
    return analyzer

def addConnectionCapacity(analyzer, origin, destination, Capacity):
    try:
        edge = gr.getEdge(analyzer['connectionsCapacity'], origin, destination)
        if edge is None:
            gr.addEdge(analyzer['connectionsCapacity'], origin, destination, Capacity)
        return analyzer
    except:
        pass

def addInternalConnections(analyzer):
    ltPorConectar = lt.newList('ARRAY_LIST',cmpfunction=compareroutes)
    ltVertices = gr.vertices(analyzer['connectionsDistance'])
    #print(gr.vertices(analyzer['connectionsDistance']))
    print(gr.degree(analyzer['connectionsDistance'],'Russia'))
    for element in lt.iterator(ltVertices):
        if gr.degree(analyzer['connectionsDistance'],element)==0:
            if not lt.isPresent(ltPorConectar,element):
                lt.addLast(ltPorConectar,element)
    print(ltPorConectar)
    return analyzer

#IDK

def generarComponentesConectados(catalog):
    catalog['components'] = scc.KosarajuSCC(catalog["connectionsDistance"])
    return catalog

def mismoCluster(catalog, landing1, landing2):
    """ Revisamos que existan los dos landings points que llegan por parametro. Si no existe alguno
    de los dos se retorna 'NE'. Si existen ambos probamos todas las combinaciones posibles <landing_id-cable>
    para cada uno de los landings para saber si ambos están en un mismo componente fuertemente conectado.
    Retorna True si están en el mismo y False de lo contrario"""
    landing1 = mp.get(catalog["LandingPointN"],landing1)
    landing2 = mp.get(catalog["LandingPointN"],landing2)
    encontrado = "NE"
    if landing1 != None and landing2 != None:
        landing1 = me.getValue(landing1)
        landing2 = me.getValue(landing2)
        landing1_id = lt.getElement(landing1['lstData'],1)["landing_point_id"]
        landing2_id = lt.getElement(landing2['lstData'],1)["landing_point_id"]
        i = 1
        encontrado = False
        while i <= lt.size(landing1['lstCables']) and not(encontrado):
            vertice1 = str(landing1_id) + "-" + lt.getElement(landing1['lstCables'],i)[0]
            j = 1
            while j <= lt.size(landing2['lstCables']) and not(encontrado):
                vertice2 = str(landing2_id) + "-" + lt.getElement(landing2['lstCables'],j)[0]
                encontrado = scc.stronglyConnected(catalog['components'], vertice1, vertice2)
                j+=1
            i+=1
    return encontrado

def landingMoreCables(catalog):
    """ Se recorren todos los landings points que se encuentran en la llave 'LandingPointI' del catalogo.
    Se revisa si el numero de cables que tiene el landing que se está revisando es mayor al mayor que se tiene;
    si esto sucede este valor se convierte en el nuevo mayor, la lista se pone vacia y se agrega el landing.
    En caso que tenga el mismo numero de landings que el mayor, el landing se agrega a la lista a retornar."""
    landingMoreCables = lt.newList('ARRAY_LIST',cmpfunction=compareCountryNames)
    maxCables = 0
    landings = mp.keySet(catalog["LandingPointI"])
    for landing in lt.iterator(landings):
        datosLanding = lt.getElement(me.getValue(mp.get(catalog["LandingPointI"],landing))['lstData'],1)
        cables = lt.size(me.getValue(mp.get(catalog["LandingPointI"],landing))['lstCables'])
        if cables > maxCables:
            maxCables = cables
            landingMoreCables = lt.newList('ARRAY_LIST',cmpfunction=compareCountryNames)
            lt.addLast(landingMoreCables,datosLanding)
        elif(cables == maxCables):
            lt.addLast(landingMoreCables,datosLanding)
    return landingMoreCables, maxCables

def caminosMinimos(catalog,Fuente):
    caminoMin = djk.Dijkstra(catalog["connectionsDistance"],Fuente)
    return caminoMin

def caminoMin(caminosMinimos,Pais2):
    """ Se consigue la distancia y el camino que conecta la fuente del grafo Caminos minimos con el Pais2.
    Si la distancia es infinito, lo cual indica que no hay camino, esta se remplaza por -1.
    #PROXIMAMENTE: Pasar el camino a una lista para que sea facil de imprimir en el view"""
    camino = djk.pathTo(caminosMinimos,Pais2)
    distancia = djk.distTo(caminosMinimos,Pais2)
    if distancia == math.inf:
        distancia = -1
    return camino, distancia

# Funciones para creacion de datos

def CreateLandingInfo():
    entry = {'lstData':None,'lstCables':None}
    entry['lstData'] = lt.newList('ARRAY_LIST')
    entry['lstCables'] = lt.newList('ARRAY_LIST',cmpfunction=compareCableName)
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

def formatVertexCapital(analyzer,Entry):
    LPorigen = Entry['origin']
    value = mp.get(analyzer['LandingPointI'],LPorigen)
    value = lt.getElement(me.getValue(value)['lstData'],1)['name']
    nameCountry = value.split(',')
    nameCountry = nameCountry[len(nameCountry)-1].strip()
    return nameCountry

def ObtenerPais(analyzer,key):
    if not mp.contains(analyzer['countriesInfo'],key):
        value = mp.get(analyzer['LandingPointI'],key)
        value = lt.getElement(me.getValue(value)['lstData'],1)['name']
        nameCountry = value.split(',')
        nameCountry = nameCountry[len(nameCountry)-1].strip()
        #print(nameCountry)
        return nameCountry

# Funciones de consulta

def InfoCatalog(analyzer):
    sizeCountries = lt.size(mp.keySet(analyzer['countriesInfo']))
    totLandingPoints = lt.size(mp.keySet(analyzer['LandingPointI']))
    totConections = gr.numEdges(analyzer['connectionsDistance'])
    return sizeCountries,totLandingPoints,totConections

def CalculateDistance(analyzer,Entry):
    oring = Entry['origin']
    destination = Entry['destination']
    Info1 = mp.get(analyzer['LandingPointI'],oring)
    Info2 = mp.get(analyzer['LandingPointI'],destination)
    try:
        latitude1 = me.getValue(Info1)['lstData']
        latitude1 = float(lt.getElement(latitude1,1)['latitude'])
        latitude2 = me.getValue(Info2)['lstData']
        latitude2 = float(lt.getElement(latitude2,1)['latitude'])
    except:
        pass
    try:
        longitude1 = me.getValue(Info1)['lstData']
        longitude1 = float(lt.getElement(longitude1,1)['longitude'])
        longitude2 = me.getValue(Info2)['lstData']
        longitude2 = float(lt.getElement(longitude2,1)['longitude'])
    except:
        pass
    loc1=latitude1,longitude1
    loc2=latitude2,longitude2
    distance = hs.haversine(loc1,loc2)
    distance *= 1000
    return distance

def CalculateDistanceCapital(analyzer, oring, destination):
    try:
        Info1 = mp.get(analyzer['LandingPointI'],oring)
        InfoCapital = mp.get(analyzer['LandingPointI'],destination)
        latitude1 = me.getValue(Info1)['lstData']
        latitude1 = float(lt.getElement(latitude1,1)['latitude'])
        latitudeCapital = me.getValue(InfoCapital)['lstData']
        latitudeCapital = float(lt.getElement(latitudeCapital,1)['CapitalLatitude'])
        longitude1 = me.getValue(Info1)['lstData']
        longitude1 = float(lt.getElement(longitude1,1)['longitude'])
        longitudeCapital = me.getValue(InfoCapital)['lstData']
        longitudeCapital = float(lt.getElement(longitudeCapital,1)['CapitalLongitude'])
        loc1=latitude1,longitude1
        loc2=latitudeCapital,longitudeCapital
        distance = hs.haversine(loc1,loc2)
        distance *= 1000
        return distance
    except:
        pass

def NumSCC(catalog):
    return scc.connectedComponents(catalog['components'])


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

def CapacityOrder(listaOrdenada):
    sub_list = lt.subList(listaOrdenada, 1, lt.size(listaOrdenada))
    sub_list = sub_list.copy()
    sorted_list = Merge.sort(sub_list, cmpCapacitys)
    return sorted_list

def cmpCapacitys(capacitys1, capacitys2):
    return capacitys1[1] < capacitys2[1]