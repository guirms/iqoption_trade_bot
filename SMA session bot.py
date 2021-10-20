from iqoptionapi.stable_api import IQ_Option
import logging, json, sys, time
from talib.abstract import *
import numpy as np
from datetime import datetime, date
import math
import schedule


def parar():
    print('O robô não está operando agora! \n(Horários de operação: 02:00 às 04:00, 09:30 ás 12:00, 18:20 ás 19:30')

def rodar():
    arq = open('userdata.txt')
    linhas = arq.readlines()
    email = (linhas[0].replace('E-mail:', '').strip())
    senha = (linhas[1].replace('Senha:', '').strip())
    conta = (linhas[2].replace('Conta:', '').strip().upper())

    API = IQ_Option(email, senha)
    API.connect()

    if conta == 'DEMO':
        API.change_balance('PRACTICE')

    elif conta == 'REAL':
        API.change_balance('REAL')

    while not API.check_connect():
        time.sleep(1)
    print('Conectado com sucesso')

    arquivo1 = 'managementdata.txt'
    horario_inicial = datetime.now().strftime('%H: %M :%S')
    win_lista = []
    loss_lista = []
    remover = []
    periodo = 5
    tempo_segundos = 300
    entradas = 0
    contador_par = 0
    payout = 0
    loss_seguidos = 0
    parar = 0
    res_valores = 0
    sl = 1
    sg = 2
    gerenciamento = 1
    print('Gerenciamento 2x1')

    def verificar_saldo():
        saldo_atual = str(API.get_balance())

        def linha_txt(linha_especifica, texto):
            file = open(arquivo1, 'r')
            lines = file.readlines()
            file.close()

            lines.insert(linha_especifica, texto + "\n")
            file = open(arquivo1, 'w')
            file.writelines(lines)
            file.close()

        def excluir_linha(posicao):
            file = open(arquivo1, 'r')
            data = file.readlines()
            data[posicao] = '\n'
            file = open(arquivo1, 'w')
            file.writelines(data)

        file = open(arquivo1, 'r')
        lines = file.readlines()
        if not '-' in lines[0]:
            linha_txt(0, str(date.today()))
            linha_txt(1, saldo_atual)
            saldo = float(saldo_atual)
            excluir_linha(2)
            excluir_linha(3)

        else:
            d_atual = str(date.today())
            d1 = datetime.strptime(str(lines[0]).strip(), '%Y-%m-%d')
            d2 = datetime.strptime(str(d_atual), '%Y-%m-%d')
            quantidade_dias = abs((d2 - d1).days)
            if quantidade_dias >= 10:
                linha_txt(0, str(date.today()))
                linha_txt(1, saldo_atual)
                saldo = float(saldo_atual)
                excluir_linha(2)
                excluir_linha(3)

            else:
                saldo = float(lines[1])

        return (saldo)

    valor = verificar_saldo() * 0.02 / sl

    saldo_banca = API.get_balance()
    if valor <= 2:
        valor = 2.10
    valor_inicial = valor
    print(f'Banca: {verificar_saldo()} ; Valor de entrada: {round(valor, 2)}')

    def esperar(delay=0):
        time.sleep(60 - int(datetime.now().strftime('%S')) + delay)

    def entrada():
        sec_atual = int(datetime.now().strftime('%S'))
        while sec_atual < 30:
            return True

    while len(win_lista) < sg and len(loss_lista) < sl and parar != 1:
        print('Iniciando análise\n')
        par_aberto = API.get_all_open_time()
        qtd_pares = 0
        for aberto in par_aberto['digital']:
            time.sleep(1)
            if par_aberto['digital'][aberto]['open'] == True:
                qtd_pares += 1
        troca = 0
        temporizador = 0
        payout_ind = 0
        if len(remover) >= qtd_pares:
            print('Adicionando novamente todos os pares para análise')
            remover = []
        pares_lista = []

        for paridade in par_aberto['digital']:
            time.sleep(1)
            if par_aberto['digital'][paridade]['open'] == True and not paridade in remover:
                print(f'Obtendo informações básicas do par {paridade}')
                contador_par += 1
                pares_lista.append(paridade)

        for par in pares_lista:
            if API.get_all_open_time()['digital'][par]['open']:
                print(f'\nAnalisando o par {par}')
                remover.append(par)
                payout = API.get_digital_payout(par)
                print(f'Payout: {payout}%')
                time.sleep(1)
            else:
                print(f'Não foi possível identificar o payout do par {par}. Reiniciando!')
                payout_ind = 1

            if not payout >= 70 or payout_ind == 1:
                break

            API.start_candles_stream(par, tempo_segundos, 200)
            velas = API.get_realtime_candles(par, tempo_segundos)
            valores = {'open': np.array([]), 'high': np.array([]), 'low': np.array([]), 'close': np.array([]),
                       'volume': np.array([])}

            for x in velas:
                valores['open'] = np.append(valores['open'], velas[x]['open'])
                valores['high'] = np.append(valores['open'], velas[x]['max'])
                valores['low'] = np.append(valores['open'], velas[x]['min'])
                valores['close'] = np.append(valores['open'], velas[x]['close'])
                valores['volume'] = np.append(valores['open'], velas[x]['volume'])

            calculo_sma = SMA(valores, timeperiod=periodo)

            API.start_candles_stream(par, tempo_segundos, 1)
            vela = API.get_realtime_candles(par, tempo_segundos)
            for velas in vela:
                preco_atual = vela[velas]['close']

            count = 0
            xy = 0
            taxa = []
            sup = []
            res = []
            while xy <= 10:
                printar = 0
                xy += 1
                if xy == len(calculo_sma):
                    xy = len(calculo_sma) - 1
                else:
                    for x in range(20 * (xy - 1), 20 * xy):
                        xx = x - 1
                        try:
                            if not math.isnan(calculo_sma[x]):
                                count += 1
                                if count >= 15:
                                    count = 0
                                    break
                                else:
                                    while calculo_sma[x] > calculo_sma[x + 1]:
                                        if calculo_sma[x + 8] - calculo_sma[x] >= 0.00003 and printar == 0:
                                            menor_t = 999999
                                            for min in range(x, x + 6):
                                                if calculo_sma[min] < menor_t:
                                                    menor_t = calculo_sma[min]
                                                    posicao = min

                                            if calculo_sma[posicao + 4] - menor_t >= 0.00002:
                                                taxa.append(round(menor_t, 5))
                                                printar = 1

                                        elif calculo_sma[x + 3] - calculo_sma[x] >= 0.00003 and printar == 0:
                                            menor_t = 999999
                                            for min in range(x, x + 6):
                                                if calculo_sma[min] < menor_t:
                                                    menor_t = calculo_sma[min]
                                                    posicao = min

                                            if calculo_sma[posicao + 3] - menor_t >= 0.00002:
                                                taxa.append(round(menor_t, 5))
                                                printar = 1
                                        break

                        except:
                            pass

            for taxas in range(len(taxa)):
                if preco_atual - taxa[taxas] >= 0.00002:
                    sup.append(taxa[taxas])

                elif taxa[taxas] - preco_atual >= 0.00002:
                    res.append(taxa[taxas])

            count = 0
            xy = 0
            taxa_m = []
            while xy <= 10:
                printar = 0
                xy += 1
                if xy == len(calculo_sma):
                    xy = len(calculo_sma) - 1
                else:
                    for x in range(20 * (xy - 1), 20 * xy):
                        xx = x - 1
                        try:
                            if not math.isnan(calculo_sma[x]):
                                count += 1
                                if count >= 15:
                                    count = 0
                                    break
                                else:
                                    while calculo_sma[x] < calculo_sma[x + 1]:
                                        if calculo_sma[x] - calculo_sma[x + 8] >= 0.00003 and printar == 0:
                                            maior_t = 0
                                            for max in range(x, x + 6):
                                                if maior_t < calculo_sma[max]:
                                                    maior_t = calculo_sma[max]
                                                    posicao = max

                                            if maior_t - calculo_sma[posicao + 2] >= 0.00002:
                                                taxa_m.append(round(maior_t, 5))
                                                printar = 1

                                        elif calculo_sma[x] - calculo_sma[x + 4] >= 0.00003 and printar == 0:
                                            maior_t = 0
                                            for max in range(x, x + 6):
                                                if maior_t < calculo_sma[max]:
                                                    maior_t = calculo_sma[max]
                                                    posicao = max

                                            if maior_t - calculo_sma[posicao + 3] >= 0.00002:
                                                taxa_m.append(round(maior_t, 5))
                                                printar = 1
                                        break
                        except:
                            pass

            for taxass in range(len(taxa_m)):
                if preco_atual - taxa_m[taxass] >= 0.00002:
                    sup.append(taxa_m[taxass])

                elif taxa_m[taxass] - preco_atual >= 0.00002:
                    res.append(taxa_m[taxass])

            if len(res) >= 1 and len(sup) >= 1:
                menor_r = 9999
                menor_s = 0
                for menorrr in res:
                    if menorrr < menor_r:
                        menor_r = menorrr
                for menorrrr in sup:
                    if menorrrr > menor_s:
                        menor_s = menorrrr

                print(f'Suporte: {menor_s} ; Resistência: {menor_r}')
                print(f'\nPar escolhido: {par}')

                print('Resistências:')
                for resss in res:
                    print(round(resss, 5))
                print('\nSuportes:')
                for suppp in sup:
                    print(round(suppp, 5))

                print('-' * 20, '\nAguardando oportunidade ideal de entrada:')
                hora_agora = datetime.now().strftime('%H: %M: %S')
                print(f'Horário de início: {hora_agora}')
                API.start_candles_stream(par, 60, 1)
                while temporizador <= 1650 and troca < 1 and \
                        (len(win_lista) < sg and len(loss_lista) < sl):
                    temporizador += 1
                    vela = API.get_candles(par, 60, 3, time.time())

                    def filtro_1():
                        for taxas_s in sup:
                            for velas in vela:
                                if velas['max'] >= taxas_s and velas['min'] <= taxas_s:
                                    return (taxas_s)

                    def filtro_2():
                        for taxas_r in res:
                            for velas in vela:
                                if velas['max'] >= taxas_r and velas['min'] <= taxas_r:
                                    return (taxas_r)

                    candle = API.get_realtime_candles(par, 60)
                    time.sleep(1)
                    for candles in candle:
                        preco_atual = candle[candles]['close']
                        abertura_inicial = candle[candles]['open']

                    if troca < 1:
                        for venda in res:
                            if (preco_atual >= venda and abertura_inicial < venda) or (
                                    preco_atual <= venda and abertura_inicial > venda) and filtro_2() != venda:
                                horario = datetime.now().strftime('%H: %M: %S')
                                print(f'Venda na próxima vela! horário atual: {horario}')
                                if 'OTC' in par:
                                    esperar()
                                preco_venda = venda
                                res.remove(venda)
                                statuss, id = API.buy_digital_spot_v2(par, valor, 'put', 1)
                                horario = datetime.now().strftime('%H: %M: %S')
                                if statuss:
                                    print(
                                        f'Venda em em {par}; Taxa: {round(preco_venda, 5)}; Horário: {horario}; Valor: {round(valor, 2)}; Preço atual: {round(preco_atual, 5)}')
                                    entradas += 1
                                    esperar(3)

                                status, historico = API.get_position_history_v2('digital-option', 1, 0, 0, 0)
                                for x in historico['positions']:
                                    resultado = float(x['close_profit'])

                                if resultado > 0:
                                    print('Win')
                                    win_lista.append(1)
                                    loss_seguidos = 0
                                    res_valores += resultado - valor
                                    valor = valor + (valor * int(payout) / 100)
                                    troca = 1

                                else:
                                    print('Loss')
                                    loss_lista.append(1)
                                    loss_seguidos += 1
                                    res_valores -= valor
                                    troca += 0.5
                                    valor = valor_inicial
                                break

                        for compra in sup:
                            if (((preco_atual <= compra and abertura_inicial > compra) or
                                 (preco_atual >= compra and abertura_inicial < compra)) and troca < 1
                                    and len(win_lista) < sg and len(loss_lista) < sl and filtro_1() != compra):
                                if 'OTC' in par:
                                    esperar()
                                horario = datetime.now().strftime('%H: %M: %S')
                                print(f'Compra na próxima vela! horário atual: {horario}')
                                esperar()
                                preco_compra = compra
                                sup.remove(compra)
                                statuss, id = API.buy_digital_spot_v2(par, valor, 'call', 1)
                                horario = datetime.now().strftime('%H: %M: %S')
                                if statuss:
                                    print(
                                        f'Compra em em {par}; Taxa: {round(preco_compra, 5)}; Horário: {horario}; Valor: {round(valor, 2)}; Preço atual: {round(preco_atual, 5)}')
                                    entradas += 1
                                    esperar(3)

                                status, historico = API.get_position_history_v2('digital-option', 1, 0, 0, 0)
                                for x in historico['positions']:
                                    resultado = float(x['close_profit'])

                                if resultado > 0:
                                    print('Win')
                                    win_lista.append(1)
                                    loss_seguidos = 0
                                    res_valores += resultado - valor
                                    if not gerenciamento == '3':
                                        valor = valor + (valor * int(payout) / 100)
                                    troca = 1

                                else:
                                    print('Loss')
                                    loss_lista.append(1)
                                    loss_seguidos += 1
                                    res_valores -= valor
                                    troca += 0.5
                                    if not gerenciamento == '3':
                                        valor = valor_inicial
                                break

            if troca >= 0.5 or temporizador >= 1650:
                break

            else:
                print(f'Par {par} não ideal para análise, continuando!\n')
                break

    horario_final = datetime.now().strftime('%H: %M: %S')
    print(f'Horário de início do robô: {horario_inicial} ; Horário final do robô: {horario_final}')
    print(f'Total de win: {len(win_lista)}')
    print(f'Total de loss: {len(loss_lista)}')
    print('Resultado: ', end='')
    if res_valores >= 0:
        print(f'Lucro de {round(res_valores, 2)}')
    else:
        print(f'Prejuízo de {abs(round(res_valores, 2))}')


schedule.every().day.at("02:00").do(rodar)
schedule.every().day.at("04:00").do(parar)
schedule.every().day.at("09:30").do(rodar)
schedule.every().day.at("12:00").do(parar)
schedule.every().day.at("18:20").do(rodar)
schedule.every().day.at("19:30").do(parar)


while True:
    schedule.run_pending()
    time.sleep(1)


















