from flask import Flask, render_template, request, session
import datetime
from cidade import ApiCidade
from atracao import ApiAtracao
from passagem import ApiPassagem
from hospedagem import ApiHospedagem
from models import Cidade, Passagem, Hospedagem, Atracao, Pacote

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template('Home.html')

@app.route("/passagem", methods=["POST"])
def get_response():
    origem = request.form.get('origem')
    destino = request.form.get('destino')
    session["passageiros"] = request.form.get('passageiros')
    session["data_ida"] = request.form.get('data_ida')
    session["data_volta"] = request.form.get('data_volta')

    #CONSULTA CIDADE - consultar se a cidade ja foi procurada antes
    print("########## CONSULTA CIDADE (ORIGEM) ##########")
    res = Cidade.consultaCidade(origem)
    #NÃO TEM ORIGEM
    if res == None:
        session['tem_origem'] = False
        print("Não tem origem")
        print("########## EXECUTANDO API CIDADE (ORIGEM) ##########")
        dict_origem = ApiCidade.get_location(origem) #API CIDADE
        session["dict_origem"] = dict_origem
        cidade = Cidade.criaCidade(dict_origem) 
        Cidade.cadastraCidade(cidade) #ARMAZENA NO BANCO
    #TEM ORIGEM
    else:
        print(res)
        session['tem_origem'] = True
        session["dict_origem"] = res
    
    print("\n########## CONSULTA CIDADE (DESTINO) ##########")
    res = Cidade.consultaCidade(destino)
    #NÃO TEM DESTINO
    if res == None:
        session['tem_destino'] = False
        print("Não tem destino")
        print("########## EXECUTANDO API CIDADE (DESTINO) ##########")
        dict_destino = ApiCidade.get_location(destino) #API CIDADE
        session["dict_destino"] = dict_destino
        cidade = Cidade.criaCidade(dict_destino) 
        Cidade.cadastraCidade(cidade) #ARMAZENA NO BANCO
    #TEM DESTINO
    else:
        print(res)
        session['tem_destino'] = True
        session["dict_destino"] = res
    
    #CONSULTA PASSAGEM - consultar se tem passagem para a cidade naquela data
    print("\n########## CONSULTA PASSAGEM (IDA) ##########")
    res = Passagem.consultaPassagem(session["dict_origem"]["location_id"], session["dict_destino"]["location_id"], session["data_ida"])

    #NÃO TEM PASSAGEM IDA
    if res == None:
        print("Não tem passagem ida")
        print("########## EXECUTANDO API PASSAGEM (IDA) ##########")
        dict_ida = ApiPassagem.get_passagem(session['data_ida'], session['passageiros'], session["dict_origem"]['aero_code'], session["dict_destino"]['aero_code']) #API PASSAGEM #É UMA LISTA
        lista_passagens = []
        for passagem in dict_ida:
            lista_passagens.append(Passagem.criaPassagem(passagem, session["dict_origem"]['location_id'], session["dict_destino"]['location_id'])) 
        Passagem.cadastraPassagens(lista_passagens) #ARMAZENA NO BANCO
    #TEM PASSAGEM IDA
    else:
        dict_ida = res
    
    print("\n########## CONSULTA PASSAGEM (VOLTA) ##########")
    res = Passagem.consultaPassagem(session["dict_destino"]["location_id"], session["dict_origem"]["location_id"], session["data_volta"])
    
    #NÃO TEM PASSAGEM VOLTA
    if res == None:
        print("Não tem passagem volta")
        print("########## EXECUTANDO API PASSAGEM (VOLTA) ##########")
        dict_volta = ApiPassagem.get_passagem(session['data_volta'], session['passageiros'], session['dict_destino']['aero_code'], session['dict_origem']['aero_code']) #API PASSAGEM #É UMA LISTA
        lista_passagens = []
        for passagem in dict_volta:
            lista_passagens.append(Passagem.criaPassagem(passagem, session['dict_destino']['location_id'], session['dict_origem']['location_id'])) 
        Passagem.cadastraPassagens(lista_passagens) #ARMAZENA NO BANCO
    #TEM PASSAGEM VOLTA
    else:
        dict_volta = res

    dict_voos = {
        "ida": dict_ida,
        "volta": dict_volta,
        "origem": session['dict_origem'],
        "destino": session['dict_destino']
    }

    return render_template('Passagem.html', content = dict_voos)

