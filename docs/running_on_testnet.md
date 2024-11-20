
# Running on testnet

Validators requires to the openai key.
For running validator, They have to generate query for embedding evaluation.

## PostgreSQL Installation.

* First, Have to install Postgresql using this commands

```
brew install postgresql@14
brew services start postgresql@14
psql postgres
CREATE ROLE your_user_name WITH LOGIN SUPERUSER PASSWORD 'your_password';
\du
```

* If you want to restart postgresql server, follow this commands

```
brew services restart postgresql@14
```

python neurons/validator.py --subtensor.network test --netuid 140 --wallet.name mytest --wallet.hotkey validator1 --logging.debug
python neurons/miner.py --subtensor.network test --netuid 140 --wallet.name mytest --wallet.hotkey miner2 --logging.debug

btcli wallet regen_coldkey 
btcli wallet regen_hotkey
btcli s metagraph --subnet.network test --netuid 140

