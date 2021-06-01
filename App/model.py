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


from DISClib.Algorithms.Graphs.prim import PrimMST as prim
import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.ADT.graph import gr
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import prim
from DISClib.Algorithms.Graphs import dfs
from DISClib.DataStructures import edge as e
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

def AddLandingPointsData(Analyzer, Entry):
    """Se cargan los landings points en la tabla de hash con llave Landing_Point_ID para que sea mas sencillo
    de encontrar con los datos brindados en el archivo de connections. Se agregan a una segunda tabla de hash
    el nombre del landing point como llave y como valor el ID del landgin point para facilitar las consultas de
    de ciertos requerimientos."""
    ID=Entry['landing_point_id']
    paisLanding = Entry['name']
    paisLanding = paisLanding.split(',')
    paisLanding = paisLanding[len(paisLanding)-1].strip()
    existLanding = mp.contains(Analyzer['LandingPointI'], ID)
    if existLanding:
        infoEntry = mp.get(Analyzer['LandingPointI'], ID)
        LandingInfo = me.getValue(infoEntry)
    else:
        LandingInfo = CreateLandingInfo()
    lt.addLast(LandingInfo['lstData'], Entry)
    lt.addLast(LandingInfo['lstLocation'], Entry['latitude'])
    lt.addLast(LandingInfo['lstLocation'], Entry['longitude'])
    mp.put(Analyzer['LandingPointI'],ID,LandingInfo)
    mp.put(Analyzer['LandingPointN'],Entry['name'],ID)
    addLandingVertexDistance(Analyzer, ID)
    addLandingVertexCapacity(Analyzer, ID)
    """Cosultamos la información del landing point del pais para agregarle la información 
    al respecto de un landing point existente dentro del país."""
    PaisEntry = mp.get(Analyzer['LandingPointI'], paisLanding)
    LandingPais = me.getValue(PaisEntry)
    lstLandingPais = LandingPais['lstLandings']
    if not lt.isPresent(lstLandingPais,ID):
        lt.addLast(lstLandingPais,ID)
    mp.put(Analyzer['LandingPointI'], paisLanding ,LandingPais)
    return Analyzer

def AddCountry(Analyzer,country):
    """Agregamos el país a una tabla de hash con Llave igual al nombre del país,
    esta tabla contendrá la información existente en la lectura del archivo de Countries."""
    Name = country['CountryName']
    existName = mp.contains(Analyzer['countriesInfo'], Name)
    if existName:
        entry = mp.get(Analyzer['countriesInfo'], Name)
        CountryInfo = me.getValue(entry)
    else:
        CountryInfo = newCountryValues()
    lt.addLast(CountryInfo['countriesInfo'], country)
    mp.put(Analyzer['countriesInfo'], Name, CountryInfo)
    """Agregamos el país a la tabla que contiene los landing points, el nombre de este landing point
    será el nombre del país y representará a la capital de este. Estos landing Poinst especiales 
    tendran una estrucutra diferente a la de los landing normales."""
    existLandingCountry = mp.contains(Analyzer['LandingPointI'], Name)
    if existLandingCountry:
        entry=mp.get(Analyzer['LandingPointI'], Name)
        LandingCountry = me.getValue(entry)
    else:
        LandingCountry = CreateLandingCountriesInfo()
    lt.addLast(LandingCountry['lstLocation'], country['CapitalLatitude'])
    lt.addLast(LandingCountry['lstLocation'], country['CapitalLongitude'])
    mp.put(Analyzer['LandingPointI'],Name,LandingCountry)
    addLandingVertexDistance(Analyzer, Name)
    addLandingVertexCapacity(Analyzer, Name)
    return Analyzer

def addLandingConnection(analyzer, Entry):
    """Se agregan los datos del archivo de connections, en este archivo se guardan los
    vértices con el formado: Landing_ID*Cable_Name. Posteriormente se calculan las distancias
    entre los landings involucadros y se almacen en una lista los cables que pertenecen a un landing
    point."""
    origin = formatVertexOring(Entry)
    destination = formatVertexDestination(Entry)
    distance = CalculateDistance(analyzer,Entry['origin'],Entry['destination'])
    capacity = Entry['capacityTBPS']
    addLandingVertexDistance(analyzer, origin)
    addLandingVertexDistance(analyzer, destination)
    addLandingVertexCapacity(analyzer, origin)
    addLandingVertexCapacity(analyzer, destination)
    addConnectionDistance(analyzer, origin, destination, distance)
    addConnectionCapacity(analyzer, origin, destination,capacity)
    addLandingsRoutes(analyzer, Entry)
    return analyzer

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
    """Guarda el cable que conecta dos landing points, esta información se almacena sea
    en landing point de origen que en el de destino"""
    Origin = mp.get(analyzer['LandingPointI'], Entry['origin'])
    Destination = mp.get(analyzer['LandingPointI'], Entry['destination'])
    Originentry = me.getValue(Origin)
    Destinationentry = me.getValue(Destination)
    CableName = Entry['cable_name']
    CapacityValue = Entry['capacityTBPS']
    Value = (CableName,CapacityValue)
    if not lt.isPresent(Originentry['lstCables'], Value):
        lt.addLast(Originentry['lstCables'], Value)
    if not lt.isPresent(Destinationentry['lstCables'], Value):
        lt.addLast(Destinationentry['lstCables'], Value)
    mp.put(analyzer['LandingPointI'], Entry['origin'], Originentry)
    mp.put(analyzer['LandingPointI'], Entry['destination'], Destinationentry)
    return analyzer

