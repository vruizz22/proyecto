from faker import Faker
import pandas as pd
from os import path

Faker.seed(0)
'''
Crear parametros
\item $D_{mit}$, demanda total de cargadores tipo $m$ en la estación $i$ para el periodo $t$. () cantidad autos
\item $CI_{it}$, el costo de instalar la infraestructura el\'ectrica en el periodo $t$ para la estaci\'on $I$. 
\item $CP_{mt}$, el costo de comprar un cargador tipo $m$ en el periodo $t$.
\item $CC_{mit}$, el costo de instalar un cargador tipo $m$ en la estación $i$ en el periodo $t$.
\item $CKW_{mit}$, el costo de energía eléctrica por kilowatt-hora para un cargador tipo $m$ en la estación $i$ en el periodo $t$.
\item $CM_{mit}$, el costo de mantención de un cargador tipo $m$ en la estación $i$ en el periodo $t$.

\item $\alpha$, coeficiente de ganancia espera por el precio seleccionado, por KW de electricidad vendido.
\item $\delta$, cantidad de KW que se espera que cargue un vehículo eléctrico en un mes.
\item $K$, la capacidad eléctrica máxima que permite la infraestructura eléctrica.

\item $\phi_m$, capacidad de carga por mes de un cargador tipo $m$ en KW.
\item $EI_{i}$, si ya existe la infraestructura eléctrica en la estación $i$.
\item $EC_{mi}$, la cantidad de estaciones de carga de tipo $m$ que ya existen en la estación $i$ en el mes $t$
\item $CS_{mt}$, el costo de almacenar un cargador tipo $m$ en el periodo $t$.
\item $AM$, atonomía minimia de un vehículo eléctrico en KM.
'''

'''
conjuntos:
t \in {1, 60}
i \in {1, 25}
m \in {1, 2}
'''

T = range(1, 61)
I = range(1, 13)
M = range(1, 3)

ruta_costo_int = path.join('parametros', 'costo_inst')
ruta_costo_kw = path.join('parametros', 'costo_kw')
ruta_costo_man = path.join('parametros', 'costo_man')
ruta_demanda = path.join('parametros', 'demanda')


def crear_datos_mit(M, I, T, fake, rango_random, ruta, nombre):
    aumento = {
        'costo_mantenimiento': 1 + (5/1200),
        'costo_instalacion_cargador': 1 + (12/1200),
        'demanda': 1 + (70/1200),
        'costo_energia_kw': 1 + (25/1200)
    }
    for t in T:
        df = pd.DataFrame(index=['Cargador ' + str(m) for m in M],
                          columns=['Estación ' + str(i) for i in I])
        for m in M:
            for i in I:
                df.at['Cargador ' + str(m), 'Estación ' + str(i)] = fake.random_int(
                    min=rango_random[0], max=rango_random[1]) * (aumento[nombre] ** (t-1))
        # Convertir el DataFrame a csv
        df.to_csv(f'{ruta}/{nombre}{t}.csv')


def crear_datos_mt(M, T, fake, rango_random, nombre):
    df = pd.DataFrame(index=['Cargador ' + str(m) for m in M],
                      columns=['Periodo ' + str(t) for t in T])
    for m in M:
        for t in T:
            df.at['Cargador ' + str(m), 'Periodo ' + str(t)] = fake.random_int(
                min=rango_random[0], max=rango_random[1])

    ruta = path.join('parametros', f'{nombre}')
    df.to_csv(f'{ruta}.csv')


def crear_datos_mi(M, I, fake, rango_random, nombre):
    df = pd.DataFrame(index=['Cargador ' + str(m) for m in M],
                      columns=['Estación ' + str(i) for i in I])
    for m in M:
        for i in I:
            df.at['Cargador ' + str(m), 'Estación ' + str(i)] = fake.random_int(
                min=rango_random[0], max=rango_random[1])

    ruta = path.join('parametros', f'{nombre}')
    df.to_csv(f'{ruta}.csv')


def crear_datos_it(I, T, fake, rango_random, nombre):
    df = pd.DataFrame(index=['Estación ' + str(i) for i in I],
                      columns=['Periodo ' + str(t) for t in T])
    for i in I:
        for t in T:
            df.at['Estación ' + str(i), 'Periodo ' + str(t)] = fake.random_int(
                min=rango_random[0], max=rango_random[1])

    ruta = path.join('parametros', f'{nombre}')
    df.to_csv(f'{ruta}.csv')


def crear_datos_m(nombre):
    capacidad_carga = {
        'Cargador 1': 684,
        'Cargador 2': 2592
    }
    df = pd.DataFrame(index=capacidad_carga.keys(),
                      data=capacidad_carga.values())
    ruta = path.join('parametros', f'{nombre}')
    df.to_csv(f'{ruta}.csv')


def crear_datos_i(I, fake, rango_random, nombre):
    diccionario = {
        f'Estación {i}': fake.random_int(min=rango_random[0], max=rango_random[1])
        for i in I
    }
    df = pd.DataFrame(index=diccionario.keys(), data=diccionario.values())
    ruta = path.join('parametros', f'{nombre}')
    df.to_csv(f'{ruta}.csv')


parametros_mit = {
    'D_mit': (M, I, T, Faker(), [40, 70], ruta_demanda, 'demanda'),
    'CC_mit': (M, I, T, Faker(), [1800000, 5500000], ruta_costo_int, 'costo_instalacion_cargador'),
    'CKW_mit': (M, I, T, Faker(), [72000, 144000], ruta_costo_kw, 'costo_energia_kw'),
    'CM_mit': (M, I, T, Faker(), [10000, 20000], ruta_costo_man, 'costo_mantenimiento')
}

parametros_mt = {
    'CP_mt': (M, T, Faker(), [500000, 700000], 'costo_compra'),
    'CS_mt': (M, T, Faker(), [20000, 40000], 'costo_almacenamiento')
}

parametros_it = {
    'CI_it': (I, T, Faker(), [1707077, 40813109], 'costo_instalacion_electrica')
}
parametros_i = {
    'EI_i': (I, Faker(), [0, 0], 'infraestructura_existente')
}
parametros_m = {
    'phi_m': ['capacidad_carga']
}
parametros_mi = {
    'EC_mi': (M, I, Faker(), [0, 0], 'cargadores_existentes')
}


def parametros_sin_dimension(nombre, num_random):
    df = pd.DataFrame(index=[nombre], data=[num_random])
    ruta = path.join('parametros', f'{nombre}')
    df.to_csv(f'{ruta}.csv')


def crear_csv(parametros, conjunto):
    conjuntos = {
        'mit': crear_datos_mit,
        'mt': crear_datos_mt,
        'it': crear_datos_it,
        'i': crear_datos_i,
        'm': crear_datos_m,
        'mi': crear_datos_mi
    }
    for args in parametros:
        conjuntos[conjunto](*args)


crear_csv(parametros_mit.values(), 'mit')
crear_csv(parametros_mt.values(), 'mt')
crear_csv(parametros_it.values(), 'it')
crear_csv(parametros_i.values(), 'i')
crear_csv(parametros_m.values(), 'm')
crear_csv(parametros_mi.values(), 'mi')
parametros_sin_dimension(
    'alpha', 1.3)
parametros_sin_dimension('delta', 333)
parametros_sin_dimension('K', 12960)
parametros_sin_dimension('AM', 80)
