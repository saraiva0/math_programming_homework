from __future__ import print_function
from ortools.linear_solver import pywraplp
from graphviz import Digraph

def calcula_distancias(cidade, cidades):
  distancias = []
  for i in range(0, len(cidades)):
    dist = (((float(cidades[i][1]) - float(cidade[0])) ** 2) + (((float(cidades[i][2]) - float(cidade[1])) ** 2))) ** 1/2
    if dist == 0:
      dist = 10000000000
    distancias.append(dist)

  return distancias

solver = pywraplp.Solver.CreateSolver('SCIP')

ref_arq = open('wi29.tsp')

cidades = []

for line in ref_arq:
  cidade = line.split()
  cidades.append(cidade)

custos = []

for i in range(0, len(cidades)):
  coord = (cidades[i][1], cidades[i][2])
  distancia = calcula_distancias(coord, cidades)
  custos.append(distancia)

'''
CUSTO_INFINITO = 3000

custos = [
            [CUSTO_INFINITO, 10, 5, 85, 23],
            [10, CUSTO_INFINITO, 45, 71, 99],
            [5, 45, CUSTO_INFINITO, 5, 21],
            [85, 71, 5, CUSTO_INFINITO, 9],
            [23, 99, 21, 9, CUSTO_INFINITO],
        ]
'''

num_planetas = len(custos)

dot = Digraph(comment='TSP Galaxies') # Cria o grafo direcionado
dot.format = 'jpg' # Muda o formato do arquivo de saida

for i in range(num_planetas): # Adiciona os nohs ao grafo
    dot.node(str(i), str(i))


# --------------- Definicoes das variaveis ------------------
# x[i, j] corresponde aos xij do problema, e sao 0 ou 1
x = {}
for i in range(num_planetas):
    for j in range(num_planetas):
        x[i, j] = solver.IntVar(0, 1, '')

y = {}
for i in range(num_planetas):
   y[i] = solver.IntVar(1, (num_planetas - 1), '')
# --------------- End Definicoes das variaveis --------------



# ------------------------  Restricoes ----------------------
# Garante que cada vertice so pode ser visitado uma unica vez
for i in range(num_planetas):
    solver.Add(solver.Sum([x[i, j] for j in range(num_planetas)]) == 1)

# Garante que, ao sair de uma galaxia, tenha-se somente uma outra galaxia como destino
for j in range(num_planetas):
    solver.Add(solver.Sum([x[i, j] for i in range(num_planetas)]) == 1)

# Garante que nao havera subrotas
for i in range(1, num_planetas):
   for j in range(1,  num_planetas):
      solver.Add((x[i, j] * (num_planetas - 1) + y[i] - y[j]) <= (num_planetas - 2))
# --------------------- End Restricoes ---------------------



# --------------------  Funcao Objetivo --------------------
objective_terms = []
for i in range(num_planetas):
    for j in range(num_planetas):
        objective_terms.append(custos[i][j] * x[i, j])
solver.Minimize(solver.Sum(objective_terms))
# ------------------  End Funcao Objetivo ------------------

status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
  print('Total cost = ', round(solver.Objective().Value(), 1), '\n')
  count = 0
  i = 0
  while (count < 5):
    for j in range(num_planetas):
        # Test if x[i,j] is 1 (with tolerance for floating point arithmetic).
        if x[i, j].solution_value() == 1.0:
            print('%d -> %d.  Cost = %d' %
               (i, j, custos[i][j]))
            dot.edge(str(i), str(j), constraint='false', label=str(custos[i][j])) # Adiciona as arestas no grafo
            i = j
            break
    count += 1

dot.render('grafo') # Salva o arquivo no formato SVG
