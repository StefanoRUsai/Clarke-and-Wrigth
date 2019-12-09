import numpy as np
import string
from collections import Counter
from clarke_and_wright.vehicle import Vehicle
import pyximport; pyximport.install()

def euclidian_distance(point_one, point_two):
    from math import sqrt
    """Funzione che prende 2 punti in entrata e calcola e ne restituisce la distanza"""
    return (sqrt( ((point_one[0]-point_two[0])**2) + ((point_one[1]-point_two[1])**2) ))

def distance_matrix(cord):
    """prende come parametro un vettore di punti, rappresentati da una coppia di numeri
    restituisce una matrice delle distanze m x n"""

    distance_matrix=[]
    array=[]     
    for cord_one in cord:
        for cord_two in cord:
            array.append(euclidian_distance(cord_one,cord_two))
        distance_matrix.append(array)
        array=[]
    return distance_matrix

def saving_matrix(c):    
    """prende come parametro una matrice delle distanze m x n 
    restituisce la matrice triangolare superiore dei risparmi chiamati saving"""
    
    saving = [] # rappresenta la matrice dei saving
    array= [] # array di supporto che rappresenta ogni riga della matrice dei saving
    for i in range(1,len(c)): # prendo in considerazione da 1 a m-1 della matrice delle distanze
        for j in range (1,len(c)): # prendo in considerazione da 1 a n-1 della matrice delle distanze
            if i==j: # se i e j sono la stessa istanza non teniamo traccia del risparmio
                array.append(0) # aggiungo 0
            elif i >= 1 and j >= 1: # guardia probabilmente inutile, per considerare solo le posizioni superiori a 1
                array.append((c[i][0]+c[0][j])-c[i][j]) # formula dei saving dell'algoritmo "Clarke and Wright"
        saving.append(array) # inserisco la riga nella matrice dei saving
        array = [] # svuoto l'array

    saving= np.triu(saving) # triangolarizzo superiormente la matrice dei saving

    return saving

def swap(a,b):
    if a < b:
        return (a,b)
    else:
        return (b,a)

def savingOrder(saving):
    """ Prende come input la matrice dei saving
    restituisce una mappa K V ordinata per valore decrescente dove
    K è una stringa che rappresenta il nome delle istanze dell'arco
    V è il valore del risparmio di quell'arco"""
    from collections import Counter

    dict_Saving={} # creo un dizionario di supporto che rappresenta la mia mappa
    for i in range(0,len(saving)): # ciclo da 0 a m-1 sulla matrice dei saving
        for j in range(0, len(saving[i])): # ciclo da 0 a n-1 sulla matrice dei saving
            if saving[i][j] != 0: # se il risparmio per le istanze ij è diverso da 0 inserisco K  str(i+1)+"-"+str(j+1) 
                dict_Saving[swap((i+1),(j+1))] = saving[i][j] # dove saving è il valoreassociato
    
    c = Counter(dict_Saving) #inizializzo una variabile della classe Counter 
    dict_Saving_Order=c.most_common() #ordino per i valori dei saving in maniera decrescente
    dict_Saving = {} # svuoto il vecchio dizionario per questioni di memoria
    for e in dict_Saving_Order: # ciclo su ogni valore del vettore della classe counter che è composto da copie 
        dict_Saving[e[0]]=e[1] # reinserisco su K il nome delle istanze e su V il valore a loro associato
    
    return dict_Saving

def route_Linehaul_Backhaul(dict_sav, vec_b, vec_l):
    """prende in input una mappa K V ordinata per valore decrescente dove
    K è una stringa che rappresenta il nome delle istanze dell'arco
    V è il valore del risparmio di quell'arco
    
    e un vettore con segnato quali istanze sono in backhaul
    e un vettore con segnato quali istanze sono in linehaul
    e restitutisce 2 mappe con linehaul e bachaul suddivisi"""
    
    dict_b={}
    dict_l={}
    for k in dict_sav.keys():
        if k[0] in vec_b and k[1] in vec_b:
            dict_b[k] = dict_sav.get(k)
        if k[0] in vec_l and k[1] in vec_l:
            dict_l[k] = dict_sav.get(k)
    
    new = set(dict_sav) - set(dict_b) - set(dict_l)
    
    dict_merge={}
    for e in new:
        dict_merge[e]=dict_sav.get(e)
    
    c = Counter(dict_merge) #inizializzo una variabile della classe Counter 
    dict_m = c.most_common() #ordino per i valori dei saving in maniera decrescente
    dict_merge = {} # svuoto il vecchio dizionario per questioni di memoria
    for e in dict_m: # ciclo su ogni valore del vettore della classe counter che è composto da copie 
        dict_merge[e[0]]=e[1] # reinserisco su K il nome delle istanze e su V il valore a loro associato
    
            
    return dict_b,dict_l, dict_merge    

def different(a,b):
    if a == b[0]:
        return b[1]
    else:
        return b[0]

