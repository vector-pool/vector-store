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
from datetime import datetime
import os
from vectornet.validator.reward import get_rewards
from vectornet.utils.uids import get_random_uids
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
from vectornet.utils.size_utils import text_length_to_storage_size
from .dashboard.model import Operation, MinerData
from .dashboard.dash_integration import send_data_to_dashboard
from dotenv import load_dotenv

load_dotenv()

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

async def forward(self, miner_uid):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    try:
        # miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
        # miner_uid = miner_uids[0] # the default sample_size is one
        
        bt.logging.info(GREEN + f"Starting Forward for miner uid : {miner_uid}" + RESET)
        
        miner_uid = int(miner_uid)
        validator_db_manager = ValidatorDBManager(miner_uid)
        count_manager = CountManager()
        

        operations = []
        
        create_request_zero_score, create_op = await forward_create_request(self, validator_db_manager, miner_uid)
        
        if create_op is not None:
            operations.append(create_op)
        time.sleep(10)
        
        update_request_zero_scores, update_ops = await forward_update_request(self, validator_db_manager, miner_uid)
        operations.extend(update_ops)
        time.sleep(20)
        
        delete_request_zero_score, delete_op = await forward_delete_request(self, validator_db_manager, miner_uid)
        
        if delete_op is not None:
            operations.append(delete_op)
        time.sleep(10)
        
        read_score, read_op = await forward_read_request(self, validator_db_manager, miner_uid)
            
        if read_op is not None:
            operations.append(read_op)
        
        total_storage_size = validator_db_manager.get_total_storage_size()
        
        bt.logging.debug("Passed all these 4 synapses successfully.")
        
        count_manager.add_count(miner_uid)
        cur_count_synapse = count_manager.read_count(miner_uid)
        
        weight = weight_controller(cur_count_synapse)
        
        bt.logging.info(f"current total number of synapse cycle for uid: {miner_uid} is {cur_count_synapse}.")
        
        if weight is None:
            raise Exception("error occurs in weight mapping in evaluation")

        bt.logging.info(f"{GREEN}Evaluated scores: Create: {create_request_zero_score}, Update: {update_request_zero_scores}, Delete: {delete_request_zero_score}, Read: {read_score}{RESET}")
        
        rewards = await get_rewards(
            create_request_zero_score,
            update_request_zero_scores,
            delete_request_zero_score,
            read_score,
            weight,
        )
        
        owner_hotkey = os.getenv("OWNER_HOTKEY")
        if len(operations) > 0 and owner_hotkey is not None:
            miner_data = MinerData(
                miner_uid=miner_uid,
                total_storage_size=total_storage_size,
                operations=operations,
                request_cycle_score=rewards,
                weight=weight,
                passed_request_count=cur_count_synapse,
            ) 
            
            print("===================== Miner Data Dubug =====================")
            print(miner_data.to_dict())
            
            await send_data_to_dashboard(miner_data, self.wallet.hotkey, owner_hotkey)

        bt.logging.info(f"Scored responses: {rewards}")
        self.update_scores(rewards, [miner_uid])
        time.sleep(40)    
    except Exception as e:
        bt.logging.error(f"Error occurs during forward: {e}")        

async def forward_create_request(self, validator_db_manager, miner_uid):
    
    category, articles, create_request, total_len = await generate_create_request(
        validator_db_manager = validator_db_manager,
        article_size = self.config.neuron.task_size,
        min_len = self.config.neuron.min_len,
        max_len = self.config.neuron.max_len,        
    )
    create_op = None
    create_request_zero_score = 0
    if create_request is not None:
        pageids = [article['pageid'] for article in articles]
        
        if total_len < self.config.neuron.task_size * self.config.neuron.min_len:
            bt.logging.error(f"There is an issue to generating task, because the total_len({total_len}) is smaller than task_size * min_len.")
     
        bt.logging.info(f"{RED}Sent Create request{RESET}")
        
        responses = await self.dendrite(
            axons = [self.metagraph.axons[miner_uid]],
            synapse = create_request,
            deserialize = True,
            timeout = 10,
        )
        
        if len(responses) != 1:
            bt.logging.info("Something went wrong, number of CreateSynaspe responses bigger than one.")
        
        response_create_request = responses[0]
        
        if response_create_request is None:
            bt.logging.error("Error: None response of CreateRequest.")
            return 0, None
        
        bt.logging.info(f"Received Create responses : {response_create_request} from {miner_uid}")
        
        create_request_zero_score = evaluate_create_request(response_create_request, validator_db_manager, create_request, pageids)
        
        pageids_info = {}
        
        for pageid, vector_id in zip(pageids, response_create_request[3]):
            if type(vector_id) != type(1) or type(pageid) != type(1):
                bt.logging.error("vector_id or pageid is not the Integer.")
            pageids_info[pageid] = vector_id
        
        s_f = "failure"
        if create_request_zero_score:
            total_size = text_length_to_storage_size(total_len)
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
                total_size,
            )
            s_f = "success"
        
        create_op = Operation(
            request_type = "create",
            s_f = s_f,
            score = create_request_zero_score,
            timestamp=datetime.now().isoformat(),
        )
            
    else:
        raise Exception("Error occurs in generating CreateRequest.")
            
    return create_request_zero_score, create_op

