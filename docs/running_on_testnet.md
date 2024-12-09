
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







python neurons/validator.py --subtensor.network test --netuid 251 --wallet.name net251 --wallet.hotkey miner55 --logging.debug --axon.port 51711
python neurons/miner.py --subtensor.network test --netuid 251 --wallet.name net251 --wallet.hotkey validator55 --logging.debug --axon.port 51711




btcli wallet regen_coldkey 
btcli wallet regen_hotkey
btcli s metagraph --subnet.network test --netuid 140

sudo systemctl start postgresql
sudo -u postgres psql
CREATE ROLE your_username WITH LOGIN SUPERUSER PASSWORD 'your_password';
\q