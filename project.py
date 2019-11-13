import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

from flask import Flask, jsonify

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Provjeri ako je hash od prijasnog bloka ispravan
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Provjeri da si prof of work paseju
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False


    def new_block(self, previous_hash, proof):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        # Dictionary treba biti sortirani, inace cemo imati razlicite hasheve
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def proof_of_work(self, last_block):
        """ 
        nadji broj p hash funkcija u kombinaciji sa hashom prijasnog bloka
        daje hash vrijednost koja pocinje sa 4 nule
        """
        
        last_proof = last_block["proof"]
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        guess = f"{last_proof}{proof}{last_hash}".encode()
        print("ovo je guess: ")
        print(guess)
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
# instanciraj server node
app = Flask(__name__)

# generiraj jedinstveni id za server node
node_id = str(uuid4()).replace('-', '')

# instaciraj blockchain
blockchain = Blockchain()

@app_route('/mine', methods=["GET"])
def mine():
    last_block = blockchain.last_block
    proof = proof_of_work(last_block)

    blockchain.new_transaction(
        sender="0",
        recipient=node_id,
        amount=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "Novi blok kreiran",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app_route('/transaction/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app_route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain,
        'length': len(blockchain),
    }
    return jsonify(response), 200

@app_route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return 'Provide nodes for registering', 400

    for node in nodes:
        blockchain.register_node(node)
    
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 200

@app_route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        reponse = {
            'message': 'Our chain has been replaced',
            'new_chain': blockchain.chain
        }
    else:
        reponse = {
            'message': 'Our chain is authoritive',
            'chain': blockchain.chain
        }
    return jsonify(reponse), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)