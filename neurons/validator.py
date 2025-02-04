import time

import bittensor as bt

from vectornet.base.validator import BaseValidatorNeuron

from vectornet.validator import forward

from vectornet.validator.wandb_manager import WandbManager

class Validator(BaseValidatorNeuron):

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()
        self.wandb_manager = WandbManager(validator=self)


    async def forward(self, miner_uid):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        return await forward(self, miner_uid)


if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info(f"Validator running... {time.time()}")
            time.sleep(20)
