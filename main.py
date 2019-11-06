from tkinter import *
from tkinter import ttk
from functools import partial
import copy
import pprint

operadores = ["","AND","OR","NOT"]
regras = []
saida = {
    "descricao" : "Jogar",
    "atributos" : []
}

entradas,saidas = [], []
entradasNomes,saidasNomes = [], []

## -- Pré cadastro --

temp = { "descricao" : "Temperatura", "atributos" : [] }

frio = {"descricao" : "Frio", "iniSuporte" : 0, "fimSuporte" : 16, "iniNucleo" : 0, "fimNucleo" : 10 }
morna = {"descricao" : "Morna", "iniSuporte" : 10, "fimSuporte" : 28, "iniNucleo" : 18, "fimNucleo" : 23 }
quente = {"descricao" : "Quente", "iniSuporte" : 20, "fimSuporte" : 45, "iniNucleo" : 24, "fimNucleo" : 45 }

sim = {"descricao" : "Sim"}
nao = {"descricao" : "Nao"}

temp["atributos"].append(frio)
temp["atributos"].append(morna)
temp["atributos"].append(quente)

saida["atributos"].append(sim)
saida["atributos"].append(nao)

entradas.append(temp)
entradasNomes.append(temp['descricao'])

saidas.append(saida)
saidasNomes.append(saida['descricao'])

def addEntrada(nome):
    entrada = {
        "descricao" : nome,
        "atributos" : []
    }
    c = copy.deepcopy(entrada)
    entradas.append(c)
    entradasNomes.append(nome)
    boxInp.insert(END, nome)
    print (f"Nova entrada adicionada! {nome}")

def remEntrada(nome):
    print(f'Removeu {nome}')

def retornaAtributos(nome):
    retorno = []
    for entrada in entradas:
        if entrada["descricao"] == nome:
            atr = ([atributo["descricao"] for atributo in entrada["atributos"]])
            retorno = atr
            break
        retorno.append('')
    return retorno

def retornaAtributosSaida(nome):
    retorno = []
    for saida in saidas:
        if saida["descricao"] == nome:
            atr = ([atributo["descricao"] for atributo in saida["atributos"]])
            retorno = atr
            break
        retorno.append('')
    return retorno

def ativarCondicoes():
    global checkState
    if (checkState == 1):
        comboOperator.current(0)
        comboOperator.configure(state='normal')
        comboEntr2.configure(state='normal')
        comboCampo2.configure(state='normal')
        checkState = 0
    else:
        comboOperator.current(0)
        comboOperator.configure(state='disabled')
        comboEntr2.configure(state='disabled')
        comboCampo2.configure(state='disabled')
        checkState = 1

def addInput_click():
    inp = enInp.get()
    if (len(inp)>0):
        if (inp not in ([entrada['descricao'] for entrada in entradas])):
            addEntrada(inp)
        else:
            print("Variável já cadastrada!")
    else:
        print("Campo vazio!")

def addCampo_click():
    inp,campo = comboEntrCampo.get(), enAtr.get()
    iniSuporte, fimSuporte = enIniSup.get(), enFimSup.get()
    iniNucleo, fimNucleo = enIniNucleo.get(), enFimNucleo.get()
    if (len(inp) > 0 and len(campo) > 0 and len(iniSuporte) > 0 and len(iniNucleo) > 0 and len(fimSuporte) > 0 and len(fimNucleo) > 0):
        todosCampos = []
        atr = copy.deepcopy([entrada['atributos'] for entrada in entradas if entrada['descricao'] == inp][0])
        for idx,atributo in enumerate(atr):
            todosCampos.append(atributo['descricao'])
        if (campo not in todosCampos):
            novoAtributo = {
                "descricao"  : campo,
                "iniSuporte" : iniSuporte,
                "fimSuporte" : fimSuporte,
                "iniNucleo"  : iniNucleo,
                "fimNucleo"  : fimNucleo
            }
            new = copy.deepcopy(novoAtributo)
            for entrada in entradas:
                if entrada["descricao"] == inp:
                    entrada["atributos"].append(new)
                    pprint.pprint(entrada)
            print(f'Adicionou {campo} á {inp}')
        else:
            print(f'Campo já cadastrado! {campo}')
    else:
        print("Preencha todos os campos antes de inserir novo Atributo á entrada!")

