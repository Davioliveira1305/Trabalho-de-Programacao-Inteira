import gurobipy as gp
import numpy as np
from pandas import DataFrame
from gurobipy import GRB

def qkp(datafile, var):
    with open(datafile, 'r') as file: linhas = file.readlines()
    
    # remove linha vazia inicial e elimina os "\n" de cada linha
    linhas = [a.strip() for a in linhas]
    
    # dimensão do problema
    n = int(linhas[0])
    
    # diagonal da matriz p
    d = np.fromstring(linhas[1], dtype=int, sep = ' ')
    
    # define o restante da matriz p
    p = np.zeros((n,n), dtype=int) 

    # diagonal principal
    for i in range(n):
        p[i][i] = d[i]
        
    # elementos fora da diagonal
    for i in range(n-1):
        linha = np.fromstring(linhas[i+2], dtype=int, sep = ' ')
        for j in range(n-(i+1)):
            p[i][j+i+1] = linha[j]
            p[j+i+1][i] = p[i][j+i+1]
            
    # capacidade
    c = int(linhas[n+2])

  
    
    # pesos
    w = np.fromstring(linhas[n+3], dtype=int, sep = ' ')
    
    m = gp.Model("qkp")
    
    # define variaveis
#    x = []
#    for j in range(n):
#        x.append(m.addVar(vtype=GRB.BINARY,name="x"))
    x = m.addVars(n, vtype= var, name="x")


    #Matriz Yij
    y=[]
    for i in range(0,n):
        l = []
        for j in range(0,n):
            l.append(m.addVar(vtype= var, name="y"))
        y.append(l)

    # define função objetivo
#    obj = None
#    for i in range(0, n):
#        obj += p[i][i] * x[i]
#        for j in range(i+1, n):
#            obj += 2*p[i][j] * y[i][j]
#    m.setObjective(obj, GRB.MAXIMIZE)
    m.setObjective(
        gp.quicksum(p[i][i]*x[i] + 
        gp.quicksum(2* p[i][j] * y[i][j] for j in range(i+1,n)) for i in range(n)) , 
        GRB.MAXIMIZE
    )
    
    # define restrições
#    constr = None
#    for j in range(0, n):
#        constr += (w[j] * x[j])
#    m.addConstr(constr <= c)
    m.addConstr(gp.quicksum(w[i]*x[i] for i in range(n)) <= c)

    for i in range(0, n):
        for j in range(i+1, n):
            m.addConstr(y[i][j] <= x[i])

    for i in range(0, n):
        for j in range(i+1, n):
            m.addConstr(y[i][j] <= x[j])

 
    #Parâmetros
    m.Params.TimeLimit = 300
    m.Params.MIPGap = 0.0001
    m.Params.Method = 1
    m.Params.NodeMethod = 1
    m.Params.Threads = 1

    if var == GRB.BINARY:
        return m, x, y

    
    # gera .lp ou .mps
    #  m.write("qkp.lp")
    #  m.write("qkp.mps")
    
    # resolve o problema
    m.optimize()
    for i in range(0, n):
        x[i] = x[i].X
        for j in range(i+1, n):
            y[i][j] = y[i][j].X
    # verifica status e imprime alguns atributos
    return ['Relaxado', m.status, m.objVal, m.objBound, 0 , m.Runtime, m.NodeCount], x, y

if __name__ == "__main__":
    tabela = []
    vetor = [
        "D:\\TrabalhoPI\\TrabalhoPI\\trab_comp_04\\grupo1\\100_50_2.txt",
    ]
    x, y = None, None
    x_i = None
    y_i = None
    for datafile in vetor:
        resultado, x, y = qkp(datafile, GRB.CONTINUOUS)
        integer, x_i, y_i = qkp(datafile, GRB.BINARY)
        for i in range(0, 100):
            for j in range(i+1, 100):
                if(x[i] + x[j] > y[i][j] + 1):
                    integer.addConstr(x_i[i] + x_i[j] <= y_i[i][j] + 1)
        integer.optimize()
        resultado2 = ['Inteiro', integer.status, integer.objVal, integer.objBound, integer.MIPGap , integer.Runtime, integer.NodeCount]
        tabela.append(resultado)
        tabela.append(resultado2)
    df = DataFrame(tabela)
    df.rename(columns={0: 'Tipo do Problema', 1: 'Status', 2: 'ObjVal', 3: 'ObjBound', 4: 'Gap', 5: 'Runtime', 6: 'Número de Nodes'}, inplace=True)
    print(df)




