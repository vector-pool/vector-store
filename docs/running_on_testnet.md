python neurons/validator.py --subtensor.network test --netuid 140 --wallet.name mytest --wallet.hotkey validator1 --logging.debug
python neurons/miner.py --subtensor.network test --netuid 140 --wallet.name mytest --wallet.hotkey miner2 --logging.debug

btcli wallet regen_coldkey 
btcli wallet regen_hotkey


