import pandas as pd
from gurobipy import GRB
import gurobipy as gp
from os import path
from math import inf


def leer_archivo(archivo: str) -> list:
    return pd.read_csv(archivo).iloc[:, 1:].values


class Modelo:

    def __init__(self) -> None:

        # Cardinalidad de los conjuntos
        self.T = range(1, 61)
        self.I = range(1, 14)
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
            'AM': path.join('parametros', 'AM.csv')
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

        # Lectura de archivos
        # y creación de parametros

        '''
        Crear parametros
        \item $D_{mit}$, demanda total de cargadores tipo $m$ en la estación $i$ para el periodo $t$. (cantidad de autos demandados)
        \item $CI_{it}$, el costo de instalar la infraestructura el\'ectrica en el periodo $t$ para la estaci\'on $I$. (pesos)
        \item $CP_{mt}$, el costo de comprar un cargador tipo $m$ en el periodo $t$. (pesos)
        \item $CC_{mit}$, el costo de instalar un cargador tipo $m$ en la estación $i$ en el periodo $t$. (pesos)
        \item $CKW_{mit}$, el costo de energía eléctrica por kilowatt-mes para un cargador tipo $m$ en la estación $i$ en el periodo $t$. (pesos)
        \item $CM_{mit}$, el costo de mantención de un cargador tipo $m$ en la estación $i$ en el periodo $t$. (pesos)

        \item $\alpha$, coeficiente de ganancia espera por el precio seleccionado, por KW de electricidad vendido. (sin dimensión)
        \item $\delta$, cantidad de KW que se espera que cargue un vehículo eléctrico en un mes. (kw)
        item $K$, la capacidad eléctrica máxima que permite la infraestructura eléctrica. (kw/mes)

        \item $\phi_m$, capacidad de carga por mes de un cargador tipo $m$ en KW. (kw/mes)
        \item $EI_{i}$, si ya existe la infraestructura eléctrica en la estación $i$. (sin dimensión)(binaria)
        \item $EC_{mi}$, la cantidad de estaciones de carga de tipo $m$ que ya existen en la estación $i$ en el mes $t$ (sin dimensión)
        \item $CS_{mt}$, el costo de almacenar un cargador tipo $m$ en el periodo $t$.(pesos)
        \item $AM$, atonomía minimia de un vehículo eléctrico en KM. (km)
        '''
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
        self.alpha = leer_archivo(ruta_archivos['alpha'])[0, 0]
        self.delta = leer_archivo(ruta_archivos['delta'])[0, 0]
        self.K = leer_archivo(ruta_archivos['K'])[0, 0]
        self.phi_m = {
            m: leer_archivo(ruta_archivos['capacidad_carga'])[m - 1, 0]
            for m in self.M
        }
        self.AM = leer_archivo(ruta_archivos['AM'])[0, 0]
        self.EI_i = {
            i: leer_archivo(ruta_archivos['infraestructura_existente'])[
                i - 1, 0]
            for i in self.I
        }
        self.EC_mi = {
            (m, i): leer_archivo(ruta_archivos['cargadores_existentes'])[m - 1, i - 1]
            for m in self.M for i in self.I
        }

        # FALTA DEFINIR d_ij

    def implementar_modelo(self):
        # Implementamos el modelo
        model = gp.Model()

        '''
        	\subsection{Variables de decisión}
	\begin{itemize}
		\item $x_{mit}$ cantidad de cargadores tipo $m$ en la estación $i$ para el periodo $t$.
		\item \[
			      y_{it} =
			      \begin{cases}
				      1 & \quad\text{si se instala la infraestructura eléctrica para }i\text{ en }t \\
				      0 & \quad\text{en cualquier otro caso.}
			      \end{cases}
		      \]
		\item \[
			      z_{it} =
			      \begin{cases}
				      1 & \quad\text{si existe la infraestructura eléctrica para }i\text{ en }t \\
				      0 & \quad\text{en cualquier otro caso.}
			      \end{cases}
		      \]
		\item $a_{mt}$, cantidad de cargadores tipo $m$ que se compran en el periodo $t$.
		\item $b_{mit}$, cantidad de cargadores tipo $m$ que se instalan en la estación $i$ en el periodo $t$.
		\item $d_{mit}$, (Cant. de vehiculos)demanda que se va a satisfacer para cargadores tipo $m$ en la estación $i$ en el periodo $t$.
		\item $S_{mt}$, cantidad de cargadores almacenados de tipo $m$ el periodo $t$.
        '''

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

        '''
        		\item Restricción de inventario, incluyendo la condici\'on inicial (\textit{storage}).
		      \begin{align*}
			       & S_{m(t-1)} + a_{mt} = S_{mt} + \sum_{i \in I} b_{mit} &  & \forall \; m \in M, t \in \{2, \ldots, 60\} \\
			       & a_{m1} = S_{m1} + \sum_{i \in I} b_{mi1}              &  & \forall \; m \in M
		      \end{align*}
		\item Restricción de cantidad de cargadores instalados ($x$) que solo puede ser mayor a $0$ cuando se instala la infraestructura eléctrica ($y$).
		      \begin{align*}
			       & N \cdot \sum_{t'=1}^{t} y_{it'} \geq x_{mit} &  & \forall \; m \in M, \; i \in I,\; t \in \{1, \ldots, 60\}
		      \end{align*}
		\item S\'olo se puede instalar la infraestructura el\'ectrica una vez si no se ha instalado antes ($EI$).
		      \begin{align*}
			       & \sum_{t \in T} y_{it} \leq 1 - EI_i &  & \forall \; i \in I
		      \end{align*}
		\item La capacidad en KW de los cargadores instalados ($x$) no puede superar la capacidad m\'axima de KW de la infraestructura el\'ectrica ($K$).
		      \begin{align*}
			       & K \geq \sum_{m \in M} \sum_{i \in I} x_{mit} \cdot \phi_m &  & \forall \; i \in I, \; t \in \{1, \ldots, 60\}
		      \end{align*}
		\item Solo puede haber infraestructura el\'ectrica en una ubicaci\'on ($z$) si se ha instalado anteriormente ($y$)
		      \begin{align*}
			       & z_{it} \leq \sum_{t'=1}^{t} y_{it'} &  & \forall \; i \in I, \; t \in \{1, \ldots, 60\} \\
			       & z_{it} \geq y_{it} + z_{i(t-1)}     &  & \forall \; i \in I, \;t \in \{2, \ldots, 60\}  \\
			       & z_{i1} \geq y_{i1} + EI_i           &  & \forall \; i \in I
		      \end{align*}
		\item Solo puede haber un centro de carga en una ubicaci\'on $j$ existe al menos una estaci\'on cuya distancia es menor a la distancia m\'axima permitida ($AM$).
		      \begin{align*}
			       & \sum_{i \in I: i \neq j, d_{ij}\leq AM} z_{it} \geq 1 &  & \forall \; j \in I, \; t \in \{1, \ldots, 60\}
		      \end{align*}
		\item La cantidad de cargadores en una estaci\'on ($x$) debe ser igual a la cantidad instalada en el periodo más la existente en el periodo anterior, considerando la condici\'on inicial.
		      \begin{align*}
			       & x_{mit} = b_{mit} + x_{mi(t-1)} &  & \forall \; m \in M, \; i \in I, \; t \in \{2, \ldots, 60\} \\
			       & x_{mi1} = b_{mi1} + EC_{mi}     &  & \forall \; m \in M, \; i \in I
		      \end{align*}
		\item La demanda a satisfacer, entendida como cantidad de vehículos, no puede superar la demanda total de cargadores en una estación.
		      \begin{align*}
			       & d_{mit} \leq D_{mit} &  & \forall \; m \in M, \; i \in I, \; t \in \{1, \ldots, 60\}
		      \end{align*}
		\item La cantidad de KW que se van a proveer no puede superar la capacidad de carga de los cargadores instalados.
		      \begin{align*}
			       & \delta \cdot d_{mit} \leq x_{mit} \cdot \phi_m &  & \forall \; m \in M, \; i \in I, \; t \in \{1, \ldots, 60\}
		      \end{align*}
        '''
        # Actualizamos el modelo
        model.update()

        # Restricciones
        model.addConstrs(
            (S_mt[m, t - 1] + a_mt[m, t] == S_mt[m, t] + sum(b_mit[m, i, t] for i in self.I)
             for m in self.M for t in self.T if t >= 1),
            name='restriccion_inventario'
        )
        model.addConstrs(
            (a_mt[m, 1] == S_mt[m, 1] + sum(b_mit[m, i, 1] for i in self.I)
             for m in self.M),
            name='restriccion_inventario_inicial'
        )
        N = inf
        model.addConstrs(
            (N * sum(y_it[i, t_] for t_ in range(1, t + 1)) >= x_mit[m, i, t]
             for m in self.M for i in self.I for t in self.T),
            name='restriccion_infraestructura'
        )
        model.addConstrs(
            (sum(y_it[i, t] for t in self.T) <= 1 - self.EI_i[i]
             for i in self.I),
            name='restriccion_infraestructura_unica'
        )
        model.addConstrs(
            (self.K >= sum(x_mit[m, i, t] * self.phi_m[m]
                           for m in self.M for i in self.I)
             for t in self.T),
            name='restriccion_capacidad'
        )
        model.addConstrs(
            (z_it[i, t] <= sum(y_it[i, t_] for t_ in range(1, t + 1))
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
            (sum(z_it[j, t_] for j in self.I if j != i and d_ij <= self.AM) >= 1
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


if __name__ == '__main__':
    modelo = Modelo()
