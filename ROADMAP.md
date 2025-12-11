# ROADMAP

## Nov 2025

### Interface
* Find better names for `cron_calc.py` and `bot.py`
* ~~`bot.py` should allow for MARKET~~
~~* `bot.py` should send a new msg with top3 pairs~~ 
*  `cron_calc.py` and `bot.py` should be `manage.py` commands

### Docker and Build
* Migrate from Poetry to UV
* ~~Application source should be inside `{$PROJECT_PATH}/src`~~
* ~~Docker should `COPY` only the `{$PROJECT_PATH}/src` dir - NOT `./`~~
* ~~Allow developement to mount ./src into /src~~

### Bugs
* Filters don't work
* FIX: error checking context: can't stat '/home/lvido/workspace/lvido/zecontinha/data/db'
* ~~bot b3 -> dashboard.models.Quotes.DoesNotExist: Quotes matching query does not exist.~~
* Scrap data for `CARTEIRA_IBRX` and `BINANCE_FUTURES`