def addLandingCapitalConnections(analyzer):
    """Se conectan los landing points con las capitales, para comodidad de comparaciones
    se decidió crear un vértice genérico que será el que se conecte con la capital del país,
    a su vez este landing point genérico es el que se conecta con los landing points que
    contienen los cables"""
    lstCountries = mp.keySet(analyzer['countriesInfo'])
    for CountryName in lt.iterator(lstCountries):
        CountryLandingInfo = mp.get(analyzer['LandingPointI'], CountryName)
        CountryLandingInfo = me.getValue(CountryLandingInfo)
        lstLandingsCountries = CountryLandingInfo['lstLandings']
        for LandingID in lt.iterator(lstLandingsCountries):
            CapitalLandingDistance = CalculateDistance(analyzer,CountryName,LandingID)
            LandingInfo = mp.get(analyzer['LandingPointI'], LandingID)
            LandingInfo = me.getValue(LandingInfo)
            lstCablesLanding = LandingInfo['lstCables']
            lstCablesLandingOrdenada = CapacityOrder(lstCablesLanding)
            capacity = lt.getElement(lstCablesLandingOrdenada,1)[1]
            CountryLandingInfo['MinCapacity_Landing'] = capacity
            LandingInfo['MinCapacity_Landing'] = capacity
            addConnectionDistance(analyzer, CountryName, LandingID, CapitalLandingDistance)
            addConnectionDistance(analyzer, LandingID, CountryName, CapitalLandingDistance)
            addConnectionCapacity(analyzer, CountryName, LandingID, capacity)
            addConnectionCapacity(analyzer, LandingID, CountryName, capacity)
            for CableName in lt.iterator(lstCablesLanding):
                LandingConetion = LandingID + '*' + CableName[0]
                addConnectionDistance(analyzer, LandingID, LandingConetion, 100)
                addConnectionDistance(analyzer, LandingConetion, LandingID, 100)
                addConnectionCapacity(analyzer, LandingID, LandingConetion, capacity)
                addConnectionCapacity(analyzer, LandingConetion, LandingID, capacity)

