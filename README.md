# Cosmos Genesis Tinker

A Python module for modifying Cosmos genesis files.

Use this tool to test how the network reacts to a given scenario. The available operations include (but are not limited to):
* Swapping validators
* Swapping delegators
* Increasing balance
* Increasing validator power
* Increasing delegator stake to a validator

Full documentation for the module can be accessed with `pydoc cosmos_genesis_tinker`.

⚠️ This project is in active development. 

## Setup

### Requirements

* Python 3.10

1. Clone from github:  `git clone git@github.com:hyphacoop/cosmos-genesis-tinkerer.git`
2. Change directory: `cd cosmos-genesis-tinkerer`
3. Create a python virtual environment: `python3 -m venv .env`
4. Source env shell vars:  `source .env/bin/activate`
5. Install requirements: `pip install -r requirements.txt`

## Running a tinker file

You can run the theta tinker file like this:
```
./genesis_theta.py --output new_genesis.json
```

## Developing

Save the required pip modules to `requirements.txt` whenever they change:
```
pip freeze > requirements. txt
```

## API

Tinkering with genesis files

```python
import cosmos_genesis_tinker

genesis = cosmos_genesis_tinker.GenesisTinker()

genesis.load_file(file)
genesis.save_file(file)
old  = {
"pub_key": "",
"address": "",
"consensus_address": ""
}
genesis.swap_validator(old, new)
genesis.swap_delegator(old_adddress, new_address)
genesis.increase_balance(address, increase=300000000, denom="uatom")
genesis.increase_validator_power(validator_address, power_increase=DEFAULT_POWER)
genesis.increase_validator_stake(operator_address, increase=DEFAULT_POWER*POWER_TO_TOKENS)
genesis.increase_delegator_stake(delegator_address, increase=DEFAULT_POWER*POWER_TO_TOKENS)
```
