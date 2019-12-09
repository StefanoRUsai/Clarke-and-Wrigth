from os.path import dirname
import pyximport; pyximport.install()
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askopenfile, askdirectory
from tkinter.filedialog import asksaveasfile
from tkinter import ttk
import os
from utils import *
import time
from os import getcwd, listdir
import pandas as pd

if not os.path.isdir('Risultati_seriale'):
    os.system('mkdir Risultati_seriale')

if not os.path.isdir('Risultati_parallelo'):
    os.system('mkdir Risultati_parallelo')
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
        folder = True
        only_file = False

def save():
    files = [('Text Document', '*.txt')]
    file = asksaveasfile(filetypes = files, defaultextension = files)

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
        record = {}

        start = time.time()
        for e in instances:
            folder_instances = path_global
            folder_rpa_solutions = 'RPA_Solutions/'
            path = folder_instances + e + '.txt'
            path_solutions = folder_rpa_solutions + 'Detailed_Solution_' + e + '.txt'
            start_instances = time.time()
            count, number_of_customers, one, number_of_vehicles, \
            vect_cord, vect_domanda, vect_carico, vec_b, vec_l, capacity = parser_instance(path)

            distance = distance_matrix(vect_cord)
            saving = saving_matrix(distance)
            dict_Saving_Order = savingOrder(saving)
            dict_b, dict_l, dict_merge = route_Linehaul_Backhaul(dict_Saving_Order, vec_b, vec_l)
            list_vehicle, set_visited = init_list_of_vehicle(dict_l, vect_domanda, distance, number_of_vehicles)
            route_linehaul_parallel(number_of_customers, dict_l, list_vehicle, vect_domanda, set_visited, distance,
                                    capacity, number_of_vehicles)  # funzione void
            route_backhaul_parallel(list_vehicle, dict_merge, dict_b, set_visited, vect_carico, distance,
                                    number_of_customers, capacity, number_of_vehicles)  # funzione void
            tot_cost = sum([x.cost for x in list_vehicle])
            record[e] = round(((tot_cost * 100) / extract_total_cost_BP(path_solutions)) - 100, 2)
            duration_instances = time.time() - start_instances
            with open(f'Risultati_parallelo/our_results_{e}.txt', "w") as the_file:
                the_file.write(f"Text File with Solution Of {e}\n\n")
                the_file.write(f"PROBLEM DETAILS:\n")
                the_file.write(f"Customers = {number_of_customers} \n")
                the_file.write(f"Max Load = {capacity} \n\n")

                the_file.write(f"SOLUTION DETAILS:\n")
                the_file.write(f"Total cost = {tot_cost}\n")
                the_file.write(f"Error = {round(((tot_cost * 100) / extract_total_cost_BP(path_solutions)) - 100, 2)}\n")
                the_file.write(f"Time = {duration_instances}:\n\n")
                the_file.write(f"Routes of the Solution = {len(list_vehicle)}:\n\n")

                for i,e in enumerate(list_vehicle):
                    the_file.write(f"ROUTE {i+1}:\n")
                    the_file.write(f"Cost = {e.cost}:\n")
                    the_file.write(f"Vertex sequence: \n"
                                   f"{e.route}:\n\n")


        duration = time.time() - start
        tot_errore = 0
        for e in record.keys():
            tot_errore += record[e]
        mean_error=tot_errore / len(record)

        list_record = []
        for e in record.keys():
            list_record.append([e, record[e]])

