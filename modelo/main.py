import pandas as pd
from gurobipy import GRB, quicksum
import gurobipy as gp
from os import path
import locale


def leer_archivo(archivo: str) -> list:
    return pd.read_csv(archivo).iloc[:, 1:].values


def leer_archivo_mixto(archivo: str) -> list:
    return pd.read_csv(archivo).values.tolist()


def crear_resultados(I, T, valores_z_it, ei):
    data = leer_archivo_mixto(path.join('mapa', 'data.csv'))

    # Filtrar las estaciones que existen según ei
    data_inicial = [data[i - 1] for i in I if ei[i] == 1]

    # Crear data0.csv en la carpeta data
    df_inicial = pd.DataFrame(
        data_inicial, columns=['Latitude', 'Longitude', 'Title', 'Description'])
    df_inicial.to_csv(path.join('mapa', 'data', 'data0.csv'), index=False)

    for t in T:
        dfs = []  # Lista para almacenar los dataframes
        for i in I:
            if valores_z_it[(i, t)]:  # Si la estación tiene infraestructura eléctrica
                df = pd.DataFrame(
                    data=[data[i - 1]], columns=['Latitude', 'Longitude', 'Title', 'Description'])
                dfs.append(df)

        # Concatenar todos los dataframes y eliminar filas con valores faltantes
        df_final = pd.concat(dfs).dropna()

        ruta = path.join('mapa', 'data', f'data{t}')
        df_final.to_csv(f'{ruta}.csv', index=False)


