from gurobipy import (GRB, Model)
from math import inf
import gurobipy as gp


class Modelo:

    def __init__(self) -> None:
        # Leer los archivos
        with open('limites.csv', 'r') as limites:
            limites_header = limites.readline().split(',')
            self.limites = [line.strip().split(',')
                            for line in limites.readlines()]
            self.largo_limites = len(self.limites)

        with open('costos.csv', 'r') as costos:
            costos_header = costos.readline()
            self.costos = [costo.strip() for costo in costos.readlines()]

        with open('contenidos_nutricionales.csv', 'r') as contenidos:
            self.contenidos_header = contenidos.readline().strip().split(',')
            self.contenidos = [line.strip().split(',')
                               for line in contenidos.readlines()]
            # Definicion de parametros:
            self.J = {cereal: costo for cereal, costo in zip(
                self.contenidos_header, self.costos)}
            self.I = {i+1: (self.limites[i][0], self.limites[i][1])
                      for i in range(len(self.limites))}

        self.a_ij = {i + 1: {self.contenidos_header[j]: self.contenidos[i][j]
                             for j in range(len(self.J))} for i in range(len(self.I))}
        self.T = range(60)

    def implementar_modelo(self) -> tuple:
        # Implementando el modelo
        model = gp.Model()

        # Variables
        x_mit = model.addVars(self.M, self.I, self.T,
                              vtype=GRB.INTEGER, name="x_mit")
        y_it = model.addVars(self.I, self.T, vtype=GRB.BINARY, name="y_it")
        z_it = model.addVars(self.I, self.T, vtype=GRB.BINARY, name="z_it")
        a_mt = model.addVars(self.M, self.T, vtype=GRB.INTEGER, name="a_mt")
        b_mit = model.addVars(self.M, self.I, self.T,
                              vtype=GRB.INTEGER, name="b_mit")
        d_mit = model.addVars(self.M, self.I, self.T,
                              vtype=GRB.CONTINOUS, name="d_mit")
        s_mt = model.addVars(self.M, self.T, vtype=GRB.INTEGER, name="s_mt")

        # Agregamos las variables al modelo
        model.update()

        # Restricciones
        model.addConstrs(s_mt[m, t - 1] + a_mt[m, t] == s_mt[m, t] + sum(b_mit[m, i, t]
                         for i in self.I) for m in self.M for t in range(1, len(self.T)))

        model.addConstr(a_mt[m, 0] == s_mt[m, 0] + sum(b_mit[m, i, 0] for i in self.I)
                        for m in self.M)
        N = inf
        model.addConstrs(N * sum(y_it[i, t_1] for t_1 in range(0, t)) >= x_mit[m, i, t] for m in self.M
                         for i in self.I for t in range(len(self.T)))
        model.addConstrs(sum(y_it[i, t] for t in range(
            len(self.T))) <= 1 - EI[i] for i in self.I)
        model.addConstrs(
            K >= sum(sum(x_mit[m, i, t] for i in self.I) * phi[m] for m in self.M))

        # Función objetivo
        objetivo = quicksum(float(self.J[j]) * x_j[j] for j in self.J.keys())
        model.setObjective(objetivo, GRB.MINIMIZE,)

        # Optimizamos el problema
        model.optimize()
        return model, x_j

    def manejo_soluciones(self, model, x_j):

        # Manejo de soluciones
        print("\n"+"-"*10+" Manejo Soluciones "+"-"*10)
        print(f"El valor objetivo es de: {model.ObjVal}", "{peso/kg}")
        print()
        print("Variables de decision:")

        for j in self.J:
            print(f"Se debe utilizar {x_j[j].x} kilogramos de {j}")
        print("\n"+"-"*9+" Restricciones Activas "+"-"*9)

        for constr in model.getConstrs():
            if constr.getAttr("slack") == 0:
                print(f"La restriccion {constr} está activa")


if __name__ == '__main__':
    modelo = Modelo()
    modelo.manejo_soluciones(*modelo.implementar_modelo())
