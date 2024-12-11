# Quickstart

## General

The `netuid` for `vectorstore` is `x` on mainnet, and `251` on testnet.

### Prepare Wallet

Generally, for both validator and miner, you need to prepare your wallet and make your key registered in the subnet.

If you are new to bittensor subnet, you are recommended to start by following

- [Bittensor Docs](https://docs.bittensor.com/subnets/register-validate-mine)

### Install VectoreStore

In the root folder of this repository, run the following command to install vectorstore:

```bash
git clone https://github.com/vector-pool/vector-store
cd vector-store
pip install -e .
```

### Install Dependencies

To enable validator auto update with github repo, you can install `pm2` or `jq`.

- Installing PM2

```bash
sudo apt update && sudo apt install jq && sudo apt install npm && sudo npm install pm2 -g && pm2 update
```

### Prepare env file

```bash
cp .env.template .env
```

Fill out the names and keys with yours. 
If you are a miner, You don't need to fill out the `wandb_api_key`.

### Installing PostgreSQL

Both the miner side and the validator side need to install PostgreSQL for storing datas. 

- Using Docker
You can refer to the [docker official guide](https://docs.docker.com/engine/install/) to install docker.

```bash
docker-compose -f scripts/postgres-docker-compose.yml up -d
```

- Alternavely You can install and launch the PostgreSQL manually if your machine does not support docker like RunPod. 
If you are going to install and run the PostgreSQL manually, you need to create super-role with password and save all these informations at .env file.

You can do that using following commands.
```bash
psql -U postgres
CREATE ROLE your_user_name WITH LOGIN SUPERUSER PASSWORD 'your_password';
\q
```

## Start the Miner

After setting up the environment and PostgreSQL, you can start the miner by running the following command:

- Running on mainnet.
```bash
pm2 start --name miner1 --interpreter python3 ./neurons/miner.py -- --subtensor.network finney --netuid x --wallet.name miner --wallet.hotkey default --logging.debug --blacklist.force_validator_permit --axon.port 8091 
```
If you want to save all the logs, You can just add these commandes.

```bash
--logging.record_log --logging.logging_dir logs/logs_miner
```

In here, `logs/logs_miner` is a directory path you are going to save the logs

- Running on testnet.

```bash
pm2 start --name miner1 --interpreter python3 ./neurons/miner.py -- --subtensor.network test --netuid 251 --wallet.name miner --wallet.hotkey default --logging.debug --blacklist.force_validator_permit --axon.port 8091 --logging.record_log --logging.logging_dir logs/logs_miner
```

The detailed commandline arguments for the `neurons/miner.py` can be obtained by `python neurons/miner.py --help`, and are as follows:

```bash
usage: miner.py [-h] [--no_prompt] [--wallet.name WALLET.NAME] [--wallet.hotkey WALLET.HOTKEY] [--wallet.path WALLET.PATH]
                [--subtensor.network SUBTENSOR.NETWORK] [--subtensor.chain_endpoint SUBTENSOR.CHAIN_ENDPOINT] [--subtensor._mock SUBTENSOR._MOCK]
                [--logging.debug] [--logging.trace] [--logging.record_log] [--logging.logging_dir LOGGING.LOGGING_DIR] [--axon.port AXON.PORT]
                [--axon.ip AXON.IP] [--axon.external_port AXON.EXTERNAL_PORT] [--axon.external_ip AXON.EXTERNAL_IP]
                [--axon.max_workers AXON.MAX_WORKERS] [--netuid NETUID] [--neuron.name NEURON.NAME] [--neuron.device NEURON.DEVICE]
                [--neuron.epoch_length NEURON.EPOCH_LENGTH] [--neuron.events_retention_size NEURON.EVENTS_RETENTION_SIZE] [--neuron.dont_save_events]
                [--neuron.disable_crawling] [--neuron.crawl_size NEURON.CRAWL_SIZE] [--neuron.search_recall_size NEURON.SEARCH_RECALL_SIZE]
                [--blacklist.force_validator_permit] [--blacklist.allow_non_registered] [--config CONFIG] [--strict] [--no_version_checking]

options:
  -h, --help            show this help message and exit
  --no_prompt           Set true to avoid prompting the user.
  --wallet.name WALLET.NAME
                        The name of the wallet to unlock for running bittensor (name mock is reserved for mocking this wallet)
  --wallet.hotkey WALLET.HOTKEY
                        The name of the wallet's hotkey.
  --wallet.path WALLET.PATH
                        The path to your bittensor wallets
  --subtensor.network SUBTENSOR.NETWORK
                        The subtensor network flag. The likely choices are: -- finney (main network) -- test (test network) -- archive (archive
                        network +300 blocks) -- local (local running network) If this option is set it overloads subtensor.chain_endpoint with an
                        entry point node from that network.
  --subtensor.chain_endpoint SUBTENSOR.CHAIN_ENDPOINT
                        The subtensor endpoint flag. If set, overrides the --network flag.
  --subtensor._mock SUBTENSOR._MOCK
                        If true, uses a mocked connection to the chain.
  --logging.debug       Turn on bittensor debugging information
  --logging.trace       Turn on bittensor trace level information
  --logging.record_log  Turns on logging to file.
  --logging.logging_dir LOGGING.LOGGING_DIR
                        Logging default root directory.
  --axon.port AXON.PORT
                        The local port this axon endpoint is bound to. i.e. 8091
  --axon.ip AXON.IP     The local ip this axon binds to. ie. [::]
  --axon.external_port AXON.EXTERNAL_PORT
                        The public port this axon broadcasts to the network. i.e. 8091
  --axon.external_ip AXON.EXTERNAL_IP
                        The external ip this axon broadcasts to the network to. ie. [::]
  --axon.max_workers AXON.MAX_WORKERS
                        The maximum number connection handler threads working simultaneously on this endpoint. The grpc server distributes new worker
                        threads to service requests up to this number.
  --netuid NETUID       Subnet netuid
  --neuron.name NEURON.NAME
                        Trials for this neuron go in neuron.root / (wallet_cold - wallet_hot) / neuron.name.
  --neuron.device NEURON.DEVICE
                        Device to run on.
  --neuron.epoch_length NEURON.EPOCH_LENGTH
                        The default epoch length (how often we set weights, measured in 12 second blocks).
  --neuron.events_retention_size NEURON.EVENTS_RETENTION_SIZE
                        Events retention size.
  --neuron.dont_save_events
                        If set, we dont save events to a log file.
  --neuron.disable_crawling
                        If set, we disable crawling when receiving a search request.
  --neuron.crawl_size NEURON.CRAWL_SIZE
                        The number of documents to crawl when receiving each query.
  --neuron.search_recall_size NEURON.SEARCH_RECALL_SIZE
                        The number of search results to retrieve for ranking.
  --blacklist.force_validator_permit
                        If set, we will force incoming requests to have a permit.
  --blacklist.allow_non_registered
                        If set, miners will accept queries from non registered entities. (Dangerous!)
  --config CONFIG       If set, defaults are overridden by passed file.
  --strict              If flagged, config will check that only exact arguments have been set.
  --no_version_checking
                        Set ``true`` to stop cli version checking.
```


## Start the Validator

### Obtain OpenAI API Key

To use the LLM ranking result evaluation, you need to obtain an API key from [OpenAI](https://platform.openai.com/). After obtaining the API key, you can write it down in the `.env` file.

```
OPENAI_API_KEY="sk-xxxxxx"
```

### Obtain WANDB API Key

Log in to [Weights & Biases](https://wandb.ai) and generate a key in your account settings.

Set the key `WANDB_API_KEY` in the `.env` file.

```
WANDB_API_KEY="your_wandb_api_key"
```

### Running Validator

- Running on mainnet.
```bash
pm2 start --name vali1 --interpreter python3 ./neurons/validator.py -- --subtensor.network finney --netuid x --wallet.name validator --wallet.hotkey default --logging.debug --blacklist.force_validator_permit --axon.port 8091 
```
If you want to save all the logs, You can just add these commandes.

```bash
--logging.record_log --logging.logging_dir logs/logs_vali
```

In here, `logs/logs_vali` is a directory path you are going to save the logs

- Running on testnet.

```bash
pm2 start --name vali1 --interpreter python3 ./neurons/validator.py -- --subtensor.network test --netuid 251 --wallet.name validator --wallet.hotkey default --logging.debug --blacklist.force_validator_permit --axon.port 8091 --logging.record_log --logging.logging_dir logs/logs_miner
```
The detailed commandline arguments for the `validator` can be obtained by `python neurons/validator.py --help`, and are as follows:

```bash
usage: validator.py [-h] [--no_prompt] [--wallet.name WALLET.NAME] [--wallet.hotkey WALLET.HOTKEY] [--wallet.path WALLET.PATH]
                    [--subtensor.network SUBTENSOR.NETWORK] [--subtensor.chain_endpoint SUBTENSOR.CHAIN_ENDPOINT] [--subtensor._mock SUBTENSOR._MOCK]
                    [--logging.debug] [--logging.trace] [--logging.record_log] [--logging.logging_dir LOGGING.LOGGING_DIR] [--axon.port AXON.PORT]
                    [--axon.ip AXON.IP] [--axon.external_port AXON.EXTERNAL_PORT] [--axon.external_ip AXON.EXTERNAL_IP]
                    [--axon.max_workers AXON.MAX_WORKERS] [--netuid NETUID] [--neuron.name NEURON.NAME] [--neuron.device NEURON.DEVICE]
                    [--neuron.epoch_length NEURON.EPOCH_LENGTH] [--neuron.events_retention_size NEURON.EVENTS_RETENTION_SIZE]
                    [--neuron.dont_save_events] [--neuron.num_concurrent_forwards NEURON.NUM_CONCURRENT_FORWARDS]
                    [--neuron.sample_size NEURON.SAMPLE_SIZE] [--neuron.search_request_interval NEURON.SEARCH_REQUEST_INTERVAL]
                    [--neuron.search_result_size NEURON.SEARCH_RESULT_SIZE] [--neuron.disable_set_weights]
                    [--neuron.moving_average_alpha NEURON.MOVING_AVERAGE_ALPHA] [--neuron.axon_off]
                    [--neuron.vpermit_tao_limit NEURON.VPERMIT_TAO_LIMIT] [--config CONFIG] [--strict] [--no_version_checking]

options:
  -h, --help            show this help message and exit
  --no_prompt           Set true to avoid prompting the user.
  --wallet.name WALLET.NAME
                        The name of the wallet to unlock for running bittensor (name mock is reserved for mocking this wallet)
  --wallet.hotkey WALLET.HOTKEY
                        The name of the wallet's hotkey.
  --wallet.path WALLET.PATH
                        The path to your bittensor wallets
  --subtensor.network SUBTENSOR.NETWORK
                        The subtensor network flag. The likely choices are: -- finney (main network) -- test (test network) -- archive (archive
                        network +300 blocks) -- local (local running network) If this option is set it overloads subtensor.chain_endpoint with an
                        entry point node from that network.
  --subtensor.chain_endpoint SUBTENSOR.CHAIN_ENDPOINT
                        The subtensor endpoint flag. If set, overrides the --network flag.
  --subtensor._mock SUBTENSOR._MOCK
                        If true, uses a mocked connection to the chain.
  --logging.debug       Turn on bittensor debugging information
  --logging.trace       Turn on bittensor trace level information
  --logging.record_log  Turns on logging to file.
  --logging.logging_dir LOGGING.LOGGING_DIR
                        Logging default root directory.
  --axon.port AXON.PORT
                        The local port this axon endpoint is bound to. i.e. 8091
  --axon.ip AXON.IP     The local ip this axon binds to. ie. [::]
  --axon.external_port AXON.EXTERNAL_PORT
                        The public port this axon broadcasts to the network. i.e. 8091
  --axon.external_ip AXON.EXTERNAL_IP
                        The external ip this axon broadcasts to the network to. ie. [::]
  --axon.max_workers AXON.MAX_WORKERS
                        The maximum number connection handler threads working simultaneously on this endpoint. The grpc server distributes new worker
                        threads to service requests up to this number.
  --netuid NETUID       Subnet netuid
  --neuron.name NEURON.NAME
                        Trials for this neuron go in neuron.root / (wallet_cold - wallet_hot) / neuron.name.
  --neuron.device NEURON.DEVICE
                        Device to run on.
  --neuron.epoch_length NEURON.EPOCH_LENGTH
                        The default epoch length (how often we set weights, measured in 12 second blocks).
  --neuron.events_retention_size NEURON.EVENTS_RETENTION_SIZE
                        Events retention size.
  --neuron.dont_save_events
                        If set, we dont save events to a log file.
  --neuron.num_concurrent_forwards NEURON.NUM_CONCURRENT_FORWARDS
                        The number of concurrent forwards running at any time.
  --neuron.sample_size NEURON.SAMPLE_SIZE
                        The number of miners to query in a single step.
  --neuron.search_request_interval NEURON.SEARCH_REQUEST_INTERVAL
                        The interval seconds between search requests.
  --neuron.search_result_size NEURON.SEARCH_RESULT_SIZE
                        The number of search results required for each miner to return.
  --neuron.disable_set_weights
                        Disables setting weights.
  --neuron.moving_average_alpha NEURON.MOVING_AVERAGE_ALPHA
                        Moving average alpha parameter, how much to add of the new observation.
  --neuron.axon_off, --axon_off
                        Set this flag to not attempt to serve an Axon.
  --neuron.vpermit_tao_limit NEURON.VPERMIT_TAO_LIMIT
                        The maximum number of TAO allowed to query a validator with a vpermit.
  --config CONFIG       If set, defaults are overridden by passed file.
  --strict              If flagged, config will check that only exact arguments have been set.
  --no_version_checking
                        Set ``true`` to stop cli version checking.
```



## Useful Commands

### Dropping PostgreSQL Database.
If you want to drop the database in PostgreSQL, you can use following commands.


1. Check Active Connections
Run the following query to see which sessions are connected to the database:

```bash
SELECT pid, usename, datname, application_name, client_addr 
FROM pg_stat_activity 
WHERE datname = '5';
```


2. Terminate Active Connections

```bash
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '5' AND pid <> pg_backend_pid();
```

3. Drop the Database
After terminating all connections, you can now drop the database:

```bash
DROP DATABASE <database_name>;
```