class Modelo:

    def __init__(self) -> None:

        # Cardinalidad de los conjuntos
        self.T = range(1, 61)
        self.I = range(1, 13)
        self.M = range(1, 3)

        ruta_archivos = {
            'capacidad_carga': path.join('parametros', 'capacidad_carga.csv'),
            'costo_almacenamiento': path.join('parametros', 'costo_almacenamiento.csv'),
            'cargadores_existentes': path.join('parametros', 'cargadores_existentes.csv'),
            'costo_compra': path.join('parametros', 'costo_compra.csv'),
            'costo_instalacion_electrica': path.join('parametros', 'costo_instalacion_electrica.csv'),
            'infraestructura_existente': path.join('parametros', 'infraestructura_existente.csv'),
            'alpha': path.join('parametros', 'alpha.csv'),
            'delta': path.join('parametros', 'delta.csv'),
            'K': path.join('parametros', 'K.csv'),
            'AM': path.join('parametros', 'AM.csv'),
            'd_ij': path.join('parametros', 'distance.csv')
        }
        ruta_archivos_demanda = {
            f'demanda{t}': path.join('parametros', 'demanda', f'demanda{t}.csv')
            for t in self.T
        }
        ruta_archivos_costo_man = {
            f'costo_mantenimiento{t}': path.join('parametros', 'costo_man', f'costo_mantenimiento{t}.csv')
            for t in self.T
        }
        ruta_archivos_costo_kw = {
            f'costo_energia_kw{t}': path.join('parametros', 'costo_kw', f'costo_energia_kw{t}.csv')
            for t in self.T
        }
        ruta_archivos_costo_int = {
            f'costo_instalacion_cargador{t}': path.join('parametros', 'costo_inst', f'costo_instalacion_cargador{t}.csv')
            for t in self.T
        }

        # Lectura de archivos y creación de parametros

        self.D_mit = {
            (m, i, t): leer_archivo(ruta_archivos_demanda[f'demanda{t}'])[m - 1, i - 1]
            for m in self.M for i in self.I for t in self.T
        }
        self.CI_it = {
            (i, t): leer_archivo(ruta_archivos['costo_instalacion_electrica'])[i - 1, t - 1]
            for i in self.I for t in self.T
        }
        self.CP_mt = {
            (m, t): leer_archivo(ruta_archivos['costo_compra'])[m - 1, t - 1]
            for m in self.M for t in self.T
        }
        self.CC_mit = {
            (m, i, t): leer_archivo(ruta_archivos_costo_int[f'costo_instalacion_cargador{t}'])[m - 1, i - 1]
            for m in self.M for i in self.I for t in self.T
        }
        self.CKW_mit = {
            (m, i, t): leer_archivo(ruta_archivos_costo_kw[f'costo_energia_kw{t}'])[m - 1, i - 1]
            for m in self.M for i in self.I for t in self.T
        }
        self.CM_mit = {
            (m, i, t): leer_archivo(ruta_archivos_costo_man[f'costo_mantenimiento{t}'])[m - 1, i - 1]
            for m in self.M for i in self.I for t in self.T
        }
        self.alpha = leer_archivo(ruta_archivos['alpha']).flatten()[0]
        self.delta = leer_archivo(ruta_archivos['delta']).flatten()[0]
        self.K = leer_archivo(ruta_archivos['K']).flatten()[0]
        self.phi_m = {
            m: leer_archivo(ruta_archivos['capacidad_carga'])[m - 1, 0]
            for m in self.M
        }
        self.AM = leer_archivo(ruta_archivos['AM']).flatten()[0]
        self.EI_i = {
            i: leer_archivo(ruta_archivos['infraestructura_existente'])[
                i - 1, 0]
            for i in self.I
        }
        self.EC_mi = {
            (m, i): leer_archivo(ruta_archivos['cargadores_existentes'])[m - 1, i - 1]
            for m in self.M for i in self.I
        }
        self.CS_mt = {
            (m, t): leer_archivo(ruta_archivos['costo_almacenamiento'])[m - 1, t - 1]
            for m in self.M for t in self.T
        }
        self.d_ij = {
            (i, j): leer_archivo(ruta_archivos['d_ij'])[i - 1, j - 1]
            for i in self.I for j in self.I if i != j
        }

    def implementar_modelo(self):
        # Implementamos el modelo
        model = gp.Model()

        # Variables de decisión
        x_mit = model.addVars(self.M, self.I, self.T,
                              vtype=GRB.INTEGER, name='x_mit')
        y_it = model.addVars(self.I, self.T,
                             vtype=GRB.BINARY, name='y_it')
        z_it = model.addVars(self.I, self.T, vtype=GRB.BINARY, name='z_it')
        a_mt = model.addVars(self.M, self.T, vtype=GRB.INTEGER, name='a_mt')
        b_mit = model.addVars(self.M, self.I, self.T,
                              vtype=GRB.INTEGER, name='b_mit')
        d_mit = model.addVars(self.M, self.I, self.T,
                              vtype=GRB.INTEGER, name='d_mit')
        S_mt = model.addVars(self.M, self.T, vtype=GRB.INTEGER, name='S_mt')

        # Actualizamos el modelo
        model.update()

        # Restricciones
        model.addConstrs(
            (S_mt[m, t - 1] + a_mt[m, t] == S_mt[m, t] + quicksum(b_mit[m, i, t] for i in self.I)
             for m in self.M for t in self.T if t >= 2),
            name='restriccion_inventario'
        )
        model.addConstrs(
            (a_mt[m, 1] == S_mt[m, 1] + quicksum(b_mit[m, i, 1] for i in self.I)
             for m in self.M),
            name='restriccion_inventario_inicial'
        )
        N = 10000000000
        model.addConstrs(
            (N * z_it[i, t] >= x_mit[m, i, t]
             for m in self.M for i in self.I for t in self.T),
            name='restriccion_infraestructura'
        )
        model.addConstrs(
            (quicksum(y_it[i, t] for t in self.T) <= 1 - self.EI_i[i]
             for i in self.I),
            name='restriccion_infraestructura_unica'
        )
        model.addConstrs(
            (quicksum(x_mit[m, i, t] * self.phi_m[m]
             for m in self.M) <= self.K for i in self.I for t in self.T),
            name='restriccion_capacidad'
        )
        model.addConstrs(
            (z_it[i, t] <= quicksum(y_it[i, t_] for t_ in range(1, t + 1)) + self.EI_i[i]
             for i in self.I for t in self.T),
            name='restriccion_infraestructura_existente'
        )
        model.addConstrs(
            (z_it[i, t] >= y_it[i, t] + z_it[i, t - 1]
             for i in self.I for t in self.T if t >= 2),
            name='restriccion_infraestructura_existente_2'
        )
        model.addConstrs(
            (z_it[i, 1] >= y_it[i, 1] + self.EI_i[i]
             for i in self.I),
            name='restriccion_infraestructura_existente_3'
        )
        model.addConstrs(
            (quicksum(z_it[j, t] for j in self.I if j != i and float(self.d_ij[(i, j)]) <= float(self.AM)) >= z_it[i, t]
             for i in self.I for t in self.T),
            name='restriccion_distancia'
        )
        model.addConstrs(
            (x_mit[m, i, t] == b_mit[m, i, t] + x_mit[m, i, t - 1]
             for m in self.M for i in self.I for t in self.T if t >= 2),
            name='restriccion_cantidad_cargadores'
        )
        model.addConstrs(
            (x_mit[m, i, 1] == b_mit[m, i, 1] + self.EC_mi[m, i]
             for m in self.M for i in self.I),
            name='restriccion_cantidad_cargadores_inicial'
        )
        model.addConstrs(
            (d_mit[m, i, t] <= self.D_mit[m, i, t]
             for m in self.M for i in self.I for t in self.T),
            name='restriccion_demanda'
        )
        model.addConstrs(
            (self.delta * d_mit[m, i, t] <= x_mit[m, i, t] * self.phi_m[m]
             for m in self.M for i in self.I for t in self.T),
            name='restriccion_carga'
        )

        # Función objetivo
        model.setObjective(quicksum(d_mit[m, i, t] * self.CKW_mit[(m, i, t)] * (self.alpha - 1)
                                    - x_mit[m, i, t] * self.CM_mit[(m, i, t)] - b_mit[m, i, t] * self.CC_mit[(m, i, t)]
                                    for m in self.M for i in self.I for t in self.T)
                           - quicksum(a_mt[m, t] * self.CP_mt[(m, t)]
                                      for t in self.T for m in self.M)
                           - quicksum(self.CS_mt[(m, t)] * S_mt[m, t]
                                      for t in self.T for m in self.M)
                           - quicksum(y_it[i, t] * self.CI_it[(i, t)] for t in self.T for i in self.I), GRB.MAXIMIZE)

        # Optimizamos el modelo
        model.optimize()

        if model.status == GRB.INFEASIBLE:
            # Imprimir las restricciones que hacen que el modelo sea infactible
            print('El modelo es infactible')
            model.computeIIS()
            model.write('modelo.ilp')
            return None

        elif model.status == GRB.UNBOUNDED:
            print('El modelo es no acotado')
            return None

        elif model.status == GRB.INF_OR_UNBD:
            print('El modelo es infactible o no acotado')
            return None

        else:
            valores_z_it = {
                (i, t): z_it[i, t].X for i in self.I for t in self.T
            }
            crear_resultados(self.I, self.T, valores_z_it, self.EI_i)
            return model.ObjVal


if __name__ == '__main__':
    modelo = Modelo()
    ov = modelo.implementar_modelo()
    if ov is not None:
        locale.setlocale(locale.LC_ALL, '')
        print(
            f'\033[1;32mLa ganancia esperada es de {locale.currency(ov, grouping=True)}\033[0m')
