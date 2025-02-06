import asyncio
import threading
import argparse
import traceback
import bittensor as bt
from vectornet.base.neuron import BaseNeuron
from vectornet.utils.config import add_miner_args
from typing import Union, Tuple
from vectornet.protocol import(
    CreateSynapse,
    ReadSynapse,
    UpdateSynapse,
    DeleteSynapse,
)

class BaseMinerNeuron(BaseNeuron):
    """
    Base class for Bittensor miners.
    """
    neuron_type: str = "MinerNeuron"

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        super().add_args(parser)
        add_miner_args(cls, parser)

    def __init__(self, config=None):
        super().__init__(config=config)

        if not self.config.blacklist.force_validator_permit:
            bt.logging.warning(
                "You are allowing non-validators to send requests to your miner. This is a security risk."
            )
        if self.config.blacklist.allow_non_registered:
            bt.logging.warning(
                "You are allowing non-registered entities to send requests to your miner. This is a security risk."
            )
        self.axon = bt.axon(
            wallet=self.wallet,
            port=self.config.axon.port,
        )

        bt.logging.info(f"Attaching forward function to miner axon.")
        self.axon.attach(
            forward_fn=self.forward_create_request,
            blacklist_fn=self.blacklist_create_request,
            priority_fn=self.priority_create_request,
        ).attach(
            forward_fn=self.forward_read_request,
            blacklist_fn=self.blacklist_read_request,
            priority_fn=self.priority_read_request,
        ).attach(
            forward_fn=self.forward_update_request,
            blacklist_fn=self.blacklist_update_request,
            priority_fn=self.priority_update_request,
        ).attach(
            forward_fn=self.forward_delete_request,
            blacklist_fn=self.blacklist_delete_request,
            priority_fn=self.priority_delete_request,
        )
    
        bt.logging.info(f"Axon created: {self.axon}")

        self.should_exit: bool = False
        self.is_running: bool = False
        self.thread: Union[threading.Thread, None] = None
        self.lock = asyncio.Lock()

    async def forward_create_request(self, query: CreateSynapse) -> CreateSynapse:
        bt.logging.warning("forward_create_request method is not implemented yet")
        
    async def forward_read_request(self, query: ReadSynapse) -> ReadSynapse:
        bt.logging.warning("forward_read_request method is not implemented yet")
        
    async def forward_update_request(self, query: UpdateSynapse) -> UpdateSynapse:
        bt.logging.warning("forward_update_request method is not implemented yet")
        
    async def forward_delete_request(self, query: DeleteSynapse) -> DeleteSynapse:
        bt.logging.warning("forward_delete_request method is not implemented yet")

    def run(self):
        """
        Initiates and manages the main loop for the miner on the Bittensor network. The main loop handles graceful shutdown on keyboard interrupts and logs unforeseen errors.

        This function performs the following primary tasks:
        1. Check for registration on the Bittensor network.
        2. Starts the miner's axon, making it active on the network.
        3. Periodically resynchronizes with the chain; updating the metagraph with the latest network state and setting weights.

        The miner continues its operations until `should_exit` is set to True or an external interruption occurs.
        During each epoch of its operation, the miner waits for new blocks on the Bittensor network, updates its
        knowledge of the network (metagraph), and sets its weights. This process ensures the miner remains active
        and up-to-date with the network's latest state.

        Note:
            - The function leverages the global configurations set during the initialization of the miner.
            - The miner's axon serves as its interface to the Bittensor network, handling incoming and outgoing requests.

        Raises:
            KeyboardInterrupt: If the miner is stopped by a manual interruption.
            Exception: For unforeseen errors during the miner's operation, which are logged for diagnosis.
        """

        self.sync()

        bt.logging.info(
            f"Serving miner axon {self.axon} on network: {self.config.subtensor.chain_endpoint} with netuid: {self.config.netuid}"
        )
        self.axon.serve(netuid=self.config.netuid, subtensor=self.subtensor)

        self.axon.start()

        bt.logging.info(f"Miner starting at block: {self.block}")

        # This loop maintains the miner's operations until intentionally stopped.
        # try:
        #     while not self.should_exit:
        #         while (
        #             self.block - self.metagraph.last_update[self.uid]
        #             < self.config.neuron.epoch_length
        #         ):
        #             # Wait before checking again.
        #             time.sleep(1)

        #             # Check if we should exit.
        #             if self.should_exit:
        #                 break

        #         # Sync metagraph and potentially set weights.
        #         self.sync()
        #         self.step += 1
        #         bt.logging.debug(f"Current step: {self.step}")
        
        try:
            self.sync()
        
        except KeyboardInterrupt:
            self.axon.stop()
            bt.logging.success("Miner killed by keyboard interrupt.")
            exit()

        except Exception as e:
            bt.logging.error(traceback.format_exc())

    def run_in_background_thread(self):
        """
        Starts the miner's operations in a separate background thread.
        This is useful for non-blocking operations.
        """
        if not self.is_running:
            bt.logging.debug("Starting miner in background thread.")
            self.should_exit = False
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            self.is_running = True
            bt.logging.debug("Started")

    def stop_run_thread(self):
        """
        Stops the miner's operations that are running in the background thread.
        """
        if self.is_running:
            bt.logging.debug("Stopping miner in background thread.")
            self.should_exit = True
            if self.thread is not None:
                self.thread.join(5)
            self.is_running = False
            bt.logging.debug("Stopped")

    def __enter__(self):
        """
        Starts the miner's operations in a background thread upon entering the context.
        This method facilitates the use of the miner in a 'with' statement.
        """
        self.run_in_background_thread()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stops the miner's background operations upon exiting the context.
        This method facilitates the use of the miner in a 'with' statement.

        Args:
            exc_type: The type of the exception that caused the context to be exited.
                      None if the context was exited without an exception.
            exc_value: The instance of the exception that caused the context to be exited.
                       None if the context was exited without an exception.
            traceback: A traceback object encoding the stack trace.
                       None if the context was exited without an exception.
        """
        self.stop_run_thread()

    def resync_metagraph(self):
        """Resyncs the metagraph and updates the hotkeys and moving averages based on the new metagraph."""
        bt.logging.info("resync_metagraph()")
        # Sync the metagraph.
        self.metagraph.sync(subtensor=self.subtensor)

    async def blacklist(self, synapse: bt.synapse) -> Tuple[bool, str]:
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

    async def priority(self, synapse: bt.synapse) -> float:
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
    
    def save_state(self):
        """Saves the state of the validator to a file."""
        pass

        # Save the state of the validator to file.


    async def blacklist_create_request(self, synapse: CreateSynapse) -> Tuple[bool, str]:
        return await self.blacklist(synapse)
    
    async def blacklist_read_request(self, synapse: ReadSynapse) -> Tuple[bool, str]:
        return await self.blacklist(synapse)
    
    async def blacklist_update_request(self, synapse: UpdateSynapse) -> Tuple[bool, str]:
        return await self.blacklist(synapse)
    
    async def blacklist_delete_request(self, synapse: DeleteSynapse) -> Tuple[bool, str]:
        return await self.blacklist(synapse)
    
    async def priority_create_request(self, synapse: CreateSynapse) -> float:
        return await self.priority(synapse)

    async def priority_read_request(self, synapse: ReadSynapse) -> float:
        return await self.priority(synapse)

    async def priority_update_request(self, synapse: UpdateSynapse) -> float:
        return await self.priority(synapse)

    async def priority_delete_request(self, synapse: DeleteSynapse) -> float:
        return await self.priority(synapse)
