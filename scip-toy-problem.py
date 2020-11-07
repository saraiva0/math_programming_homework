from __future__ import print_function
from ortools.linear_solver import pywraplp
from graphviz import Digraph

solver = pywraplp.Solver.CreateSolver('SCIP')

CUSTO_INFINITO = 3000

custos = [
            [CUSTO_INFINITO, 5, 3, 17, 1],
            [5, CUSTO_INFINITO, 6, 5, 9],
            [3, 6, CUSTO_INFINITO, 3, 3],
            [17, 5, 3, CUSTO_INFINITO, 2],
            [1, 9, 3, 2, CUSTO_INFINITO],
         ]

# custos = [
#             [CUSTO_INFINITO, 500, 300, 170, 1],
#             [5, CUSTO_INFINITO, 60, 50, 90],
#             [300, 6, CUSTO_INFINITO, 30, 30],
#             [1700, 500, 3, CUSTO_INFINITO, 200],
#             [1000, 900, 300, 2, CUSTO_INFINITO],
#          ]

num_planetas = len(custos)

dot = Digraph(comment='TSP Galaxies') # Cria o grafo direcionado
dot.format = 'svg' # Muda o formato do arquivo de saida

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

# Garante que, ao sair de uma galaxia, tenha-se somente uma outra galaxia como destin
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
  print('Total cost = ', solver.Objective().Value(), '\n')
  count = 0
  i = 0
  while (count < 5):
    for j in range(num_planetas):
        # Test if x[i,j] is 1 (with tolerance for floating point arithmetic).
        if x[i, j].solution_value() > 0.5:
            print('%d -> %d.  Cost = %d' %
               (i, j, custos[i][j]))
            dot.edge(str(i), str(j), constraint='false') # Adiciona as arestas no grafo
            i = j
            break
    count += 1

dot.render('grafo') # Save o arquivo no formato SVG
