<h2 align="center">Iqoption trade bot baseed in SMA moving average </h2>

>Status: Completed ✔️ (Without interface)


>Language used: Python 🐍

>API used: https://github.com/Lu-Yi-Hsun/iqoptionapi <i>(credits to him)</i>


*A project of my own that performs purchases and sales at the broker IQOption, based on peaks formed by SMA moving averages*

## Requirements
Before we start, you will need some donwloads to run the project correctly in your machine. First, you need to install our interpreter [python](https://www.python.org/downloads/). Second, i recommend you use as IDLE [pycharm](https://www.jetbrains.com/pt-br/pycharm/download/) because was the IDLE that i have used to code the bot and saves you a lot of time while you coding.
You will need too some new libralies, and you can install it typing in yout terminal IDLE _pip intall libraryName_. 
* _pip install talib_
* _pip install numpy_
* _pip install schedule_

As i said before, i used [iqoptionapi](https://github.com/Lu-Yi-Hsun/iqoptionapi/) to project the bot. The API creator has two versions, a free version and a paid version. Lucky for us, we can do all of the functions without any problems using the free version. To install this version of the API, all you have to do is download it by clicking on _donwload zip_

![image](https://user-images.githubusercontent.com/85650237/137520470-c4b4b993-dee6-4ea2-84f0-8a001f86c8e3.png)

After that, you have to open the file you donwloaded and copy the folder inside the zip file and paste it into the bot's code file.
And of course, you need to create a [iqoption account](https://iq-option.com/lp/mobile-pwa/pt/?aff=1&afftrack=GAD_BR_PT_01_Brand_Web_TestDomenNewIQ_kwd-79547840234&gclid=Cj0KCQjwtrSLBhCLARIsACh6Rmg1M-SjX57UqAm63FcxglZLHWYFVQ6rng1p0RdRxzuh2dVF__jV8KQaAjGiEALw_wcB). The donwnload of iqoption app is optional.

## How the bot works
It's baseed on 5 period SMA moving average, where we are looking for tops and bottoms in M5 candles.
![image](https://user-images.githubusercontent.com/85650237/137859098-9368c02b-2df7-401c-abbd-0e9591bef108.png)

As you can see, we have many reference lines in a short period of time, and if we make a buy or sell on any of them we will lose a lot of money. So the secret is to filter the entries so that we only make a buy or sell when all filters are positive for us. That's the reason we have 7 filters in the bot.
* Trade only with 1 minute expiration time.
* Trade only when the current candle is less than 30 seconds long
* Trade only when payout the payout is equal to or above 70%.
* Trade only if we have at least one ask and bid lines.
* If no trade opportunities are found within 30 minutes, restart the analysis.
* With every victory restart the analysis.
* When the analysis is restarted, the same parity will not be parsed unless all parities currently available have already been parsed.

## Management
The bot uses a management baseed on soros, stopping with 1 loss or 2 gains in a row. The initial value of trade is 2% of your balance. If this value is less than $2, the initial value will be $2.10. In soros management, if we get a gain, the next trade will have the same value as the first + the profit of this same trade. Your trading value will be automatically updated every 30 days automatically.

## How add-on files work
To understand the code, we need to understand the two files that accompany the main code. The first is _userdata_, inside of it, we have 5 lines:

![image](https://user-images.githubusercontent.com/85650237/137864085-5ade0e87-7810-4da2-89cf-05dd275ee721.png)

>In the first one you need to write your iq option email.

>In the second one you need to write your iq option passord.

>In the third you need to write which type of account you want the bot to trade (real / demo).

>The fourth line talks about management, which is explained in the topic _how the bot works_.

The second file has only 2 lines.
 
![image](https://user-images.githubusercontent.com/85650237/137954831-382b8fd1-d78b-4d82-b29b-261c5157db48.png)

>The first one talks about your balance.

>Second one talks about the date the bot saved your balance.

## How the code works
* First, we declare the libraries and the API and open the txt file containing the user account information and read it. With this information, we can connect the IQOption account whith the API by the funcion _connect_ and define whether we are going to trade on a demo or real account by the function _change_balance_:
```python
from iqoptionapi.stable_api import IQ_Option
import logging, json, sys, time
from talib.abstract import *
import numpy as np
from datetime import datetime, date
import math

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
```

* After that, we declare the variables and check the date of the txt file to know if it needs to be updated to define our initial trade amount.We have also created two functions that will help us to check if the current candle is right for some trade.

```python
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

    return(saldo)
   
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
```
* Here we check the parity we will trade with. We have to check 3 things before and after checking which paritys are open by the function _get_all_open_time()_:
> If this parity has been analyzed before (unless all others have already been analyzed as well).

> If this parity has more than 70% payout.

> If we haven't reached our stop gain or stop loss.

```python
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
```

* Now is the time to configure SMA moving average. We did this through the _talib_ library which gives us all the moving average information of the last 200 candles.

```python
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
```
* The next step is to build the "heart" of the code, the reference lines. These lines follow a basic logic: we want tops and bottoms, right? So to get this information, we'll check all the latest micro bullish and bearish trends. In addition, we'll look at when this bullish or bearish trend was reversed.
That price during trend reversal is what we are looking for. These prices will be added in a tuple. You can also change some values ​​of this part of the code in order to get more "defined" tops and bottoms or with less difference in price. Basically, we repeat this part of the code 2 times,
one for the buy lines and one for the sell lines.
If we have 2 pips difference between one reference line and another, we exclude one of the two

```python
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
```
* This is where the code analyzes actual trading prices. The condition for starting the analysis is that we need at least one reference for selling and buying lines. If this condition is true, we start reading current prices and expect an ideal opportunity to trade, baseed on ours trade filters:
> Candle time of at least 30 seconds.
> Stop gain and loss not yet reached.
> Analysis time of maximum 30 minutes
* If parity is in otc and we find an ideal trade oportunity, we will wait until the next minute to actually trade.
``` python
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
                        return(taxas_s)

        def filtro_2():
            for taxas_r in res:
                for velas in vela:
                    if velas['max'] >= taxas_r and velas['min'] <= taxas_r:
                        return(taxas_r)

        candle = API.get_realtime_candles(par, 60)
        time.sleep(1)
        for candles in candle:
            preco_atual = candle[candles]['close']
            abertura_inicial = candle[candles]['open']


        if troca < 1:
            for venda in res:
                if (preco_atual >= venda and abertura_inicial < venda) or (preco_atual <= venda and abertura_inicial > venda) and filtro_2() != venda:
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
```





