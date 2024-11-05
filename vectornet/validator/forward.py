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
    
    miner_uid = get_random_uids(self, k=self.config.neuron.sample_size)
    
    validator_db_manager = ValidatorDBManager(miner_uid)
    
    category, articles, query = generate_create_request(
        article_size = 30,
    )
    pageids = [article['pageid'] for article in articles]
    
    response_create_request = await self.dendrite(
        axons = [self.metagraph.axons[miner_uid]],
        synapse = query,
        deserialize = True,
        timeout = 90,
    )
    
    bt.logging.info(f"Received responses: {response_create_request}")
    
    create_request_zero_score = evaluate_create_request(response_create_request)
    
    if create_request_zero_score:
        validator_db_manager.create_operation("CREATE", query.user_name, query.organization_name, query.namespace_name, category, pageids)
            
    category, articles, query = generate_update_request(
        article_zize = 30,
        miner_uid = miner_uid,
    )

    responses_update = await self.dendrite(
        axons = [self.metagraph.axons[miner_uid]],
        synapse = query,
        deserialize = True,
        timeout = 90,
    )
    
    bt.logging.info(f"Received responses: {responses_update}")
    
    update_request_zero_scores = evaluate_update_request(responses_update)
        
    if update_request_zero_scores:
        validator_db_manager.update_operation("UPDATE", query.user_id, query.organization_id, query.namespace_id, category, pageids)
        
    query = generate_delete_request(miner_uid)
    
    responses_delete = await self.dendrite(
        axons = [self.metagraph.axons[miner_uid]],
        synapse = query,
        deserialize = True,
        timeout = 20,
    )
    
    bt.logging.info(f"Received responses: {responses_delete}") 
    
    delete_request_zero_scores = evaluate_delete_request(query, responses_delete)
    
    if delete_request_zero_scores:
        validator_db_manager.delete_operation("DELETE", query.user_id, query.organization_id, query.namespace_id)
    
    query = generate_read_request()
    
    responses_read = await self.dendrite(
        axons = [self.metagraph.axons[uid] for uid in miner_uids],
        synapse = query,
        deserialize = True,
        timeout = 30,
    )
    
    bt.logging.info(f"Received responses: {responses_read}")
    
    read_scores = evaluate_delete_request(query, responses_read)
    
    miner_row_scores = create_zero_scores * update_zero_scores * delete_zero_scores * read_scores

    rewards = get_rewards(self, query=self.step, responses=responses)

    bt.logging.info(f"Scored responses: {rewards}")
    # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
    self.update_scores(rewards, miner_uids)
    time.sleep(5)