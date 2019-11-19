import json

saidasLoad, entradasLoad, regrasLoad = [], [], []

saidas, entradas, regras = [], [], []

class Atributo(atr):

    def __repr__(self):
        return f'{self.descricao} {self.iniSuporte}  {self.fimSuporte} {self.iniNucleo}  {self.fimNucleo}'

    def __init__(self, nome, iniSuporte, fimSuporte, iniNucleo, fimNucleo, objetivo):
        self.descricao = atr['descricao']
        self.iniSuporte = atr['iniSuporte']
        self.fimSuporte = atr['fimSuporte']
        self.iniNucleo = atr['iniNucleo']
        self.fimNucleo = atr['fimNucleo']
        self.temSubida = atr['temSubida']
        self.temDescida = atr['temDescida']
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
        if (x <= self.iniSuporte):
            return 0
        elif (x >= self.iniNucleo and x <= self.fimNucleo):
            return 1
        else:
            return ((x - self.iniNucleo) / (self.iniNucleo - self.iniSuporte))

    def curvaDescida(self,x):
        #right shaft
        if (x >= self.fimSuporte):
            return 0
        elif (x >= self.iniNucleo and x <= self.fimNucleo):
            return 1
        else:
            return ((self.fimSuporte - x) / (self.fimSuporte - self.fimNucleo))

    def curvaAmbos(self,x):
        if (x <= self.iniSuporte or x >= self.fimSuporte):
            return 0
        elif (x >= self.iniNucleo and x <= self.fimNucleo):
            return 1
        elif (x >= self.iniSuporte and x <= self.iniNucleo):
            return (x - self.iniSuporte) / (self.iniNucleo - self.iniSuporte)
        elif (x >= self.fimNucleo and x <= self.fimSuporte):
            return (self.fimSuporte - x) / (self.fimSuporte - self.fimNucleo)

class Variavel(var):
    def __init__(self, descricao, atributos, input, isSaida):
        self.descricao = var['descricao']
        self.atributos = self.atributosDictToAtributos(var['atributos'])
        self.input = input
        self.isSaida = isSaida

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
                universo[0] = atrib.inicioBase
                universo[1] = atrib.fimBase
            else:
                universo[0] = atrib.inicioBase if atrib.inicioBase < universo[0] else universo[0]
                universo[1] = atrib.fimBase if atrib.fimBase > universo[1] else universo[1]
        return universo

    def plot(self, doClear):
        legenda = []
        for atributo in self.atributos:
            yPositions = []
            legenda.append(atributo.name)
            if atributo.hasLeftShaft and atributo.hasRightShaft:
                yPositions = [0,1,1,0]
            elif atributo.hasLeftShaft and not atributo.hasRightShaft:
                yPositions = [0,1,1,1]
            elif not atributo.hasLeftShaft and atributo.hasRightShaft:
                yPositions = [1,1,1,0]
            plt.plot([atributo.inicioBase,atributo.inicioNucleo,atributo.fimNucleo,atributo.fimBase],yPositions)
        plt.legend(legenda, loc='lower left')
        plt.title(self.descricao, loc='center')
        bytes_image = io.BytesIO()
        plt.savefig(bytes_image, format='PNG')
        if (doClear):
            plt.clf()
        return bytes_image

class Projeto():

    def __init__(self, variaveis, regras):
        self.variaveis = variaveis
        self.regras = regras
        self.ruleSetValues = {}


    def fuzzify(self):
        self.calculaPertinencias()
        return self.ativacaoDosAntecedentes()

    def calculaPertinencias(self):
        for variavel in self.variaveis:
            if variavel.isObjective:
                continue
            for atributo in variavel.atributos:
                atributo.calculaPertinencia(variavel.inputValue)

    def getVariavleByName(self, name):
        for variavel in self.variaveis:
            if name.casefold() == variavel.name.casefold():
                return variavel

    def getObjectiveVariable(self):
        for variavel in self.variaveis:
            if variavel.isObjective:
                return variavel

    def ativacaoDosAntecedentes(self):
        self.ruleSetValues = {}
        universo = self.getObjectiveVariable().getUniverso()
        alvos = []
        objetivo = None
        for regra in self.regras:
            print(regra)
            var1 = self.getVariavleByName(regra.descricao[1])
            atrib1 = var1.getAtributeByName(regra.descricao[3])
            operator = regra.descricao[4]
            var2 = self.getVariavleByName(regra.descricao[5])
            atrib2 = var2.getAtributeByName(regra.descricao[7])
            varObjet = self.getVariavleByName(regra.descricao[9])
            objetivo = varObjet
            atribObjet = varObjet.getAtributeByName(regra.descricao[11])
            if operator.casefold() == 'E'.casefold():
                result = min([atrib1.pertinencia, atrib2.pertinencia])
            else:
                result = max([atrib1.pertinencia, atrib2.pertinencia])
            if self.ruleSetValues.get(atribObjet.name) == None:
                self.ruleSetValues[atribObjet.name] = [result]
                alvos.append(atribObjet)
            else:
                self.ruleSetValues[atribObjet.name].append(result)

        for key in self.ruleSetValues:
            self.ruleSetValues[key] = max(self.ruleSetValues[key])

        values = list(self.ruleSetValues.values())
        dividendo = []
        x = []
        y = []
        divisor = []
        print(values)
        for i,value in enumerate(values):

            dividendo.append([])
            arrayUniverso = np.arange(universo[0],universo[1]+1)
            antAscendente = i > 0 and value > values[i-1]
            posAscendente = (len(values) - 1 >= i + 1  and value < values[i+1])
            for j in arrayUniverso:
                if (j >= alvos[i].inicioNucleo and j <= alvos[i].fimNucleo) or (j >= alvos[i].inicioBase and j <= alvos[i].fimBase and (antAscendente or not posAscendente)):
                    dividendo[i].append(j*value)
                    x.append(j)
                    y.append(value)
            divisor.append(value * len(dividendo[i]))
            dividendo[i] = np.sum(dividendo[i])
        sumDivisor = np.sum(divisor)
        objetivo.plot(False)
        plt.fill_between(x,0,y[1])
        bytes_image = io.BytesIO()
        plt.savefig(bytes_image, format='PNG')
        plt.clf()
        result = {}
        result['valor'] = np.sum(dividendo)/sumDivisor if sumDivisor != 0 else 0
        result['imagem'] = base64.b64encode(bytes_image.getvalue())
        return result

## - Utilidade
def loadConfig():
    try:
        global saidas, entradas, regras
        with open("config.json") as configJson:
            dadosConfig = json.load (configJson)
        entradas, saidas, regras = dadosConfig['entradas'], dadosConfig['saidas'], dadosConfig['regras']
    except:
        print ('Não há arquivo de configuração disponível!')

## -- Start
loadConfig()
