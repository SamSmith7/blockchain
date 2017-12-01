from textwrap import dedent
from flask import Flask, jsonify, request
from uuid import uuid4
from sys import stdout

from blockchain import Blockchain


app = Flask(__name__)

nodeIdentifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():

    lastBlock = blockchain.lastBlock
    lastProof = lastBlock['proof']
    proof = blockchain.proofOfWork(lastProof)

    blockchain.newTransaction(
        sender = '0',
        recipient = nodeIdentifier,
        amount = 1
    )

    previousHash = blockchain.hash(lastBlock)
    block = blockchain.newBlock(proof, previousHash)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previousHash': block['previousHash']
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def newTransaction():

    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.newTransaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def fullChain():

    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def registerNodes():


    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.registerNode(node)

    response = {
        'message': 'New nodes have been added',
        'totalNodes': list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route('/nodes/consensus', methods=['GET'])
def consensus():

    replaced = blockchain.resolveConflicts()

    if replaced :
        response = {
            'message': 'Our chain was replaced',
            'newChain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
