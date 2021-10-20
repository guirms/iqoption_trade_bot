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

As you can see, we have many reference lines in a short period of time, and if we make a buy or sell on any of them we will lose a lot of money. So the secret is to filter the entries so that we only make a buy or sell when all filters are positive for us. That's the reason we have 3 filters in the bot.
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



