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
import typing
import bittensor as bt

# Bittensor Miner vectornet:
import vectornet

# import base miner class which takes care of most of the boilerplate
from vectornet.base.miner import BaseMinerNeuron
from vectornet.protocol import(
    CreateSynapse,
    ReadSynapse,
    UpdateSynapse,
    DeleteSynapse,
)
from vectornet.utils.version import compare_version, get_version
from vectornet.embedding.embed import TextToEmbedding
from vectornet.database_manage.miner_db_manager import MinerDBManager
from vectornet.search_engine.search import SearchEngine

class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)


        # TODO(developer): Anything specific to your use case you can do here

    async def forward_create_request(self, query: CreateSynapse) -> CreateSynapse:
        """
        processes the incoming CreateSynapse by creating new embeddings and saving them in database
        """
        self.check_version(query.version)
        
        request_type = query.type
        user_name = query.user_name
        organization_name = query.organization_name
        namespace_name = query.namespace_name
        index_data = query.index_data
        validator_hotkey = query.dendrite.hotkey
        
        validator_db_manager = MinerDBManager(validator_hotkey)
        
        embedding_manager = TextToEmbedding()
        
        embeded_data, embeddings, original_data = embedding_manager.embed(index_data)
        results = []
        user_id, organization_id, namespace_id = validator_db_manager.create_operation(request_type, user_name, organization_name, namespace_name, embeded_data, embeddings, original_data)
        results.append(user_id)
        results.append(organization_id)
        results.append(namespace_id)
        
        query.results = results
        
    async def forward_read_request(self, query: ReadSynapse) -> ReadSynapse:
        """
        processes the incoming ReadSynapse by searching the most similar texts with query by comparing embeddings
        between query and saved data using advanced searching algorithms
        """
        self.check_version(query.version)
        
        request_type = query.type
        user_name = query.user_name
        organization_name = query.organization_name
        namespace_name = query.namespace_name
        query_data = query.query_data
        size = query.size
        valdiator_hotkey = query.dendrite.hotkey
        
        validator_db_manager = MinerDBManager(valdiator_hotkey)
        
        embedding_manager = TextToEmbedding()
        
        vectors = validator_db_manager.read_operation(request_type, user_name, organization_name, namespace_name)
        
        query_embedding = embedding_manager.embed(query_data)
        
        search_engine = SearchEngine()
        
        top_vectors = search_engine.cosine_similarity_search(query_embedding, vectors, size)
        
        results = []
        for top_vector in top_vectors:
            results.append({'text': top_vector['original_text'], 'embedding': top_vector['embedding']})

        query.results = results
        
    async def forward_update_request(self, query: UpdateSynapse) -> UpdateSynapse:
        """
        processes the incoming UpdateSynapse by updating existing embeddings that saved in database
        """
        self.check_version(query.version)
        
        perform = query.perform.lower()
        if perform != 'replace' and perform != 'add':
            raise Exception(f"Undifined perform type: {perform} in UpdateSynapse")

        request_type = query.type
        user_name = query.user_name
        organization_name = query.organization_name
        namespace_name = query.namespace_name
        index_data = query.index_data
        validator_hotkey = query.dendrite.hotkey
        
        validator_db_manager = MinerDBManager(validator_hotkey)
        
        embedding_manager = TextToEmbedding()
        
        embeded_data, embeddings, original_data = embedding_manager.embed(index_data)
        
        results = []
        user_id, organization_id, namespace_id = validator_db_manager.update_operation(request_type, perform, user_name, organization_name, namespace_name, embeded_data, embeddings, original_data)
        results.append(user_id)
        results.append(organization_id)
        results.append(namespace_id)
        
        query.results = results
        
    async def forward_delete_request(self, query: DeleteSynapse) -> DeleteSynapse:
        self.check_version(query.version)
        
        perform = query.perform.lower()
        if perform != 'user' and perform != 'organization' and perform != 'namespace':
            raise Exception(f"Undifined perfom type: {perform} in DeleteSynapse")
        
        request_type = query.type
        user_name = query.user_name
        organization_name = query.organization_name
        namespace_name = query.namespace_name
        validator_hotkey = query.dendrite.hotkey
        
        validator_db_manager = MinerDBManager(validator_hotkey)
        
        results = []
        user_id, organization_id, namespace_id = validator_db_manager.delete_operation(request_type, perform, user_name, organization_name, namespace_name)        
        results.append(user_id)
        results.append(organization_id)
        results.append(namespace_id)
        
        query.results = results

    async def forward(
        self, synapse: vectornet.protocol.Dummy
    ) -> vectornet.protocol.Dummy:
        """
        Processes the incoming 'Dummy' synapse by performing a predefined operation on the input data.
        This method should be replaced with actual logic relevant to the miner's purpose.

        Args:
            synapse (vectornet.protocol.Dummy): The synapse object containing the 'dummy_input' data.

        Returns:
            vectornet.protocol.Dummy: The synapse object with the 'dummy_output' field set to twice the 'dummy_input' value.

        The 'forward' function is a placeholder and should be overridden with logic that is appropriate for
        the miner's intended operation. This method demonstrates a basic transformation of input data.
        """
        # TODO(developer): Replace with actual implementation logic.
        synapse.dummy_output = synapse.dummy_input * 2
        return synapse

    def check_version(self, version):
        """
        Check the version of request is up to date with subnet
        """
        if (version is not None 
            and compare_version(version, get_version()) > 0
        ):
            bt.logging.warning(
                f"Received request with version {version}, is newer than miner running version {get_version()}"
            )
            
    def print_info(self):
        metagraph = self.metagraph
        self.uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)

        log = (
            "Miner | "
            f"Epoch:{self.step} | "
            f"UID:{self.uid} | "
            f"Block:{self.block} | "
            f"Stake:{metagraph.S[self.uid]} | "
            f"Rank:{metagraph.R[self.uid]} | "
            f"Trust:{metagraph.T[self.uid]} | "
            f"Consensus:{metagraph.C[self.uid] } | "
            f"Incentive:{metagraph.I[self.uid]} | "
            f"Emission:{metagraph.E[self.uid]}"
        )
        bt.logging.info(log)

# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info(f"Miner running... {time.time()}")
            time.sleep(30)