def remove_Route_in_dict(dict_new, x=0, y=0 ):
    lista_keys= list(dict_new.keys())
    for k in lista_keys:
        if x in k or y in k:
            dict_new.pop(k)

def remove_first_instance(dict_new, s):
    lista_keys= list(dict_new.keys())
    for k in lista_keys:
        if k[0] in s or k[1] in s:
            dict_new.pop(k)

def init_list_of_vehicle(dict_l, vect_domanda, distance, number_of_vehicles=0):
    list_vehicle = []
    set_iniziale = {0}
    set_first = {0}
    set_visited = {0}
    lista_keys= list(dict_l.keys())
    
    for k in lista_keys:
        if len(list_vehicle) < number_of_vehicles\
        and k[0] not in set_iniziale\
        and k[1] not in set_iniziale:
            list_vehicle.append(Vehicle([0, k[0], k[1]], vect_domanda[k[0]]+vect_domanda[k[1]],
                             distance[0][k[0]]+distance[k[0]][k[1]]))        
            set_iniziale.add(k[0])
            set_iniziale.add(k[1])
            set_first.add(k[0])
            set_visited.add(k[0])
            set_visited.add(k[1])
    
    remove_first_instance(dict_l, set_first)
    
    return list_vehicle, set_visited

def init_list_of_vehicle_parallel(dict_l, vect_domanda, distance, number_of_vehicles=0):
    list_vehicle = []
    set_iniziale = {0}
    set_first = {0}
    set_visited = {0}
    lista_keys= list(dict_l.keys())
    for k in lista_keys:
        if len(list_vehicle) < number_of_vehicles and k[0] not in set_iniziale and k[1] not in set_iniziale:
            list_vehicle.append(Vehicle([0, k[0], k[1]], vect_domanda[k[0]]+vect_domanda[k[1]],
                             distance[0][k[0]]+distance[k[0]][k[1]]))
            set_iniziale.add(k[0])
            set_iniziale.add(k[1])
            set_first.add(k[0])
            set_visited.add(k[0])
            set_visited.add(k[1])
            
    return list_vehicle, set_visited
    


def route_linehaul(dict_l, list_vehicle, vect_domanda, set_visited, distance, capacity):
    c = 0
    set_first = {0}

    while(len(dict_l)>0 and c < len(list_vehicle)):
        lista_keys = list(dict_l.keys())
        flag = True

        while(flag):
            for k in lista_keys:
                if list_vehicle[c].route[-1] in k \
                and different(list_vehicle[c].route[-1], k) not in set_visited \
                and list_vehicle[c].weight + vect_domanda[different(list_vehicle[c].route[-1],k)] <= capacity:
                        list_vehicle[c].add_weight(vect_domanda[different(list_vehicle[c].route[-1],k)])
                        list_vehicle[c].add_route(k)           
                        set_visited.add(list_vehicle[c].route[-1])
                        set_first.add(k[0])
                        list_vehicle[c].add_cost(distance[k[0]][k[1]])
                        break
                else:
                    if lista_keys.index(k) == len(lista_keys)-1:
                        flag = False
                        break
            remove_first_instance(dict_l, set_first)
        list_vehicle[c].delivery = list_vehicle[c].weight
        list_vehicle[c].weight = 0
        c += 1

def route_linehaul_parallel(number_of_customers, dict_l, list_vehicle, vect_domanda, set_visited, distance, capacity, number_of_vehicles):
    c = 0
    temp = dict_l.copy()
    set_first = {0}
    i = 0 
    while(i < np.math.factorial(number_of_customers)/(np.math.factorial(number_of_customers-2)*2)):
        lista_keys = list(dict_l.keys())
        flag = True
        for k in lista_keys:
            #if 17 in k and list_route[c].route[-1] in k: #controllo cosa c'è quando arriva a 17
                #print(f'La route {c}: \t\t {list_route[c].route} \t\t capacità raggiunta: {list_route[c].weight} \t\t pair {k}')
                #print('----')
            if list_vehicle[c].route[-1] in k \
            and different(list_vehicle[c].route[-1], k) not in set_visited \
            and list_vehicle[c].weight + vect_domanda[different(list_vehicle[c].route[-1],k)] <= capacity:

                    list_vehicle[c].add_weight(vect_domanda[different(list_vehicle[c].route[-1],k)])
                    list_vehicle[c].add_route(k)           
                    set_visited.add(list_vehicle[c].route[-1])
                    list_vehicle[c].add_cost(distance[k[0]][k[1]])
                    set_first.add(k[0])

                    break

        #remove_first_instance(dict_l, set_first)
        c = (c + 1) % number_of_vehicles

        i += 1
        for e in list_vehicle:
            e.delivery = e.weight
            e.weight = 0
        
