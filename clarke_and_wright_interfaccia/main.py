from os.path import dirname
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askopenfile, askdirectory
from clarke_and_wright.utils import *
import time
from os import getcwd, listdir
import pandas as pd

import os

window = Tk()
window.geometry('500x500')
window.title('Clarke and Wright')

path_global = ''
only_file = False
folder = False
result = ''
path_file = ''

df = pd.DataFrame()

def open_file():
    global only_file
    global folder
    global path_file

    file = askopenfile(mode='r', filetypes=[('instances Files', '*.txt')])
    folder = False
    only_file = True
    path_file = file.name
    if file is None:
        only_file = False

def openDirectory():
    global only_file
    global folder

    dirname = askdirectory(parent=window, title='Please select a directory')
    if len(dirname) > 0:
        print(f"You chose {dirname}")
        global path_global
        path_global = dirname

def save():
    '''funzione da finire da vedere'''
    df.to_csv('file.csv')

def run_Parallel():
    global df
    global result
    global text_box
    global path_file
    if folder == True:
        global path_global
        path_global = path_global + '/'
        instances = listdir(path_global)
        instances = [x for x in [(x.split('.'))[0] for x in instances] if len(x) == 2]
        print(instances)
        record = {}

        start = time.time()
        for e in instances:
            folder_instances = path_global
            folder_rpa_solutions = 'RPA_Solutions/'
            path = folder_instances + e + '.txt'
            path_solutions = folder_rpa_solutions + 'Detailed_Solution_' + e + '.txt'

            count, number_of_customers, one, number_of_vehicles, \
            vect_cord, vect_domanda, vect_carico, vec_b, vec_l, capacity = parser_instance(path)

            distance = distance_matrix(vect_cord)
            saving = saving_matrix(distance)

            dict_Saving_Order = savingOrder(saving)

            dict_b, dict_l, dict_merge = route_Linehaul_Backhaul(dict_Saving_Order, vec_b, vec_l)

            list_vehicle, set_visited = init_list_of_vehicle(dict_l, vect_domanda, distance, number_of_vehicles)
            route_linehaul(dict_l, list_vehicle, vect_domanda, set_visited, distance, capacity)  # funzione void
            route_backhaul(list_vehicle, dict_merge, dict_b, set_visited, vect_carico, distance, number_of_customers,
                           capacity)  # funzione void
            tot_cost = sum([x.cost for x in list_vehicle])
            record[e] = round(((tot_cost * 100) / extract_total_cost_BP(path_solutions)) - 100, 2)

        duration = time.time() - start
        tot_errore = 0
        for e in record.keys():
            tot_errore += record[e]

        list_record = []
        for e in record.keys():
            list_record.append([e, record[e]])

        df = pd.DataFrame(list_record, columns=['Instances', 'Error'])

        df.to_csv('parallelo.csv')

        result = f'tempo di esecuzione {duration}\n'\
                 f'percentuale errore rispetto a best solution {tot_errore / len(record)}'
        text_box.delete('1.0', END)
        text_box.insert("end-1c", result)

    if only_file == True:
        folder_rpa_solutions = 'RPA_Solutions/'
        path = path_file
        n_instance = path_file.split('/')[-1].split('.')[0]
        path_solutions = folder_rpa_solutions + 'Detailed_Solution_' + n_instance + '.txt'

        start = time.time()
        count, number_of_customers, one, number_of_vehicles, \
        vect_cord, vect_domanda, vect_carico, vec_b, vec_l, capacity = parser_instance(path)

        distance = distance_matrix(vect_cord)
        saving = saving_matrix(distance)
        dict_Saving_Order = savingOrder(saving)
        dict_b, dict_l, dict_merge = route_Linehaul_Backhaul(dict_Saving_Order, vec_b, vec_l)
        list_vehicle, set_visited = init_list_of_vehicle(dict_l, vect_domanda, distance, number_of_vehicles)
        route_linehaul_parallel(dict_l, list_vehicle, vect_domanda, set_visited, distance, capacity)  # funzione void
        route_backhaul_parallel(list_vehicle, dict_merge, dict_b, set_visited, vect_carico, distance, number_of_customers,
                       capacity)  # funzione void
        tot_cost = sum([x.cost for x in list_vehicle])
        duration = time.time() - start


        result = f'tempo di esecuzione {duration}\n' \
                 f'percentuale errore rispetto a best solution {round(((tot_cost * 100) / extract_total_cost_BP(path_solutions))-100 , 2)}'
        text_box.delete('1.0', END)
        text_box.insert("end-1c", result)

        # list_record = []
        # for e in record.keys():
        #     list_record.append([e, record[e]])
        # df = pd.DataFrame(list_record, columns=['Instances', 'Error'])
        # df.to_csv('seriale.csv')

