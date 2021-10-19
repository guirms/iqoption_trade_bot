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
The bot uses a management baseed on soros, stopping with 1 loss or 2 gains in a row. The initial value of trade is 2% of your balance. If this value is less than 2, the initial value will be 2.10. In soros management, if we get a gain, the next trade will have the same value as the first + the profit of this same trade.

## How the code works
To understand the code, we need to understand the two files that accompany the main code. The first is _userdata_, inside of it, we have 5 lines:

![image](https://user-images.githubusercontent.com/85650237/137864085-5ade0e87-7810-4da2-89cf-05dd275ee721.png)

>In the first one you need to write your iq option email.

>In the second one you need to write your iq option passord.

>In the third you need to write which type of account you want the bot to trade (real / demo).

>The fourth line talks about management, which is explained in the topic _how the bot works_.
 


First, we declare the libraries and the API and open the txt file containing the user account information and read it. With this information, we can connect the IQOption account whith the API by the funcion:
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





