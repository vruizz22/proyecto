from faker import Faker
import pandas as pd
from os import path

Faker.seed(0)

T = range(1, 61)
I = range(1, 13)
M = range(1, 3)

ruta_costo_int = path.join('parametros', 'costo_inst')
ruta_costo_kw = path.join('parametros', 'costo_kw')
ruta_costo_man = path.join('parametros', 'costo_man')
ruta_demanda = path.join('parametros', 'demanda')


def crear_datos_mit(M, I, T, fake, rango_random, ruta, nombre):
    aumento = {
        'costo_mantenimiento': 1 + (5/120),
        'costo_instalacion_cargador': 1 + (12/120),
        'demanda': 1 + (70/120),
        'costo_energia_kw': 1 + (25/1200)
    }
    for t in T:
        df = pd.DataFrame(index=['Cargador ' + str(m) for m in M],
                          columns=['Estación ' + str(i) for i in I])
        for m in M:
            for i in I:
                df.at['Cargador ' + str(m), 'Estación ' + str(i)] = fake.random_int(
                    min=int(rango_random[0] * aumento[nombre] ** (t/12)), max=int(rango_random[1] * aumento[nombre] ** (t/12)))
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


def crear_datos_mi(M, I, nombre):
    df = pd.DataFrame(index=['Cargador ' + str(m) for m in M],
                      columns=['Estación ' + str(i) for i in I])
    for m in M:
        for i in I:
            df.at['Cargador ' + str(m), 'Estación ' + str(i)
                  ] = 1 if i == 5 else (2 if i == 10 else 0)

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
        'Cargador 1': 2520,
        'Cargador 2': 7920
    }
    df = pd.DataFrame(index=capacidad_carga.keys(),
                      data=capacidad_carga.values())
    ruta = path.join('parametros', f'{nombre}')
    df.to_csv(f'{ruta}.csv')


def crear_datos_i(I, nombre):
    diccionario = {
        f'Estación {i}': 1 if i == 5 or i == 10 else 0
        for i in I
    }
    df = pd.DataFrame(index=diccionario.keys(), data=diccionario.values())
    ruta = path.join('parametros', f'{nombre}')
    df.to_csv(f'{ruta}.csv')


parametros_mit = {
    'D_mit': (M, I, T, Faker(), [80, 100], ruta_demanda, 'demanda'),
    'CC_mit': (M, I, T, Faker(), [1800000, 5500000], ruta_costo_int, 'costo_instalacion_cargador'),
    'CKW_mit': (M, I, T, Faker(), [72000, 144000], ruta_costo_kw, 'costo_energia_kw'),
    'CM_mit': (M, I, T, Faker(), [70000, 120000], ruta_costo_man, 'costo_mantenimiento')
}

parametros_mt = {
    'CP_mt': (M, T, Faker(), [1600000, 1700000], 'costo_compra'),
    'CS_mt': (M, T, Faker(), [50000, 150000], 'costo_almacenamiento')
}

parametros_it = {
    'CI_it': (I, T, Faker(), [1707077, 40813109], 'costo_instalacion_electrica')
}
parametros_i = {
    'EI_i': (I, 'infraestructura_existente')
}
parametros_m = {
    'phi_m': ['capacidad_carga']
}
parametros_mi = {
    'EC_mi': (M, I, 'cargadores_existentes')
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
parametros_sin_dimension('delta', 300)
parametros_sin_dimension('K', 22200)
parametros_sin_dimension('AM', 80)
