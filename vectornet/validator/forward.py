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
from vectornet.validator.reward import get_rewards
from vectornet.utils.uids import get_random_uids
from vectornet.database_manage.validator_db_manager import ValidatorDBManager
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
    evaluate_update_request,
    evaluate_delete_request,
    evaluate_read_request,
)
from vectornet.database_manage.validator_db_manager import ValidatorDBManager, CountManager
from vectornet.utils.weight_control import weight_controller

async def forward(self, miner_uid):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    
    # miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
    # miner_uid = miner_uids[0] # the default sample_size is one
    
    create_request_zero_score, update_request_zero_score, delete_request_zero_score, read_score = 0, 0, 0, 0
    
    
    RED = "\033[31m"
    GREEN = "\033[32m"
    RESET = "\033[0m"

    # Print colored text
    print(RED + "This text is red!" + RESET)
    print(GREEN + "This text is green!" + RESET)
    
    
    miner_uid = int(miner_uid)
    # print(miner_uid)
    # print(type(miner_uid))
    validator_db_manager = ValidatorDBManager(miner_uid)
    count_manager = CountManager()
    
    count_manager.add_count(miner_uid)
    cur_count_synapse = count_manager.read_count(miner_uid)
    
    category, articles, create_request = await generate_create_request(
        validator_db_manager = validator_db_manager,
        article_size = 1,
    )
    print(create_request)
    pageids = [article['pageid'] for article in articles]
    
    print(RED + "\n\n Sent Create_request\n\n" + RESET)
    
    responses = await self.dendrite(
        axons = [self.metagraph.axons[miner_uid]],
        synapse = create_request,
        deserialize = True,
        timeout = 60,
    )
    
    if len(responses) != 1:
        bt.logging.info("Something went wrong, number of CreateSynaspe responses bigger than one.")
    response_create_request = responses[0]
    
    bt.logging.info(f"Received responses : {response_create_request} from {miner_uid}")
    
    create_request_zero_score = evaluate_create_request(response_create_request, validator_db_manager, create_request, pageids)
    pageids_info = []
    for pageid, vector_id in zip(pageids, response_create_request[3]):
        pageids_info.append({pageid:vector_id})
        
    if create_request_zero_score:
        validator_db_manager.create_operation(
            "CREATE",
            create_request.user_name,
            create_request.organization_name,
            create_request.namespace_name,
            response_create_request[0],
            response_create_request[1],
            response_create_request[2],
            category,
            pageids_info,
        )
    
    for i in range(0, 3):
        category, articles, update_request = await generate_update_request(
            article_size = 3,
            validator_db_manager = validator_db_manager,
        )
        pageids = [article['pageid'] for article in articles]
        if update_request is not None:
            print(RED + "\n\n Sent update_request\n\n" + RESET)
            response_update_request = await self.dendrite(
                axons = [self.metagraph.axons[miner_uid]],
                synapse = update_request,
                deserialize = True,
                timeout = 10,
            )
            
            bt.logging.info(f"Received Update responses : {response_update_request} from {miner_uid}")
            update_request_zero_score = evaluate_update_request(update_request, response_update_request)
            
            pageid_info = {}
            for pageid, vector_id in zip(pageids, response_create_request[3]):
                pageid_info[pageid] = vector_id
            
            if update_request_zero_score:
                validator_db_manager.update_operation(
                    "UPDATE",
                    update_request.perform,
                    update_request.user_id,
                    update_request.organization_id,
                    update_request.namespace_id,
                    category,
                    pageids_info,
                )
    
    random_num = random.random()
    if random_num < 0.3:
        delete_request = await generate_delete_request(validator_db_manager)
        
        if delete_request is not None:
            response_delete_request = await self.dendrite(
                axons = [self.metagraph.axons[miner_uid]],
                synapse = delete_request,
                deserialize = True,
                timeout = 20,
            )
            
            bt.logging.info(f"Received responses: {response_delete_request}") 
            
            delete_request_zero_score = evaluate_delete_request(delete_request, response_delete_request)
            
            if delete_request_zero_score:
                validator_db_manager.delete_operation("DELETE", delete_request.user_id, delete_request.organization_id, delete_request.namespace_id)
        
    read_request, content = await generate_read_request(validator_db_manager)
    
    if read_request is not None:
        
        response_read = await self.dendrite(
            axons = [self.metagraph.axons[miner_uid]],
            synapse = read_request,
            deserialize = True,
            timeout = 30,
        )
        
        bt.logging.info(f"Received responses: {response_read}")
        
        read_score = evaluate_read_request(read_request, response_read, content)
    
    weight = weight_controller(cur_count_synapse)
    
    if weight is None:
        raise Exception("error occurs in weight mapping in evaluation")
    
    rewards = get_rewards(
        self,
        create_request_zero_score,
        update_request_zero_score,
        delete_request_zero_score,
        read_score,
        weight,
    )

    bt.logging.info(f"Scored responses: {rewards}")
    # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
    self.update_scores(rewards, [miner_uid])
    time.sleep(20)
    