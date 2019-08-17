import pandas as pd
import numpy as np
import string
from collections import Counter

import networkx as nx
from bokeh.io import show, output_file, output_notebook
from bokeh.plotting import figure
from bokeh.models.graphs import from_networkx

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

