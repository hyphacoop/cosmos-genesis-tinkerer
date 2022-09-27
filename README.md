# Cosmos Genesis Tinker

A Python module for modifying Cosmos genesis files.

Use this tool to test how the network reacts to a given scenario. The available operations include (but are not limited to):
* Swapping validators
* Swapping delegators
* Increasing balance
* Increasing validator power
* Increasing delegator stake to a validator

⚠️ This project is in active development. 

## Setup

### Requirements

* Python 3.10

1. Clone from github:  `git clone git@github.com:hyphacoop/cosmos-genesis-tinkerer.git`
2. Change directory: `cd cosmos-genesis-tinkerer`
3. Create a python virtual environment: `python -m venv .env`
4. Source env shell vars:  `source .env/bin/activate`
5. Install requirements: `pip install -r requirements.txt`

## Running a tinker file

You can run an example genesis tinker file like this:
```
./example_fresh_genesis.py
```

It will read the `fresh_genesis.json` file from the `tests` folder and generate `tinkered_genesis.json`.

## Usage

Access full module documentation with `pydoc cosmos_genesis_tinker`.

Example:

```python
from cosmos_genesis_tinker import GenesisTinker, Delegator

tinker = cosmos_genesis_tinker.GenesisTinker(
    input_file='input.json',
    output_file='output.json')

old_del = Delegator()
old_del.address = 'cosmos123'
old_del.public_key = 'abcxyz'

new_del = Delegator()
new_del.address = 'cosmos456'
new_del.public_key = 'defuvw'

tinker.add_task(tinker.replace_delegator,
    old_delegator=old_del,
    new_delegator=new_del)
    
tinker.add_task(tinker.increase_balance,
    address=new_delegator.address,
    amount=9000000000,
    denom='uatom')

tinker.run_tasks()
```

## Exported genesis files
We export the `cosmoshub-4` genesis bi-weekly and modify the exported genesis with `example_mainnet_genesis.py`:

- A set of exported `cosmoshub-4` genesis files can be found [here](https://files.polypore.xyz/genesis/mainnet-genesis-export/).
- A set of tinkered `cosmoshub-4` genesis files can be found [here](https://files.polypore.xyz/genesis/mainnet-genesis-tinkered/).