@app.route("/hospedagem", methods=["POST"])
def get_hotel():
    session["voo_ida"] = request.form.get('voo_ida')
    session["voo_volta"] = request.form.get('voo_volta')

    data_ida = datetime.datetime.strptime(session["data_ida"], "%Y-%m-%d").date()
    data_volta = datetime.datetime.strptime(session["data_volta"], "%Y-%m-%d").date()
    session['noites'] = (data_volta - data_ida).days
    
    #NÃO TEM ORIGEM
    if session["tem_origem"] == False:
        print("Não tem ORIGEM, não há hospedagem para cidade")
        print("########## EXECUTANDO API HOTEL (ORIGEM) ##########")
        dict_hoteis = ApiHospedagem.get_hotels(session["dict_origem"]["location_id"], session["passageiros"], session["data_ida"], session['noites']) #API HOTEL #É UMA LISTA
        lista_hospedagens = []
        for hospedagem in dict_hoteis:
            lista_hospedagens.append(Hospedagem.criaHospedagem(hospedagem))
        Hospedagem.cadastraHospedagens(lista_hospedagens) #ARMAZENA NO BANCO
    
    #NÂO TEM DESTINO
    if session["tem_destino"] == False:
        print("\nNão tem DESTINO, não há hospedagem para a cidade")
        print("########## EXECUTANDO API HOTEL (DESTINO) ##########")
        dict_hoteis = ApiHospedagem.get_hotels(session["dict_destino"]["location_id"], session["passageiros"], session["data_ida"], session['noites']) #API HOTEL #É UMA LISTA
        lista_hospedagens = []
        for hospedagem in dict_hoteis:
            lista_hospedagens.append(Hospedagem.criaHospedagem(hospedagem))
        Hospedagem.cadastraHospedagens(lista_hospedagens) #ARMAZENA NO BANCO
    
    else:
        #CONSULTA HOSPEDAGEM - consultar e retornar hospedagem para o destino
        print("########## CONSULTA HOSPEDAGEM (DESTINO) ##########")
        res = Hospedagem.consultaHospedagem(session["dict_destino"]["location_id"])
        dict_hoteis = res
    
    return render_template('Hospedagem.html', content = dict_hoteis)

@app.route("/pacote", methods=["POST"])
def fechando_pacote():
    hotel = request.form.get('hotel')
    hotel = eval(hotel)
    ida = eval(session['voo_ida'])
    volta = eval(session['voo_volta'])

    #NÃO TEM ORIGEM
    if session["tem_origem"] == False:
        print("Não tem ORIGEM, não há atração para cidade")
        print("########## EXECUTANDO API ATRACAO (ORIGEM) ##########")
        dict_atracoes = ApiAtracao.get_atracao(session["dict_origem"]['location_id'])
        lista_atracoes = []
        for atracao in dict_atracoes:
            lista_atracoes.append(Atracao.criaAtracao(atracao))
        Atracao.cadastraAtracoes(lista_atracoes) #ARMAZENA NO BANCO

    #NÂO TEM DESTINO
    if session['tem_destino'] == False:
        print("\nNão tem DESTINO, não há atração para cidade")
        print("########## EXECUTANDO API ATRACAO (DESTINO) ##########")
        dict_atracoes = ApiAtracao.get_atracao(session["dict_destino"]['location_id'])
        lista_atracoes = []
        for atracao in dict_atracoes:
            lista_atracoes.append(Atracao.criaAtracao(atracao))
        Atracao.cadastraAtracoes(lista_atracoes) #ARMAZENA NO BANCO
    
    else:
        #CONSULTA ATRACAO - consultar e retornar atração para o destino
        print("########## CONSULTA ATRACAO (DESTINO) ##########")
        res = Atracao.consultaAtracao(session["dict_destino"]["location_id"])
        dict_atracoes = res
    
    #PACOTE TURISTICO
    print("\n########## FECHANDO PACOTE ##########")
    valor_pacote = round((float(ida['preco']) + float(volta['preco'])) * float(session['passageiros']) + float(hotel['preco'] * float(session['noites']))) #calcula valor pacote

    dict_pacote = {
        'hotel': hotel,
        'ida': ida,
        'volta': volta,
        'passageiros': session["passageiros"],
        'noites': session['noites'],
        'atracoes': dict_atracoes,
        'valor_pacote': valor_pacote,
        'origem': session["dict_origem"],
        'destino': session["dict_destino"]
    }
    
    passagem_id_ida = Passagem.passagemSelecionada(ida) #busca id da passagem de ida
    if passagem_id_ida != 'error':
        passagem_id_ida = passagem_id_ida[0][0]

    passagem_id_volta = Passagem.passagemSelecionada(volta) #busca id da passagem de volta
    if passagem_id_volta != 'error':
        passagem_id_volta = passagem_id_volta[0][0]

    hospedagem_id = Hospedagem.hospedagemSelecionada(hotel) #busca id da hospedagem
    if hospedagem_id != 'error':
        hospedagem_id = hospedagem_id[0][0]

        pacote = Pacote.criaPacote(passagem_id_ida, passagem_id_volta, hospedagem_id, valor_pacote, session['passageiros'])
        Pacote.cadastraPacote(pacote) #ARMAZENA NO BANCO

    return render_template('Pacote.html', content = dict_pacote)

if __name__ == "__main__":
    app.secret_key = 'key'
    app.run()