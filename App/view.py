"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
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
import sys
import threading
import controller
from DISClib.ADT import list as lt
import time
from DISClib.ADT.graph import gr
assert cf
import math


sys.setrecursionlimit(2 ** 20)
"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

#Menu
def printMenu():
    print("\nBienvenido")
    print("1- Inicializar catálogo")
    print("2- Cargar información en el catálogo")
    print("3- Encontrar la cantidad de clústeres")
    print("4- Encontrar landing point(s) que sirven como punto de interconexión")
    print("5- Encontrar la ruta mínima en distancia para enviar información entre dos países")
    print("6- Identifique la red de expansión mínima en cuanto a distancia con mayor cobertura")
    print("7- Lista de países que podrían verse afectados al producirse una caída en el proceso de comunicación")
    print("8- Conocer el ancho de banda máximo que se puede garantizar para la transmisión")
    print("9- Encontrar la ruta mínima en número de saltos para enviar información")
    print("10- Graficar mapa resultados requerimientos")

#Print de Resultados
def printDatosCargados(TotLanding,TotConections,TotCountries,InfoFirstLanding,InfoLastCountry,time_mseg):
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    print("Se cargaron:",TotLanding,"landing points.")
    print("Se cargaron:",TotConections,"conexiones entre los landing points.")
    print("Se cargaron:",TotCountries,"paises.")
    print("Informacion primer landing point cargado-> " + InfoFirstLanding)
    print("Información ultimo pais cargado-> " + InfoLastCountry)
    print("Tiempo de ejecucion:",time_mseg,"milisegundos.")
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    input("Enter para continuar")

def printReq1(numeroComponentes,mismo_clus,time_mseg):
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    print("El numero total de clusteres presentes en la red es: " + str(numeroComponentes))
    if(mismo_clus == "NE"):
        print("No existe un Landing Point con alguno de los nombres ingresados.")
    elif(mismo_clus == True):
        print("Los dos landing points indicados están en el mismo cluster.")
    else:
        print("Los dos landing points indicados NO están en el mismo cluster.")
    print ("Tiempo de ejecucion:",time_mseg,"milisegundos.")
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    input("Enter para continuar")

def printReq2(numero,LandingMoreCables,time_mseg):
    formato1 = "Los siguiente landings son un punto de interconexion a {} cables en la red:"
    formato2 = "-> Nombre: {}, identificador: {}, país: {}"
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    print(formato1.format(numero))
    for landing in lt.iterator(LandingMoreCables):
        nombre = landing["name"]
        id1 = landing["landing_point_id"]
        pais = landing["name"].split(",")[1].strip()
        print(formato2.format(nombre,id1,pais))
    print ("Tiempo de ejecucion:",time_mseg,"milisegundos.")
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    input("Enter para continuar")

def printReq3(Pais1,Pais2,camino,distancia,time_mseg):
    formato1 = "La distancia total desde {} hasta {} es de {} metros."
    formato2 = "-> Nombre: {}, identificador: {}, país: {}"
    formato3 = "No existe un camino entre {} y {}."
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    if (distancia) == -1:
        print(formato3.format(Pais1,Pais2))
    else:
        print(formato1.format(Pais1,Pais2,distancia))
        print("El camino a realizar es:")
        print(camino)
    print ("Tiempo de ejecucion:",time_mseg,"milisegundos.")
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    input("Enter para continuar")

def printReq4(mst,NumNodos,dist,Rama,time_mseg):
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    print("El número de nodos conectados a la red de expansión mínima es: " + str(NumNodos))
    print("El costo total de la red de expansión mínima es: " + str(dist/1000) + " Km.")
    print("Rama más larga: ")
    print(Rama)
    print ("Tiempo de ejecucion:",time_mseg,"milisegundos.")
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    input("Enter para continuar")

catalog = None

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 1:
        t1 = time.process_time()
        catalog = controller.newAnalyzer()
        t2 = time.process_time()
        time_mseg = (t2 - t1)*1000
        print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
        print ("Tiempo de ejecucion:",time_mseg,"milisegundos.")
        print("Catalogo inicializado correctamente.")
        print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
        input("Enter para continuar")

    elif int(inputs[0]) == 2:
        t1 = time.process_time()
        catalog,InfoFirstLanding,InfoLastCountry = controller.loadData(catalog)
        t2 = time.process_time()
        time_mseg = (t2 - t1)*1000
        TotCountries,TotLanding,TotConections = controller.InfoCatalog(catalog)
        printDatosCargados(TotLanding,TotConections,TotCountries,InfoFirstLanding,InfoLastCountry,time_mseg)
    
    #Req 1
    elif int(inputs[0]) == 3:
        t1 = time.process_time()
        landing1 = input("Ingrese el nombre del primer Landing Point: ")
        landing2 = input("Ingrese el nombre del segundo Landing Point: ")
        if catalog["components"] == None:
            catalog = controller.generarComponentesConectados(catalog)
        numeroComponentes = controller.NumSCC(catalog)
        mismo_clus = controller.mismoCluster(catalog, landing1, landing2)
        t2 = time.process_time()
        time_mseg = (t2 - t1)*1000
        printReq1(numeroComponentes,mismo_clus,time_mseg)

    #Req 2
    elif int(inputs[0]) == 4:
        t1 = time.process_time()
        landingMoreCables, numero = controller.landingMoreCables(catalog)
        t2 = time.process_time()
        time_mseg = (t2 - t1)*1000
        printReq2(numero,landingMoreCables,time_mseg)

    #Req 3
    elif int(inputs[0]) == 5:
        t1 = time.process_time()
        pais1 = input("Ingrese el nombre del primer País: ")
        pais2 = input("Ingrese el nombre del segundo País: ")
        caminosMinimos = controller.caminosMinimos(catalog,pais1)
        camino, distancia = controller.caminoMin(caminosMinimos,pais2)
        t2 = time.process_time()
        time_mseg = (t2 - t1)*1000
        printReq3(pais1,pais2,camino,distancia,time_mseg)

    #Req 4
    elif int(inputs[0]) == 6:
        t1 = time.process_time()
        mst = controller.CrearMst(catalog)
        dist, NumNodos, Rama = controller.InfoMst(mst,catalog)
        t2 = time.process_time()
        time_mseg = (t2 - t1)*1000
        printReq4(mst,NumNodos,dist,Rama,time_mseg)

    #Req 5
    elif int(inputs[0]) == 7:
        nombreLanding = input("Ingrese el nombre del Landing Point: ")
        pass

    elif int(inputs[0]) == 8:
        pass

    elif int(inputs[0]) == 9:
        pass

    elif int(inputs[0]) == 10:
        pass

    else:
        sys.exit(0)
sys.exit(0)
