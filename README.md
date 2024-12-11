<div align="center">

# **VectorStore Subnet** <!-- omit in toc -->
[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

</div>

### Validator and Miner Installation

Please see [Validator and Miner Setup](docs/setup_guide.md)

<!-- ---

> There is a legacy version of the project focusing on decentralized indexing of various data sources, see [here](./docs/openkaito_v0_legacy.md) for more details. -->

## Abstract

This subnet is dedicated to providing a reliable and decentralized vector storage solution, specifically designed to enhance AI training and development within the Bittensor ecosystem.

## Objectives & Contributions

The primary objective of Subnet VectorStore is to embed texts and store them efficiently. Once stored, it processes queries from validators to identify the most relevant results based on the pre-computed embeddings.

Miners are tasked with embedding and storing data, primarily text. They must then identify the most similar results in response to queries from validators, utilizing advanced embedding models to ensure accuracy and relevance.

Validators will rigorously assess miners' performance by evaluating the quality of vector storage and the accuracy of result retrieval, based on the use of powerful embedding models. 

## Units

### User
This is the largest unit of storage, similar to an organization in Pinecone, encompassing multiple organizations.

### Organization
This is the mid-level unit of storage, comprising several namespaces.

### Namespace
This is the smallest unit of storage, capable of containing hundreds or thousands of vectors, each representing an embedding of text.

## How This Subnet Works
### Validator
Validators are tasked with sending queries to miners and performing CRUD operations, which involve issuing four types of queries. They direct miners to embed, save, and manipulate data using create, update, and delete queries, followed by validating storage and embedding performance through read queries. Validators select a text already stored in the miner's namespace, employ a large language model (LLM) to generate summarized content from this text, and send it as a query to the miners. After receiving responses, validators evaluate the outcomes. To accurately assess miners' performance, validators utilize Read Synapse, sending queries in batches that consist of one Create Synapse, three Update Synapses, one optional Delete Synapse, and one Reading Synapse.

### Miner
Miners receive CRUD queries from validators. They are responsible for embedding and saving the data while identifying the most relevant and accurately matched text based on the validators' requests. As their storage size grows over time, it becomes increasingly challenging to locate the correct and most relevant data within the allotted time. To improve performance, miners should employ advanced embedding models and sophisticated techniques for efficient data retrieval.

## Incentive Mechanism

Miners receive CRUD queries from validators, and as they remain in the system longer, maintaining performance becomes challenging due to the continuous increase in data size. To address this, miners are categorized into five groups based on the number of synapse circles they have processed, with older miners receiving higher weights.

***Squire*** : count < 100 (weight = 0.6)

***Knight*** : count < 150 (weight = 0.7)

***Champion*** : count < 250 (weight = 0.8)

***Paladin*** : count < 400 (weight = 0.9)

***Lord*** : count ≥ 400 (weight = 1.0) 🌱

These settings will be modified during the testing phase.

***Rewarding***

If a miner accurately selects the data summarized by the validator, they receive a score of 1.0. If not, the validator assigns a score based on the similarity score calculated using the cosine similarity algorithm, which evaluates the cosine of the angle between two non-zero vectors in an inner product space, providing a measure of their orientation.

The reward is calculated as follows:

$\text{reward} = 0.8 \text{score}^{7} + 0.1 \text{score}^{5} + 0.1 \text{score}^{3}$

This formula ensures that scores close to 1.0 are rewarded more sensitively, while scores significantly lower than 1.0 receive diminishing returns, reflecting a more gradual penalty for decreased performance.

<img src="docs/image/reward1.png" alt="Description" width="500" />




## Computing Requirements

Data stogate:

- Miners need some relable storage to store data(it's curial for miners to lost data even at once)

Embedding model training and advanced searching algorithm(ranking algorithm) for better performance:

- GPUs for training models for powerful embedding and searching

## Development Roadmap

### Distributed Storage Network with Dual Synapse Architecture

**Current Status**
The subnet currently operates with synthetic synapses only, where validators scrape and store Wikipedia data.

**Upcoming Features**
* Dual Synapse System
     * Synthetic Synapses: Automated data collection and storage
     * Organic Synapses: User-submitted data storage

* User-Friendly Storage Interface:
We're developing a Pinecone-like application that allows users to:
     * Store custom text data
     * Store vector embeddings
     * Query stored data efficiently

* Data Flow Architecture
     * User requests are received by validators
     * Validators distribute data to mining nodes
     * Mining nodes handle storage and processing

* Data Reliability & Redundancy.
     To ensure data persistence and reliability we are going to build storage & back-up feature using S3 bucket.

     * Automatic backup system monitors miner status
     * If a miner deregisters, their stored data is:
         * Backed up immediately
         * Redistributed to active miners
     * This prevents data loss and maintains service reliability

* Benefits
     * Fault-tolerant storage system
     * High data availability
     * Reliable service for users
     * Distributed backup mechanism

V1:

- The text-embedding model evaluation and incentive mechanism
- Subnet dashboard with miner's performance growing curve, total-data size and similiarity-score
- Subnet API for integration of our subnet with other subnets like sn4: Targon, Sn5: Openkaito etc.

V2:

- Building the user-interface for real-world usage
- Building the Storage & Backup platform to prevent data loss
- Adding the type of organic Synapses and evaluation mechanism

V3 and further:

- Extending the embedding data with audio and image
- …