def run_Serial():
    global df
    global result
    global text_box
    global path_file
    if folder == True:
        global path_global
        path_global = path_global + '/'
        instances = listdir(path_global)
        instances = [x for x in [(x.split('.'))[0] for x in instances] if len(x) == 2]
        print(instances)
        record = {}

        start = time.time()
        for e in instances:
            print('sono qui')
            folder_instances = path_global
            folder_rpa_solutions = 'RPA_Solutions/'
            path = folder_instances + e + '.txt'
            path_solutions = folder_rpa_solutions + 'Detailed_Solution_' + e + '.txt'

            count, number_of_customers, one, number_of_vehicles, \
            vect_cord, vect_domanda, vect_carico, vec_b, vec_l, capacity = parser_instance(path)

            distance = distance_matrix(vect_cord)
            saving = saving_matrix(distance)
            dict_Saving_Order = savingOrder(saving)
            dict_b, dict_l, dict_merge = route_Linehaul_Backhaul(dict_Saving_Order, vec_b, vec_l)
            list_vehicle, set_visited = init_list_of_vehicle(dict_l, vect_domanda, distance, number_of_vehicles)
            route_linehaul(dict_l, list_vehicle, vect_domanda, set_visited, distance, capacity)  # funzione void
            route_backhaul(list_vehicle, dict_merge, dict_b, set_visited, vect_carico, distance, number_of_customers,
                           capacity)  # funzione void
            tot_cost = sum([x.cost for x in list_vehicle])
            record[e] = round(((tot_cost * 100) / extract_total_cost_BP(path_solutions)) - 100, 2)

        duration = time.time() - start
        tot_errore = 0
        for e in record.keys():
            tot_errore += record[e]

        list_record = []
        for e in record.keys():
            list_record.append([e, record[e]])

        df = pd.DataFrame(list_record, columns=['Instances', 'Error'])

        df.to_csv('parallelo.csv')

        result = f'tempo di esecuzione {duration}\n'\
                 f'percentuale errore rispetto a best solution {tot_errore / len(record)}'
        text_box.delete('1.0', END)
        text_box.insert("end-1c", result)

    if only_file == True:
        folder_rpa_solutions = 'RPA_Solutions/'
        path = path_file
        n_instance = path_file.split('/')[-1].split('.')[0]
        path_solutions = folder_rpa_solutions + 'Detailed_Solution_' + n_instance + '.txt'

        start = time.time()
        count, number_of_customers, one, number_of_vehicles, \
        vect_cord, vect_domanda, vect_carico, vec_b, vec_l, capacity = parser_instance(path)

        distance = distance_matrix(vect_cord)
        saving = saving_matrix(distance)
        dict_Saving_Order = savingOrder(saving)
        dict_b, dict_l, dict_merge = route_Linehaul_Backhaul(dict_Saving_Order, vec_b, vec_l)
        list_vehicle, set_visited = init_list_of_vehicle(dict_l, vect_domanda, distance, number_of_vehicles)
        route_linehaul(dict_l, list_vehicle, vect_domanda, set_visited, distance, capacity)  # funzione void
        route_backhaul(list_vehicle, dict_merge, dict_b, set_visited, vect_carico, distance, number_of_customers,
                       capacity)  # funzione void
        tot_cost = sum([x.cost for x in list_vehicle])
        duration = time.time() - start


        result = f'tempo di esecuzione {duration}\n' \
                 f'percentuale errore rispetto a best solution {round(((tot_cost * 100) / extract_total_cost_BP(path_solutions))-100 , 2)}'
        text_box.delete('1.0', END)
        text_box.insert("end-1c", result)

        # list_record = []
        # for e in record.keys():
        #     list_record.append([e, record[e]])
        # df = pd.DataFrame(list_record, columns=['Instances', 'Error'])
        # df.to_csv('seriale.csv')

def exit1():
    exit()


if __name__ == '__main__':
    btn1 = Button(window, text='Open Folder', width=10, command=openDirectory)
    btn1.place(x=10, y=20)

    btn2 = Button(window, text='Open File', width=10,command=open_file)
    btn2.place(x=10, y=45)

    btn3 = Button(window, text='Run Parallel', width=10, command=run_Parallel)
    btn3.place(x=350, y=70)

    btn7 = Button(window, text='Run Serial', width=10, command=run_Serial)
    btn7.place(x=250, y=70)

    btn4 = Button(window, text='Save', width=10, command=save)
    btn4.place(x=350, y=95)

    btn5 = Button(window, text='exit', width=10, command=exit1)
    btn5.place(x=350, y=400)


    text_box = Text(window, bg='grey', width=67, height=5)
    text_box.place(x=10, y=200)

    window.mainloop()
