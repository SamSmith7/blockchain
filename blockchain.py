
import hashlib
import json
import requests
from time import time
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.currentTransactions = []
        self.nodes = set()

        # Genesis Block
        self.newBlock(previousHash = 1, proof = 100)

    def newBlock(self, proof, previousHash = None):

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.currentTransactions,
            'proof': proof,
            'previousHash': previousHash or self.hash(self.chain[-1])
        }

        self.currentTransactions = []

        self.chain.append(block)
        return block

    def newTransaction(self, sender, recipient, amount):

        self.currentTransactions.append({
            'amount': amount,
            'sender': sender,
            'recipient': recipient
        })

        return self.lastBlock['index'] + 1

    def registerNode(self, address):

        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)

    @staticmethod
    def hash(block):

        blockString = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockString).hexdigest()

    @property
    def lastBlock(self):

        return self.chain[-1]

    def proofOfWork(self, lastProof):
        proof = 0
        print (lastProof, proof)
        while self.validProof(lastProof, proof) is False:
            proof += 1

        return proof

    def validProof(self, lastProof, proof):

        guess = f'{lastProof}{proof}'.encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:4] == "0000"

    def validChain(self, chain):

        lastBlock = chain[0]
        currentIndex = 1

        while currentIndex < len(chain):
            block = chain[currentIndex]
            print(f'{lastBlock}')
            print(f'{block}')
            print("\n-----------\n")

            if block['previousHash'] != self.hash(lastBlock):
                return False

            if not self.validProof(lastBlock['proof'], block['proof']):
                return False

            lastBlock = block
            currentIndex += 1

        return True

    def resolveConflicts(self):

        neighbours = self.nodes
        newChain = None

        maxLength = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > maxLength and self.validChain(chain):
                    maxLength = maxLength
                    newChain = chain

        if newChain:
            self.chain = newChain
            return True

        return False