def addConnectionDistance(analyzer, origin, destination, distance):
    edge = gr.getEdge(analyzer['connectionsDistance'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connectionsDistance'], origin, destination, distance)
    return analyzer

def addConnectionCapacity(analyzer, origin, destination, Capacity):
    edge = gr.getEdge(analyzer['connectionsCapacity'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connectionsCapacity'], origin, destination, Capacity)
    return analyzer

def addContinentConnection(analyzer):
    """Se consultan cuales nodos del grafo tiene grado 0 y se les realizan las comparaciones necesarias
    para encontrar la distancia de los landing points para encontrar el camino más cercano en KM a las 
    capitales de interés."""
    ltVertices = gr.vertices(analyzer['connectionsDistance'])
    for element in lt.iterator(ltVertices):
        if gr.degree(analyzer['connectionsDistance'],element)==0:
            primero = True
            minElement = ""
            minDistance = 0
            capacity = 0
            lstLandingPoints = mp.keySet(analyzer['LandingPointI'])
            for key in lt.iterator(lstLandingPoints):
                if not (key == element):
                    distance = CalculateDistance(analyzer,element,key)
                    if distance == 0:
                        distance = 100
                    if primero:
                        minDistance = distance
                        minElement = key
                        minElementInfo = mp.get(analyzer['LandingPointI'],key)
                        minElementInfo = me.getValue(minElementInfo)
                        capacity = minElementInfo['MinCapacity_Landing']
                        primero = False
                    elif minDistance < distance:
                        minDistance = distance
                        minElement = key
                        minElementInfo = mp.get(analyzer['LandingPointI'],key)
                        minElementInfo = me.getValue(minElementInfo)
                        capacity = minElementInfo['MinCapacity_Landing']
            addConnectionDistance(analyzer, element, minElement, minDistance)
            addConnectionDistance(analyzer, minElement, element, minDistance)
            addConnectionCapacity(analyzer, element, minElement, capacity)
            addConnectionCapacity(analyzer, minElement, element, capacity)
    ltVertices = gr.vertices(analyzer['connectionsDistance'])
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
        encontrado = scc.stronglyConnected(catalog['components'], landing1, landing2)
        """i = 1
        encontrado = False
        while i <= lt.size(landing1['lstCables']) and not(encontrado):
            vertice1 = str(landing1_id) + "-" + lt.getElement(landing1['lstCables'],i)[0]
            j = 1
            while j <= lt.size(landing2['lstCables']) and not(encontrado):
                vertice2 = str(landing2_id) + "-" + lt.getElement(landing2['lstCables'],j)[0]
                encontrado = scc.stronglyConnected(catalog['components'], vertice1, vertice2)
                j+=1
            i+=1"""
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
        if not mp.contains(catalog['countriesInfo'],landing):
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

def caminoMin(caminosMinimos,pais1,pais2):
    """ Se consigue la distancia y el camino que conecta la fuente del grafo Caminos minimos con el Pais2.
    Si la distancia es infinito, lo cual indica que no hay camino, esta se remplaza por -1.
    #PROXIMAMENTE: Pasar el camino a una lista para que sea facil de imprimir en el view"""
    caminos = lt.newList('ARRAY_LIST',cmpfunction=compareCountryNames)
    camino = djk.pathTo(caminosMinimos,pais2)
    distancia = djk.distTo(caminosMinimos,pais2)
    if distancia == math.inf:
        distancia = -1
    else:
        for elemento in lt.iterator(camino):
            dato = lt.newList('ARRAY_LIST')
            land1 = e.either(elemento)
            peso = e.weight(elemento)
            land2 = e.other(elemento,e.either(elemento))
            lt.addLast(dato,land1)
            lt.addLast(dato,peso)
            lt.addLast(dato,land2)
            lt.addLast(caminos,dato)
    return caminos, distancia

def CrearMst(catalog):
    mst = prim.PrimMST(catalog['connectionsDistance'])
    return mst

# Funciones para creacion de datos

def CreateLandingInfo():
    entry = {'lstData':None,'lstCables':None,'lstLocation':None,'MinCapacity_Landing':float}
    entry['lstData'] = lt.newList('ARRAY_LIST')
    entry['lstCables'] = lt.newList('ARRAY_LIST',cmpfunction=compareCableName)
    entry['lstLocation'] = lt.newList('ARRAY_LIST')
    entry['MinCapacity_Landing'] = 0
    return entry

def CreateLandingCountriesInfo():
    entry = {'lstLandings':None,'lstLocation':None,'MinCapacity_Landing':float}
    entry['lstLandings'] = lt.newList('ARRAY_LIST',cmpfunction=compareCableName)
    entry['lstLocation'] = lt.newList('ARRAY_LIST')
    entry['MinCapacity_Landing'] = 0
    return entry

def newCountryValues():
    Values = {"countriesInfo": None}
    Values['countriesInfo'] = lt.newList('ARRAY_LIST')
    return Values

def newContinentValues():
    Values = {"ContinentCountries": None}
    Values['ContinentCountries'] = lt.newList('ARRAY_LIST',cmpfunction=compareCableName)
    return Values

def formatVertexOring(Entry):
    """Formato del vértice del grafo"""
    name = Entry['origin'] + '*'
    name = name + Entry['cable_name']
    return name
    
def formatVertexDestination(Entry):
    """Formato del vértice del grafo"""
    name = Entry['destination'] + '*'
    name = name + Entry['cable_name']
    return name

# Funciones de consulta

def InfoCatalog(analyzer):
    sizeCountries = lt.size(mp.keySet(analyzer['countriesInfo']))
    totLandingPoints = lt.size(mp.keySet(analyzer['LandingPointI']))
    totConections = gr.numEdges(analyzer['connectionsDistance'])
    return sizeCountries,totLandingPoints,totConections

def CalculateDistance(analyzer,oring,destination):
    """Calcula las distancias entre una localización y otra"""
    Info1 = mp.get(analyzer['LandingPointI'],oring)
    Info2 = mp.get(analyzer['LandingPointI'],destination)
    Coor1 = me.getValue(Info1)['lstLocation']
    Coor2 = me.getValue(Info2)['lstLocation']
    lat1 = float(lt.getElement(Coor1,1))
    lon1 = float(lt.getElement(Coor1,2))
    lat2 = float(lt.getElement(Coor2,1))
    lon2 = float(lt.getElement(Coor2,2))
    loc1=lat1,lon1
    loc2=lat2,lon2
    distance = hs.haversine(loc1,loc2)
    distance *= 1000
    return distance

def NumSCC(catalog):
    return scc.connectedComponents(catalog['components'])

def InfoMst(mst,catalog):
    dist = prim.weightMST(catalog['connectionsDistance'],mst)
    NumNodos = gr.numVertices(catalog['connectionsDistance'])
    """mst2 = gr.newGraph(datastructure='ADJ_LIST',directed=True,size=3500,comparefunction=compareLanCableIds)
    lista = lt.newList('ARRAY_LIST',cmpfunction=compareCountryNames)
    arcos = mst['mst']
    for arco in lt.iterator(arcos):
        gr.addEdge(mst2,e.either(arco),e.weight(arco))
    dfs.DepthFirstSearch(mst2,)"""
    Rama = ""
    return dist, NumNodos, Rama

def verificarPais(catalog,pais2):
    verificado = mp.contains(catalog['countriesInfo'],pais2)
    return verificado

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
