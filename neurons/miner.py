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
import vectornet
from vectornet.protocol import(
    CreateSynapse,
    ReadSynapse,
    UpdateSynapse,
    DeleteSynapse,
)
from vectornet.utils.version import compare_version, get_version
from vectornet.embedding.embed import TextToEmbedding
from vectornet.database_manage.db_manager import DBManager
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
        
        validator_db_manager = DBManager(validator_hotkey)
        
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
        
        validator_db_manager = DBManager(valdiator_hotkey)
        
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
        
        validator_db_manager = DBManager(validator_hotkey)
        
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
        
        validator_db_manager = DBManager(validator_hotkey)
        
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

    async def blacklist(
        self, synapse: vectornet.protocol.Dummy
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contracted via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (vectornet.protocol.Dummy): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """

        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            bt.logging.warning(
                "Received a request without a dendrite or hotkey."
            )
            return True, "Missing dendrite or hotkey"

        # TODO(developer): Define how miners should blacklist requests.
        uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
        if (
            not self.config.blacklist.allow_non_registered
            and synapse.dendrite.hotkey not in self.metagraph.hotkeys
        ):
            # Ignore requests from un-registered entities.
            bt.logging.trace(
                f"Blacklisting un-registered hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        if self.config.blacklist.force_validator_permit:
            # If the config is set to force validator permit, then we should only allow requests from validators.
            if not self.metagraph.validator_permit[uid]:
                bt.logging.warning(
                    f"Blacklisting a request from non-validator hotkey {synapse.dendrite.hotkey}"
                )
                return True, "Non-validator hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(self, synapse: vectornet.protocol.Dummy) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (vectornet.protocol.Dummy): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may receive messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            bt.logging.warning(
                "Received a request without a dendrite or hotkey."
            )
            return 0.0

        # TODO(developer): Define how miners should prioritize requests.
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        priority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: {priority}"
        )
        return priority
    
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

# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info(f"Miner running... {time.time()}")
            time.sleep(5)