def route_backhaul(list_vehicle, dict_merge, dict_b, set_visited, vect_carico, distance, number_of_customers, capacity):
    c = 0
    set_first = {0}
    set_merge = {0}
    while(c < len(list_vehicle)):
        if len(set_visited) <= number_of_customers:
            merge = list(dict_merge.keys())
            back = list(dict_b.keys())
            for k in merge:
                if list_vehicle[c].route[-1] in k and different(list_vehicle[c].route[-1], k) not in set_visited:
                        list_vehicle[c].add_weight(vect_carico[different(list_vehicle[c].route[-1],k)])
                        list_vehicle[c].add_route(k)
                        set_visited.add(list_vehicle[c].route[-1])
                        list_vehicle[c].add_cost(distance[k[0]][k[1]])
                        set_merge.add(k[0])
                        break
            remove_first_instance(dict_merge, set_merge)
            flag = True 
            while(flag):
                for k in back:
                    if list_vehicle[c].route[-1] in k and different(list_vehicle[c].route[-1], k) not in set_visited \
                    and list_vehicle[c].weight + vect_carico[different(list_vehicle[c].route[-1],k)] <= capacity:
                            list_vehicle[c].add_weight(vect_carico[different(list_vehicle[c].route[-1],k)])
                            list_vehicle[c].add_route(k)           
                            set_visited.add(list_vehicle[c].route[-1])
                            list_vehicle[c].add_cost(distance[k[0]][k[1]])
                            set_first.add(k[0])
                            break
                    else:
                        if back.index(k) == len(back)-1:
                            flag = False
                            break
                remove_first_instance(dict_b, set_first)
        list_vehicle[c].cost += distance[0][list_vehicle[c].route[-1]]
        list_vehicle[c].route.append(0)
        list_vehicle[c].pickUp= list_vehicle[c].weight
        c += 1

def route_backhaul_parallel(list_vehicle, dict_merge, dict_b, set_visited, vect_carico, distance, number_of_customers, capacity, number_of_vehicles):
    c = 0

    while(c < len(list_vehicle)):
        if len(set_visited) <= number_of_customers:
            merge = list(dict_merge.keys())
            back = list(dict_b.keys())
            for k in merge:
                if list_vehicle[c].route[-1] in k and different(list_vehicle[c].route[-1], k) not in set_visited:
                        list_vehicle[c].add_weight(vect_carico[different(list_vehicle[c].route[-1],k)])
                        list_vehicle[c].add_route(k)
                        set_visited.add(list_vehicle[c].route[-1])
                        list_vehicle[c].add_cost(distance[k[0]][k[1]]) 
                        break
        c += 1


    c = 0
    temp = dict_b.copy()
    set_first = {0}
    i = 0 
    while(i < np.math.factorial(number_of_customers)/(np.math.factorial(number_of_customers-2)*2)):
        lista_keys = list(dict_b.keys())
        flag = True
        for k in lista_keys:
            if list_vehicle[c].route[-1] in k \
            and different(list_vehicle[c].route[-1], k) not in set_visited \
            and list_vehicle[c].weight + vect_carico[different(list_vehicle[c].route[-1],k)] <= capacity:

                    list_vehicle[c].add_weight(vect_carico[different(list_vehicle[c].route[-1],k)])
                    list_vehicle[c].add_route(k)           
                    set_visited.add(list_vehicle[c].route[-1])
                    list_vehicle[c].add_cost(distance[k[0]][k[1]])
                    set_first.add(k[0])
                    break

        #remove_first_instance(dict_l, set_first)
        c = (c + 1) % number_of_vehicles

        i += 1

    for e in list_vehicle:
        e.cost += distance[0][e.route[-1]]
        e.route.append(0)
        e.pickUp= e.weight
    
    
def parser_instance(path):
    #support
    count = 0
    #first 3 lines of the txt file
    number_of_customers=0
    one=0
    number_of_vehicles=0
    #vettori di informazione
    vect_cord=[] #lista/vettore di coppiadi coordinate
    vect_domanda=[] #linehaul
    vect_carico=[] #backhaul
    vec_b=[] #vettore delle istanze backhaul
    vec_l=[] #vettore delle istanze linehaul
    with open(path) as file:
        for line in file:
            #print(line)
            count+=1
            if count  == 1:
                number_of_customers=int((line.split())[0])
            if count  == 2:
                one=int((line.split())[0])
            if count == 3:
                number_of_vehicles=int((line.split())[0])
            if count > 3:
                vect_cord.append((int((line.split())[0]),int((line.split())[1])))
                vect_domanda.append((int((line.split())[2])))
                vect_carico.append((int((line.split())[3]))) 
                if int((line.split())[3]) == 0:
                    vec_l.append(count-4) #il numero delle istanze linehaul
                if int((line.split())[3]) > 0:
                    vec_b.append(count-4) # il numero delle istanze backhaul

    #capacità massima di ogni mezzo
    capacity=vect_carico[0]
    
    return count, number_of_customers, one, number_of_vehicles, vect_cord, vect_domanda, vect_carico, vec_b, vec_l, capacity

def extract_total_cost_BP(path):
    count=0
    with open(path) as file:
        for line in file:
            count+=1
            if count  == 9:
                return float((line.split())[3])