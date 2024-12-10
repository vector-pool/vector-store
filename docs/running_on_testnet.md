
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







python neurons/validator.py --subtensor.network test --netuid 251 --wallet.name net251 --wallet.hotkey miner55 --logging.debug --axon.port 51711 --logging.record_log --logging.logging_dir logs
python neurons/miner.py --subtensor.network test --netuid 251 --wallet.name net251 --wallet.hotkey validator55 --logging.debug --axon.port 51711 --logging.record_log --logging.logging_dir logs



sudo apt update && sudo apt install jq && sudo apt install npm && sudo npm install pm2 -g && pm2 update


pm2 start --name net251-validator1 --interpreter python3 ./neurons/validator.py -- --subtensor.network test --netuid 251 --wallet.name net251 --wallet.hotkey miner55 --logging.debug --axon.port 51711 --logging.logging_dir logs

pm2 start --name net251-miner1 --interpreter python3 ./neurons/miner.py -- --subtensor.network test --netuid 251 --wallet.name net251 --wallet.hotkey validator55 --logging.debug --axon.port 51711 --logging.logging_dir logs


btcli wallet regen_coldkey 
btcli wallet regen_hotkey
btcli s metagraph --subnet.network test --netuid 140

sudo systemctl start postgresql
sudo -u postgres psql
CREATE ROLE your_username WITH LOGIN SUPERUSER PASSWORD 'your_password';
\q










1. Check Active Connections
Run the following query to see which sessions are connected to the database:

sql
Copy code


SELECT pid, usename, datname, application_name, client_addr 
FROM pg_stat_activity 
WHERE datname = '5';






2. Terminate Active Connections
Terminate a Specific Connection
If there are only a few connections, you can terminate them individually by using their pid (process ID):

sql
Copy code
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '5';
Terminate All Connections to the Database
If you want to terminate all connections at once:

sql
Copy code



SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '5' AND pid <> pg_backend_pid();
DROP DATABASE "5";


pid <> pg_backend_pid() ensures that your current session is not terminated.



3. Drop the Database
After terminating all connections, you can now drop the database:

sql
Copy code


DROP DATABASE "5";










pm2 log 0 --lines 5000 >> logging_vali.txt