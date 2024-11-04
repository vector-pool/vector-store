# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import time
import bittensor as bt
import random


from vectornet.protocol import (
    CreateSynapse,
    ReadSynapse,
    UpdateSynapse,
    DeleteSynapse,    
)
from vectornet.validator.reward import get_rewards
from vectornet.utils.uids import get_random_uids
from vectornet.database_manage.validator_db_manager import ValidatorDBManager
from vectornet.miner_group.check_new_miners import check_miner_status
from vectornet.miner_group.miner_group import make_miner_group
from vectornet.wiki_integraion.wiki_scraper import wikipedia_scraper
from vectornet.tasks.generate_task import (
    generate_create_request,
    generate_read_request,
    generate_update_request, 
    generate_delete_request,
)
from vectornet.evaludation.evaluate import (
    evaluate_create_request,
)
from vectornet.database_manage.validator_db_manager import ValidatorDBManager



async def forward(self):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    # TODO(developer): Define how the validator selects a miner to query, how often, etc.
    # get_random_uids is an example method, but you can replace it with your own.
    new_miner_uids, miner_ages = check_miner_status()
    very_young_miers, young_miners, mature_miners, old_miners, very_old_miners = make_miner_group(miner_ages)
    
    # init_new_miner_uids()
    
    miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
    
    validator_db_managers = {} #this may occurs the error
    
    for miner_uid in miner_uids:
        validator_db_managers[miner_uid] = ValidatorDBManager(miner_uid)
    
    category, articles, query = generate_create_request(
        article_size = 30,
    )
    pageids = [article['pageid'] for article in articles]
    for miner_uid, manager in validator_db_managers.items():
        # Call the create_operation method on each manager
        manager.create_operation("CREATE", query.user_name, query.organization_name, query.namespace_name, category, pageids)
    
    responses_create = await self.dendrite(
        axons = [self.metagraph.axons[uid] for uid in miner_uids],
        synapse = query,
        deserialize = True,
        timeout = 90,
    )
    
    create_scores = evaluate_create_request(responses_create)
    
    query = generate_update_request(
        article_zize = 30,
        miner_uids = miner_uids,
    )

    for miner_uid, manager in validator_db_managers.items():
        manager.update_operation("UPDATE", query.user_name, query.organization_name, query.namespace_name, pageids)

    responses_update = evaluate_update_request(responses_update)
    
    query = generate_delete_request()

    # The dendrite client queries the network.
    responses = await self.dendrite(
        # Send the query to selected miner axons in the network.
        axons=[self.metagraph.axons[uid] for uid in miner_uids],
        # Construct a dummy query. This simply contains a single integer.
        synapse=Dummy(dummy_input=self.step),
        # All responses have the deserialize function called on them before returning.
        # You are encouraged to define your own deserialization function.
        deserialize=True,
    )

    # Log the results for monitoring purposes.
    bt.logging.info(f"Received responses: {responses}")

    # TODO(developer): Define how the validator scores responses.
    # Adjust the scores based on responses from miners.
    rewards = get_rewards(self, query=self.step, responses=responses)

    bt.logging.info(f"Scored responses: {rewards}")
    # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
    self.update_scores(rewards, miner_uids)
    time.sleep(5)