def remInput_click():
    try:
        selectedItem = boxInp.curselection()
        name = boxInp.get(boxInp.curselection())
        entradasNomes.pop(selectedItem[0])
        boxInp.delete(selectedItem[0])
        for idx,entrada in enumerate(entradas):
            if entrada['descricao'] == name:
                entradas.pop(idx)
                break
        print (f"Entradas restantes: {entradasNomes}")
    except:
        print ("Selecione um item da lista!")

def remRule_click():
    try:
        selectedItem = boxRules.curselection()
        boxRules.delete(selectedItem)
    except:
        print('Selecione um item da lista!')

def updateCboxEntrada(box):
    box['values'] = entradasNomes

def updateCboxVariaveis(box):
    try:
        box['values'] = retornaAtributos(comboEntr1.get())
    except:
        box['values'] = ''
        print("Adicione campos para a variável de entrada!")

def updateCboxVariaveis2(box):
    try:
        box['values'] = retornaAtributos(comboEntr2.get())
    except:
        box['values'] = ''
        print("Adicione campos para a variável de entrada!")

def addRule_click():
    rule = ""
    valor = checkState
    if (valor == 1):
        rule = f"{comboEntr1.get()} = {comboCampo1.get()} THEN {comboSaida.get()} = {comboCampoSaida.get()}"
    else:
        rule = f"{comboEntr1.get()} = {comboCampo1.get()} {comboOperator.get()} {comboEntr2.get()} = {comboCampo2.get()} THEN {comboSaida.get()} = {comboCampoSaida.get()}"
    boxRules.insert(END, rule)
    regras.append(rule)

janela = Tk()
janela.title("Janela Principal")
janela.resizable(False,False)
#janela["bg"] = "green"
janela.geometry("455x660")

checkState = IntVar()
checkState = 1

frameAddInput = LabelFrame(janela, text="Inserir variável de entrada")
frameAddInput.place(x=5,y=5,height=80,width=280)

frameInputSelect = LabelFrame(janela, text="Variáveis de entrada")
frameInputSelect.place(x=300,y=5,height=225,width=150)

frameAddAtributo = LabelFrame(janela, text="Inserir campo á entrada")
frameAddAtributo.place(x=5, y=90, height=170, width=280)

frameAddRegras = LabelFrame(janela, text="Inserir regra")
frameAddRegras.place(x=5, y=265, height=180, width=445)

frameListaRegras = LabelFrame(janela, text="Regras")
frameListaRegras.place(x=5, y=450, height=200,width=445)

lbInp = Label(frameAddInput, text="Descrição")

lbEntrAtributo = Label(frameAddAtributo, text="Entrada")
lbCampoAtributo = Label(frameAddAtributo, text="Campo")
lbIniSuporte = Label(frameAddAtributo, text="In. Sup.")
lbFimSuporte = Label(frameAddAtributo, text="Fim Sup.")
lbIniNucleo = Label(frameAddAtributo, text="In. Nucleo")
lbFimNucleo = Label(frameAddAtributo, text="Fim Nucleo")

lbEntr1 = Label(frameAddRegras, text="Entrada")
lbIgual1 = Label(frameAddRegras, text="=")
lbCampo1 = Label(frameAddRegras, text="Campos")
lbOp = Label(frameAddRegras, text="Operador")

lbIgual2 = Label(frameAddRegras, text="=")
lbThen = Label(frameAddRegras, text="THEN")
lbSaida = Label(frameAddRegras, text="Saida")
lbIgual3 = Label(frameAddRegras, text="=")


checkAtivar = Checkbutton(frameAddRegras, text="Mais", variable=checkState, command=ativarCondicoes)

comboEntrCampo = ttk.Combobox(frameAddAtributo, values=entradasNomes, width=15)
comboEntrCampo["postcommand"] = partial(updateCboxEntrada, comboEntrCampo)

comboEntr1 = ttk.Combobox(frameAddRegras, values=entradasNomes,width=15)
comboEntr1["postcommand"] = partial(updateCboxEntrada, comboEntr1)
comboEntr1.current(0)

