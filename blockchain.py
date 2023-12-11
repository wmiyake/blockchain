import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockchain:

    def __init__(self):
        self.chain = []
        self.create_block(proof=1, current_hash='0')

    def create_block(self, proof, current_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'current_hash': current_hash}
        self.chain.append(block)
        return block

    def get_current_block(self):
        return self.chain[-1]

    def proof_of_work(self, current_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - current_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        current_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['current_hash'] != self.hash(current_block):
                return False
            current_proof = current_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - current_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            current_block = block
            block_index += 1
        return True


app = Flask(__name__)

blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    current_block = blockchain.get_current_block()
    current_proof = current_block['proof']
    proof = blockchain.proof_of_work(current_proof)
    current_hash = blockchain.hash(current_block)
    block = blockchain.create_block(proof, current_hash)
    response = {'message': 'Parabens voce acabou de minerar um bloco!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'current_hash': block['current_hash']}
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response_chain = []
    for i, block in enumerate(blockchain.chain):
        current_hash = blockchain.hash(block)
        previous_hash = blockchain.hash(blockchain.chain[i - 1]) if i > 0 else '0'
        response_block = {
            'index': block['index'],
            'timestamp': block['timestamp'],
            'proof': block['proof'],
            'current_hash': current_hash,
            'previous_hash': previous_hash
        }
        response_chain.append(response_block)

    response = {'chain': response_chain,
                'length': len(response_chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': ' Tudo certo, o blockchain e valido '}
    else:
        response = {'message': ' O blockchain nao e valido '}
    return jsonify(response), 200

app.run(host='0.0.0.0', port=5000)
