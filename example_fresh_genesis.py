#!/usr/bin/env python
"""
Genesis modification script on a fresh genesis file.
Usage:
$ ./fresh_genesis_tinker.py
"""
from cosmos_genesis_tinker import Delegator, Validator, GenesisTinker


GENESIS_ARCHIVE = "tests/fresh_genesis.json"
NEW_CHAIN_ID = "tinkered-net"

# Tokens configuration
UATOM_STAKE_INCREASE = 50000000 * 1000000
UATOM_LIQUID_TOKEN_INCREASE = 175000000 * 1000000
MYCO_LIQUID_TOKEN_INCREASE = 1000

# Validator we are replacing
old_val = Validator()
old_val.self_delegation_address = 'cosmos1lj54q70v2mt9e7c5mtp5xgg5n9c0hkas60kec9'
old_val.self_delegation_public_key = 'Aiu5OMUoNnBnWiWOC/Z/Luyq2XFROqubW5oP4Y8y/Lzz'
old_val.address = '19CEF0E87C6FBDED2A2A486069C8F4DD51BD3981'
old_val.public_key = 'T6bqYkfRS1toJAFN8R34MByeuj1siCx0/0GdIgX8SmI='
old_val.operator_address = 'cosmosvaloper1lj54q70v2mt9e7c5mtp5xgg5n9c0hkaslmzv5k'
old_val.consensus_address = 'cosmosvalcons1r880p6rud7776232fpsxnj85m4gm6wvpe2pkp2'

# New validator
new_val = Validator()
new_val.self_delegation_address = 'cosmos1wvvhhfm387xvfnqshmdaunnpujjrdxznr5d5x9'
new_val.self_delegation_public_key = 'ApDOUyfcamDmnbEO7O4YKnKQQqQ93+gquLfGf7h5clX7'
new_val.operator_address = 'cosmosvaloper1wvvhhfm387xvfnqshmdaunnpujjrdxznxqep2k'
new_val.public_key = 'qwiUMxz3llsy45fPvM0a8+XQeAJLvrX3QAEJmRMEEoU='
new_val.address = 'D5AB5E458FD9F9964EF50A80451B6F3922E6A4AA'
new_val.consensus_address = 'cosmosvalcons16k44u3v0m8uevnh4p2qy2xm08y3wdf92xsc3ve'

# Delegator
new_del = Delegator()
new_del.address = 'cosmos1wvvhhfm387xvfnqshmdaunnpujjrdxznr5d5x9'
new_del.public_key = 'ApDOUyfcamDmnbEO7O4YKnKQQqQ93+gquLfGf7h5clX7'


print("Tinkering")

tinkerer = GenesisTinker(input_file=GENESIS_ARCHIVE)

# Swap validators
tinkerer.add_task(tinkerer.replace_validator,
                  old_validator=old_val,
                  new_validator=new_val)
# Set chain id to 'tinkered-net'
tinkerer.add_task(tinkerer.set_chain_id,
                  chain_id=NEW_CHAIN_ID)
# Earth validator adjustments
tinkerer.add_task(tinkerer.increase_balance,
                  address=new_del.address,
                  amount=UATOM_LIQUID_TOKEN_INCREASE)
tinkerer.add_task(tinkerer.increase_balance,
                  address=new_val.self_delegation_address,
                  amount=MYCO_LIQUID_TOKEN_INCREASE,
                  denom="myco")
tinkerer.add_task(tinkerer.increase_delegator_stake_to_validator,
                  delegator=new_del,
                  validator=new_val,
                  increase={'amount': UATOM_STAKE_INCREASE, 'denom': 'uatom'})

# Set governance parameters
tinkerer.add_task(tinkerer.set_min_deposit, min_amount='1')  # 1 uatom
tinkerer.add_task(tinkerer.set_tally_param,
                  parameter_name='quorum', value='0.000000000000000001')
tinkerer.add_task(tinkerer.set_tally_param,
                  parameter_name='threshold', value='0.000000000000000001')
tinkerer.add_task(tinkerer.set_voting_period, voting_period='60s')
# Make redelegations faster
tinkerer.add_task(tinkerer.set_unbonding_time, unbonding_time='1s')

tinkerer.run_tasks()