#        df = pd.DataFrame(list_record, columns=['Instances', 'Error'])
#        df.to_csv('parallelo.csv')

        result = f'tempo di esecuzione {duration}\n'\
                 f'percentuale errore rispetto a best solution {mean_error}'
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
        route_linehaul_parallel(number_of_customers, dict_l, list_vehicle, vect_domanda, set_visited, distance, capacity, number_of_vehicles)  # funzione void
        route_backhaul_parallel(list_vehicle, dict_merge, dict_b, set_visited, vect_carico, distance, number_of_customers, capacity, number_of_vehicles)  # funzione void
        tot_cost = sum([x.cost for x in list_vehicle])
        duration = time.time() - start

        with open(f'Risultati_parallelo/our_results_{n_instance}.txt', "w") as the_file:
            the_file.write(f"Text File with Solution Of {e}\n\n")
            the_file.write(f"PROBLEM DETAILS:\n")
            the_file.write(f"Customers = {number_of_customers} \n")
            the_file.write(f"Max Load = {capacity} \n\n")

            the_file.write(f"SOLUTION DETAILS:\n")
            the_file.write(f"Total cost = {tot_cost}\n")
            the_file.write(f"Time = {duration}:\n\n")
            the_file.write(f"Error = {round(((tot_cost * 100) / extract_total_cost_BP(path_solutions))-100 , 2)}\n")
            the_file.write(f"Routes of the Solution = {len(list_vehicle)}:\n\n")
            for i, e in enumerate(list_vehicle):
                the_file.write(f"ROUTE {i}:\n")
                the_file.write(f"Cost = {e.cost}:\n")
                the_file.write(f"Vertex sequence: \n"
                               f"{e.route}:\n\n")


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
        record = {}

        start = time.time()
        for e in instances:
            folder_instances = path_global
            folder_rpa_solutions = 'RPA_Solutions/'
            path = folder_instances + e + '.txt'
            path_solutions = folder_rpa_solutions + 'Detailed_Solution_' + e + '.txt'
            start_instances = time.time()
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
            duration_instances = time.time() - start_instances
            with open(f'Risultati_seriale/our_results_{e}.txt', "w") as the_file:
                the_file.write(f"Text File with Solution Of {e}\n\n")
                the_file.write(f"PROBLEM DETAILS:\n")
                the_file.write(f"Customers = {number_of_customers} \n")
                the_file.write(f"Max Load = {capacity} \n\n")

                the_file.write(f"SOLUTION DETAILS:\n")
                the_file.write(f"Total cost = {tot_cost}\n")
                the_file.write(f"Error = {round(((tot_cost * 100) / extract_total_cost_BP(path_solutions)) - 100, 2)}\n")
                the_file.write(f"Time = {duration_instances}:\n\n")
                the_file.write(f"Routes of the Solution = {len(list_vehicle)}:\n\n")

                for i, e in enumerate(list_vehicle):
                    the_file.write(f"ROUTE {i}:\n")
                    the_file.write(f"Cost = {e.cost}:\n")
                    the_file.write(f"Vertex sequence: \n"
                                   f"{e.route}:\n\n")

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
        with open(f'Risultati_seriale/our_results_{n_instance}.txt', "w") as the_file:
            the_file.write(f"Text File with Solution Of {n_instance}\n\n")
            the_file.write(f"PROBLEM DETAILS:\n")
            the_file.write(f"Customers = {number_of_customers} \n")
            the_file.write(f"Max Load = {capacity} \n\n")

            the_file.write(f"SOLUTION DETAILS:\n")
            the_file.write(f"Total cost = {tot_cost}\n")
            the_file.write(f"Error = {round(((tot_cost * 100) / extract_total_cost_BP(path_solutions))-100 , 2)}\n")
            the_file.write(f"Time = {duration}:\n\n")
            the_file.write(f"Routes of the Solution = {len(list_vehicle)}:\n\n")

            for i, e in enumerate(list_vehicle):
                the_file.write(f"ROUTE {i}:\n")
                the_file.write(f"Cost = {e.cost}:\n")
                the_file.write(f"Vertex sequence: \n")
                the_file.write(f"{e.route}:\n\n")


        result = f'tempo di esecuzione {duration}\n' \
                 f'percentuale errore rispetto a best solution {round(((tot_cost * 100) / extract_total_cost_BP(path_solutions))-100 , 2)}'
        text_box.delete('1.0', END)
        text_box.insert("end-1c", result)


def exit1():
    exit()


if __name__ == '__main__':

    label = Label(window, text="Gruppo H19")
    label.pack()

    btn1 = Button(window, text='Open Folder', width=10, command=openDirectory)
    btn1.place(x=10, y=20)

    btn2 = Button(window, text='Open File', width=10,command=open_file)
    btn2.place(x=10, y=45)

    btn3 = Button(window, text='Run Parallel', width=10, command=run_Parallel)
    btn3.place(x=350, y=70)

    btn7 = Button(window, text='Run Serial', width=10, command=run_Serial)
    btn7.place(x=230, y=70)

    btn5 = Button(window, text='exit', width=10, command=exit1)
    btn5.place(x=350, y=400)


    text_box = Text(window, bg='grey', width=67, height=5)
    text_box.place(x=10, y=200)

    label2 = Label(window, text="I file di salvataggio sono creati nelle cartelle Risultati_parallelo\n"
                                "e Risultati_seriale all'interno della cartella di progetto ")
    label2.place(x=10, y=350)


    window.mainloop()
