# VectorStore Miner & Validator Setup Guide

This guide provides step-by-step instructions for setting up a miner and validator on the Bittensor subnet.

---

## General Information

- **NetUIDs**:
  - `vectorstore` NetUID on **mainnet**: `14`
  - `vectorstore` NetUID on **testnet**: `251`
  
- You must prepare your wallet and register your key in the subnet before running the miner or validator.

For beginners, refer to the [Bittensor Documentation](https://docs.bittensor.com) for a comprehensive introduction.

---

## Prerequisites

Ensure the following are installed on your system:

- **Python**: Version 3.10 or higher
- **pip**: Python package manager
- **virtualenv** (optional): For dependency isolation

---

## Installation Steps

### 1. Install PM2 (Process Manager)

PM2 is used to manage and monitor miner/validator processes. If PM2 is not installed, follow these steps:

```bash
sudo apt update
sudo apt install npm -y
sudo npm install pm2 -g
pm2 update
```

For more details, refer to the [PM2 Documentation](https://pm2.io/docs/runtime/guide/installation/).

---

### 2. Clone the Repository

Clone the project repository to your local machine:

```bash
git clone https://github.com/vector-pool/vector-store.git
cd vector-store
```

---

### 3. Set Up a Virtual Environment (Recommended)

Create and activate a virtual environment to isolate project dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install Dependencies

Install the project and its dependencies using `pip`:

```bash
pip install -e .
```

---

### 5. Configure the Environment File

Copy the `.env.template` file and update it with your details:

```bash
cp .env.template .env
```

Fill in the required fields, such as wallet names, keys, and API keys.

---

### 6. Install PostgreSQL

Both the miner and validator require PostgreSQL for data storage. You can install PostgreSQL using **Docker** or directly on your machine.

#### Option 1: Install PostgreSQL Using Docker

1. Install Docker:
   ```bash
   sudo apt update
   sudo apt install -y docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

   Verify the installation:
   ```bash
   docker --version
   ```

2. Install docker-compose:
   ```bash
   sudo apt install -y docker-compose
   sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | jq -r .tag_name)/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```
   verify installation
   ```bash
   docker-compose --version
   ```

3. Run PostgreSQL with Docker Compose:
   ```bash
   docker-compose -f scripts/postgres-docker-compose.yml up -d
   ```

#### Option 2: Install PostgreSQL Directly

If your machine does not support Docker (e.g., RunPod), install PostgreSQL manually

### 7. Create SuperUser

Both the miner and vaidator require set up superuser at PostgreSQL Database

1. Connect to PostgreSQL:
   ```bash
   sudo -u postgres psql
   ```

2. Create a superuser role:
   ```sql
   CREATE ROLE <postgres_user_name> WITH LOGIN SUPERUSER PASSWORD '<postgres_password>';
   \du  -- Verify the superuser is created
   \q   -- Exit PostgreSQL
   ```

3. Update the `.env` file with the `postgres_user_name` and `postgres_password`.
you must ensure that this `postgres_user_name` and `postgres_password` match with `.env` file

---

## Miner Setup

After setting up the environment and PostgreSQL, you can start the miner:

### Run Miner on Mainnet

```bash
pm2 start --name miner --interpreter python3 neurons/miner.py -- \
  --subtensor.network finney \
  --netuid 14 \
  --wallet.name <YOUR_WALLET_NAME> \
  --wallet.hotkey <YOUR_HOTKEY_NAME> \
  --logging.debug \
  --axon.port <PORT>
```

If you want to save logs, append the following options:

```bash
--logging.record_log --logging.logging_dir logs/logs_miner
```

In this case, `logs/logs_miner` is the directory where logs will be saved.

---

## Validator Setup

### 1. Obtain OpenAI API Key

To use the LLM ranking result evaluation, obtain an API key from [OpenAI](https://platform.openai.com/) and add it to the `.env` file:

```
OPENAI_API_KEY="sk-xxxxxx"
```

---

<!-- ### 2. Obtain WANDB API Key

Log in to [Weights & Biases](https://wandb.ai), generate an API key in your account settings, and add it to the `.env` file:

```
WANDB_API_KEY="your_wandb_api_key"
``` -->

---

### 2. Run Validator on Mainnet

- Ensure that the jq package is installed on your system by following these steps:

```bash
sudo apt-get update
sudo apt-get install jq
jq --version #verify
```

---

- Running validator

```bash
pm2 start run.sh --name vectornet_v_autoupdater -- \
  --subtensor.network finney \
  --netuid 14 \
  --wallet.name <YOUR_WALLET_NAME> \
  --wallet.hotkey <YOUR_HOTKEY_NAME> \
  --logging.debug \
  --axon.port <PORT> 
```

- To save logs, append the following options:

```bash
--logging.record_log --logging.logging_dir logs/logs_vali
```

In this case, `logs/logs_vali` is the directory where logs will be saved.

#### This command runs both the validator and the auto-updater.

---

## Useful Commands

### Dropping PostgreSQL Database

If you need to drop the database in PostgreSQL, follow these steps:

1. Connect to PostgreSQL:
   ```bash
   sudo -u postgres psql
   ```

2. Check active connections:
   ```sql
   SELECT pid, usename, datname, application_name, client_addr 
   FROM pg_stat_activity 
   WHERE datname = '<database_name>';
   ```

3. Terminate active connections:
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE datname = '<database_name>' AND pid <> pg_backend_pid();
   ```

4. Drop the database:
   ```sql
   DROP DATABASE <database_name>;
   ```

5. Drop all databases
   drop all databases running this script:
   ```bash
   python scripts/init_db.py
   ```

---

## Additional Resources

- [Bittensor Documentation](https://docs.bittensor.com)
- [PM2 Documentation](https://pm2.io/docs/runtime/guide/installation/)
- [Docker Official Guide](https://docs.docker.com/engine/install/)

---

## Troubleshooting

If you encounter issues during setup, ensure:

1. All dependencies are installed correctly.
2. Your `.env` file is properly configured with matching credentials.
3. PostgreSQL is running and accessible.

For further assistance, refer to the [Bittensor Community](https://bittensor.com/community).

---
