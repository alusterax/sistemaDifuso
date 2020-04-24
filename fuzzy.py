import matplotlib.pyplot as plt
import numpy as np
import jsons
import json
import io
import base64
import pprint
from PIL import Image

saidasLoad, entradasLoad, regrasLoad = [], [], []

saidas, entradas, regras = [], [], []
inputs = []

class Atributo(jsons.JsonSerializable):

    def __repr__(self):
        return f'Desc: {self.descricao},Ini Sup:{self.iniSuporte},Fim Sup: {self.fimSuporte},Ini Nucleo: {self.iniNucleo},Fim Nucleo: {self.fimNucleo},Pertinencia: {self.pertinencia}'

    def __init__(self, descricao, iniSuporte, fimSuporte, iniNucleo, fimNucleo, temSubida, temDescida, pertinencia):
        self.descricao = descricao
        self.iniSuporte = iniSuporte
        self.fimSuporte = fimSuporte
        self.iniNucleo = iniNucleo
        self.fimNucleo = fimNucleo
        self.temSubida = temSubida
        self.temDescida = temDescida
        self.pertinencia = 0

    ## -- Funções --
    def calcPertinencia(self, x):
        if self.temSubida and self.temDescida:
            self.pertinencia = self.curvaAmbos(x)
        elif self.temSubida:
            self.pertinencia = self.curvaSubida(x)
        elif self.temDescida:
            self.pertinencia = self.curvaDescida(x)

    def curvaSubida(self,x):
        #left shaft
        if (x <= int(self.iniSuporte)):
            return 0
        elif (x >= int(self.iniNucleo) and x <= int(self.fimNucleo)):
            return 1
        else:
            return ((x - int(self.iniNucleo)) / (int(self.iniNucleo) - int(self.iniSuporte)))

    def curvaDescida(self,x):
        #right shaft
        if (x >= int(self.fimSuporte)):
            return 0
        elif (x >= int(self.iniNucleo) and x <= int(self.fimNucleo)):
            return 1
        else:
            return ((int(self.fimSuporte) - x) / (int(self.fimSuporte) - int(self.fimNucleo)))

    def curvaAmbos(self,x):
        if (x <= int(self.iniSuporte) or x >= int(self.fimSuporte)):
            return 0
        elif (x >= int(self.iniNucleo) and x <= int(self.fimNucleo)):
            return 1
        elif (x >= int(self.iniSuporte) and x <= int(self.iniNucleo)):
            return (x - int(self.iniSuporte)) / (int(self.iniNucleo) - int(self.iniSuporte))
        elif (x >= int(self.fimNucleo) and x <= int(self.fimSuporte)):
            return (int(self.fimSuporte) - x) / (int(self.fimSuporte) - int(self.fimNucleo))

class Variavel(jsons.JsonSerializable):
    def __init__(self, descricao, atributos, isSaida, input):
        self.descricao = descricao
        self.atributos = self.atributosDictToAtributos(atributos)
        self.isSaida = isSaida
        self.input = input

    def __repr__(self):
        return f'Descrição: {self.descricao} INPUT :{self.input} Atributos: {self.atributos}'

    def atributosDictToAtributos(self, atributos):
        atrib = []
        for atributo in atributos:
            atrib.append(jsons.loads(jsons.dumps(atributo),Atributo))
        return atrib

    def getAtributeByName(self, name):
        for atributo in self.atributos:
            if name.casefold() == atributo.descricao.casefold():
                return atributo

    def getUniverso(self):
        universo = [None,None]
        for atrib in self.atributos:
            if universo[0] == None:
                universo[0] = atrib.iniSuporte
                universo[1] = atrib.fimSuporte
            else:
                universo[0] = atrib.iniSuporte if atrib.iniSuporte < universo[0] else universo[0]
                universo[1] = atrib.fimSuporte if atrib.fimSuporte > universo[1] else universo[1]
        return universo

    def plot(self, doClear):
        legenda = []
        for atributo in self.atributos:
            yPositions = []
            legenda.append(atributo.descricao)
            if atributo.temSubida and atributo.temDescida:
                yPositions = [0,1,1,0]
            elif atributo.temSubida and not atributo.temDescida:
                yPositions = [0,1,1,1]
            elif not atributo.temSubida and atributo.temDescida:
                yPositions = [1,1,1,0]
            plt.plot([atributo.iniSuporte,atributo.iniNucleo,atributo.fimNucleo,atributo.fimSuporte],yPositions)
        plt.legend(legenda, loc='lower left')
        plt.title(self.descricao, loc='center')
        bytes_image = io.BytesIO()
        plt.savefig(bytes_image, format='PNG')
        if (doClear):
            plt.clf()
        return bytes_image

class Regra(jsons.JsonSerializable):
    # SE 0  TEMP 1  = 2 ALTA 3  E 4  HUMI 5 = 6 MEDIA 7 ENTAO IRRIGACAO 9 = BAIXA 11
    def __init__(self, descricao):
        self.descricao = descricao.split(' ')
        self.finalResult = 0

    def __repr__(self):
        return f'Regra: '