async def forward_update_request(self, validator_db_manager, miner_uid):
    
    update_request_zero_scores = []
    update_ops = []
    for i in range(0, 3):
        user_id, organization_id, namespace_id, category, articles, update_request, total_len = await generate_update_request(
            validator_db_manager = validator_db_manager,
            article_size = self.config.neuron.task_size,
            min_len = self.config.neuron.min_len,
            max_len = self.config.neuron.max_len,   
        )
        update_request_zero_score = None
        update_op = None
        if update_request is not None:
            pageids = [article['pageid'] for article in articles]
            
            if total_len < self.config.neuron.task_size * self.config.neuron.min_len:
                bt.logging.error(f"There is an issue to generating task, because the total_len({total_len}) is smaller than task_size * min_len.")
     
            
            bt.logging.info(f"{RED}Sent Update request{RESET}")
            response = await self.dendrite(
                axons = [self.metagraph.axons[miner_uid]],
                synapse = update_request,
                deserialize = True,
                timeout = 20,
            )
            response_update_request = response[0]
            bt.logging.info(f"\n\nReceived Update responses : {response_update_request} from {miner_uid}\n\n")
            update_request_zero_score = evaluate_update_request(update_request, response_update_request, user_id, organization_id, namespace_id, pageids)
            
            s_f = "failure"
            if update_request_zero_score:
                pageids_info = {}
                for pageid, vector_id in zip(pageids, response_update_request[3]):
                    pageids_info[pageid] = vector_id
                
                total_size = text_length_to_storage_size(total_len)
                validator_db_manager.update_operation(
                    "UPDATE",
                    update_request.perform,
                    user_id,
                    organization_id,
                    namespace_id,
                    category,
                    pageids_info,
                    total_size,
                )
                s_f = "success"
            update_request_zero_scores.append(update_request_zero_score)
            
            update_op = Operation(
                request_type = "update",
                s_f = s_f,
                score = update_request_zero_score,
                timestamp=datetime.now().isoformat()
            )
            time.sleep(30)
            
            update_ops.append(update_op)        
            
        else:
            bt.logging.debug("There is no saved data in miner side, Skipping UpdateRequest, Giving zero score.")
            update_request_zero_scores = [0, 0, 0]
    return update_request_zero_scores, update_ops
    
async def forward_delete_request(self, validator_db_manager, miner_uid):
    random_num = random.random()
    delete_request_zero_score = 1
    # random_num = 0.1
    delete_op = None
    if random_num < 0.3:
        
        bt.logging.debug(f"Random number = {random_num}")
        
        user_id, organization_id, namespace_id, delete_request = await generate_delete_request(validator_db_manager)
        
        if delete_request is not None:
            bt.logging.info(f"{RED}Sent Delete request{RESET}")
            
            response = await self.dendrite(
                axons = [self.metagraph.axons[miner_uid]],
                synapse = delete_request,
                deserialize = True,
                timeout = 5,
            )
            response_delete_request = response[0]
            bt.logging.debug(f"Received Delete responses: {response_delete_request} from {miner_uid}") 
            
            s_f = "failure"
            delete_request_zero_score = evaluate_delete_request(delete_request, response_delete_request, user_id, organization_id, namespace_id)
            
            if delete_request_zero_score:
                validator_db_manager.delete_operation("DELETE", user_id, organization_id, namespace_id)
                s_f = "success"
            
            delete_op = Operation(
                request_type = "delete",
                s_f = s_f,
                score = delete_request_zero_score,
                timestamp=datetime.now().isoformat()
            )
            
        else:
            bt.logging.debug("There is no saved data in miner side, Skipping DeleteRequest, Giving zero score.")
            delete_request_zero_score = 0
    return delete_request_zero_score, delete_op
     
async def forward_read_request(self, validator_db_manager, miner_uid):
    
    read_request, content, query_user_id, query_organization_id, query_namespace_id, pageids_info = await generate_read_request(validator_db_manager, self.config.neuron.max_len)
    
    read_score = 0
    read_op = None
    if read_request is not None:
        bt.logging.info(f"{RED}Sent Read request{RESET}")
        
        response = await self.dendrite(
            axons = [self.metagraph.axons[miner_uid]],
            synapse = read_request,
            deserialize = True,
            timeout = 5,
        )
        
        response_read = response[0]
        bt.logging.info(f"Received READ responses from {miner_uid}")
        
        s_f = "failure"
        
        read_score = evaluate_read_request(query_user_id, query_organization_id, query_namespace_id, pageids_info, response_read, content)
        
        if read_score:
            s_f = "success"
            
        read_op = Operation(
            request_type = "read",
            s_f = s_f,
            score = read_score,
            timestamp=datetime.now().isoformat()
        )
        
    else:
        bt.logging.debug("There is no saved data in miner side, Skipping ReadRequest, Giving zero score.")
        
    return read_score, read_op
    
