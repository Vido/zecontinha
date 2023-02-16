# Zé Continha

O Zé Continha é uma prova de conceito sobre PairTrading (a.k.a Long and Short), baseado em Cointegração.

* Nenhuma recomendação de compra ou venda é feita neste sistema.
* Não garantimos que os dados apresentados estão corretos.
* Não me responsabilizo pelo mal uso das informações.

http://zecontinha.herokuapp.com/b3/pairs_ranking

## Instruções para rodar em Desenvolvimento:
** Requisito ** : Python 3.6
** Requisito ** : Postgres 10.12, 11.9 ou melhor

Recomendamos criar um database no Postgres, com as configurações típicas para o
Django

Recomendamos usar o pyenv para obter a versão correta do Python,
e criar um virtualenv a partir do pyenv.

Recomendamos exportar as seguintes variaveis (usando um arquivo .env e chamando ele no docker-compose.yml):
```
# Requerido para o Django
SECRET_KEY=xxx
DATABASE_URL=postgres://user:password@host:5432/dbname


# Requerido para a parte de Crypto
BINANCE_APIKEY=xxx
BINANCE_SECRETKEY=xxx

# Requerido para o Bot de Telegram
TELEGRAM_API_KEY=xxx
```

Operação padrão Django normal: `manage.py`

`python cron_calc.py` é o comando para gerar os dados do sistema