class Projeto():

    def __init__(self, variaveis, regras):
        self.variaveis = variaveis
        self.regras = regras
        self.ruleSetValues = {}


    def fuzzify(self):
        self.calculaPertinencias()
        return self.ativacaoDosAntecedentes()

    def calculaPertinencias(self):
        print(f'_______________________________________\n\n        Pertinencias em Atributos        ')
        for variavel in self.variaveis:
            if variavel.isSaida:
                continue
            print(f'_______________________________________\n\n(Variável: {variavel.descricao}) | (Entrada: {variavel.input})\n ......................................')
            for atributo in variavel.atributos:
                atributo.calcPertinencia(variavel.input)
                print(f'(Atributo: {atributo.descricao}) | Pertinencia: {atributo.pertinencia}')

    def getVariavleByName(self, name):
        for variavel in self.variaveis:
            if name.casefold() == variavel.descricao.casefold():
                return variavel

    def getObjectiveVariable(self):
        for variavel in self.variaveis:
            if variavel.isSaida:
                return variavel

    def ativacaoDosAntecedentes(self):
        self.ruleSetValues = {}
        universo = self.getObjectiveVariable().getUniverso()
        alvos = []
        saidasResult = []
        objetivo = None
        print(f'_____________________________________________________________________________________________\n\n                          Pertinencias em Regras                          ')
        for regra in self.regras:
            var1 = self.getVariavleByName(regra.descricao[1])
            atrib1 = var1.getAtributeByName(regra.descricao[3])
            operator = regra.descricao[4]
            var2 = self.getVariavleByName(regra.descricao[5])
            atrib2 = var2.getAtributeByName(regra.descricao[7])
            varObjet = self.getVariavleByName(regra.descricao[9])
            objetivo = varObjet
            atribObjet = varObjet.getAtributeByName(regra.descricao[11])
            if operator.casefold() == 'AND'.casefold():
                result = min([atrib1.pertinencia, atrib2.pertinencia])
            else:
                result = max([atrib1.pertinencia, atrib2.pertinencia])
            if self.ruleSetValues.get(atribObjet.descricao) == None:
                self.ruleSetValues[atribObjet.descricao] = [result]
                alvos.append(atribObjet)
            else:
                self.ruleSetValues[atribObjet.descricao].append(result)
            print(f'_____________________________________________________________________________________________')
            print(f'\nRegra: {regra.descricao[0]} {regra.descricao[1]} {regra.descricao[2]} {regra.descricao[3]} {regra.descricao[4]} {regra.descricao[5]} {regra.descricao[6]} {regra.descricao[7]} {regra.descricao[8]} {regra.descricao[9]} {regra.descricao[10]} {regra.descricao[11]}')
            print(f'Pertinência: {result}')
        print(f'_____________________________________________________________________________________________\n\nResultado\n')
        for key in self.ruleSetValues:
            self.ruleSetValues[key] = max(self.ruleSetValues[key])
        values = list(self.ruleSetValues.values())
        dividendo = []
        x = []
        y = []
        divisor = []
        for idx,valor in enumerate(values):
            print (f'{alvos[idx].descricao}: {valor}')
        index_max = np.argmax(values)
        print(f'Tendência a saída {alvos[index_max].descricao}')
#       print(values)
        for i,value in enumerate(values):
            # Value é a altura onde vai cortar no plot
            dividendo.append([])
            arrayUniverso = np.arange(int(universo[0]),int(universo[1])+1)
            antAscendente = i > 0 and value > values[i-1]
            posAscendente = (len(values) - 1 >= i + 1  and value < values[i+1])
            for j in arrayUniverso:
                if (j >= int(alvos[i].iniNucleo) and j <= int(alvos[i].fimNucleo)) or (j >= int(alvos[i].iniSuporte) and j <= int(alvos[i].fimSuporte) and (antAscendente or not posAscendente)):
                    dividendo[i].append(j*value)
                    x.append(j)
                    y.append(value)
            divisor.append(value * len(dividendo[i]))
            dividendo[i] = np.sum(dividendo[i])
        sumDivisor = np.sum(divisor)
        objetivo.plot(True)
        plt.fill_between(x,0,y[1])
        bytes_image = io.BytesIO()
        plt.savefig("figura.png", format='PNG')
        plt.clf()
        result = {}
        result['valor'] = np.sum(dividendo)/sumDivisor if sumDivisor != 0 else 0
        result['imagem'] = base64.b64encode(bytes_image.getvalue())
        print(f"Centróide: {result['valor']}")
        return result

## - Utilidade
def loadConfig():
    global saidas, entradas, regras
    with open("config.json") as configJson:
        dadosConfig = json.load (configJson)
        for entrada in dadosConfig['entradas']:
            entradas.append(jsons.loads(jsons.dumps(entrada), Variavel))
        for saida in dadosConfig['saidas']:
            saidas.append(jsons.loads(jsons.dumps(saida), Variavel))
        for regra in dadosConfig['regras']:
            regras.append(jsons.loads(jsons.dumps(regra), Regra))
        

    #entradas, saidas, regras = jsons.loads(dadosConfig['entradas'], Variavel), jsons.loads(dadosConfig['saidas'], Variavel), jsons.loads(dadosConfig['regras'],Regras)


## -- Start
loadConfig()

for entrada in entradas:
    inputs.append(entrada)
for saida in saidas:
    inputs.append(saida)

p = Projeto(inputs, regras)
p.fuzzify()