comboEntr2 = ttk.Combobox(frameAddRegras, values=entradasNomes,width=15, state='disabled')
comboEntr2["postcommand"] = partial(updateCboxEntrada, comboEntr2)
comboEntr2.current(0)

comboCampo1 = ttk.Combobox(frameAddRegras, values=retornaAtributos(comboEntr1.get()),width=15)
comboCampo1["postcommand"] = partial(updateCboxVariaveis, comboCampo1)

comboCampo2 = ttk.Combobox(frameAddRegras, values=retornaAtributos(comboEntr2.get()),width=15, state='disabled')
comboCampo2["postcommand"] = partial(updateCboxVariaveis2, comboCampo2)

comboOperator = ttk.Combobox(frameAddRegras, values=operadores,width=5, state='disabled')

comboSaida = ttk.Combobox(frameAddRegras, values=saidasNomes, width=15)
comboSaida.current(0)
comboCampoSaida = ttk.Combobox(frameAddRegras, values=retornaAtributosSaida(comboSaida.get()), width=15)


enInp = Entry(frameAddInput, width=25)
enAtr = Entry(frameAddAtributo, width=20)
enIniSup = Entry(frameAddAtributo, width=7)
enFimSup = Entry(frameAddAtributo, width=7)
enIniNucleo = Entry(frameAddAtributo, width=8)
enFimNucleo = Entry(frameAddAtributo, width=8)

btInp = Button(frameAddInput, width=10, text="Add", command=addInput_click)
btrmInp = Button(frameInputSelect, width=7, text="Delete", command=remInput_click)
btrmRule = Button(frameListaRegras, width=10, text="Delete Rule", command=remRule_click)
btAddRule = Button(frameAddRegras, width=10, text="Add Rule", command=addRule_click)
btCampo = Button(frameAddAtributo, width=10, text="Add campo", command=addCampo_click)
scrInp = Scrollbar(frameInputSelect, orient=VERTICAL)
scrRules = Scrollbar(frameListaRegras, orient=VERTICAL)

boxInp = Listbox(frameInputSelect, height=10)
scrInp.config(command=boxInp.yview)
scrInp.place(x=128,y=5,height=165)

boxRules = Listbox(frameListaRegras, width=69,height=8)
scrRules.config(command=boxRules.yview)
scrRules.place(x=422,y=5,height=132)


lbInp.place(x=5, y=5)
enInp.place(x=5, y=25)
btInp.place(x=165, y=20)
btrmInp.place(x=80,y=175)

lbEntrAtributo.place(x=5, y=5)
lbCampoAtributo.place(x=135, y=5)
comboEntrCampo.place(x=5, y=30)
enAtr.place(x=135, y=30)
lbIniSuporte.place(x=5, y=60)
lbFimSuporte.place(x=60, y=60)
lbIniNucleo.place(x=130, y=60)
lbFimNucleo.place(x=190, y=60)
enIniSup.place(x=10, y=90)
enFimSup.place(x=65, y=90)
enIniNucleo.place(x=135, y=90)
enFimNucleo.place(x=195, y=90)
btCampo.place(x=190, y=120)

lbEntr1.place(x=5, y=5)
lbCampo1.place(x=157, y=5)
lbIgual1.place(x=130, y=30)
lbOp.place(x=290,y=5)
comboEntr1.place(x=5,y=30)
comboCampo1.place(x=160,y=30)
comboOperator.place(x=290,y=30)
checkAtivar.place(x=350,y=30)

lbIgual2.place(x=130, y=60)
comboEntr2.place(x=5,y=60)
comboCampo2.place(x=160,y=60)
lbThen.place(x=290,y=60)

lbSaida.place(x=5, y=90)
lbIgual3.place(x=130, y=110)
comboSaida.place(x=5, y=110)
comboCampoSaida.place(x=160, y=110)
btAddRule.place(x=290, y=108)
btrmRule.place(x=335, y=150)

#lbInpList.place(x=300, y=10)
boxInp.place(x=5, y=5)
boxRules.place(x=5, y=5)

for entr in entradasNomes:
    boxInp.insert(END, entr)

print(checkState)

janela.mainloop()
