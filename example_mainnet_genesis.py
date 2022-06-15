#!/usr/bin/env python
"""
This example will turn a genesis file exported from mainnet
into a genesis file that has a single validator.
Usage:
$ ./example_mainnet_genesis.py
To recover the validator key, use the following mnemonic:
abandon abandon abandon abandon abandon abandon abandon abandon
abandon abandon abandon abandon abandon abandon abandon abandon
abandon abandon abandon abandon abandon abandon abandon art
"""
from cosmos_genesis_tinker import Delegator, Validator, GenesisTinker

GENESIS_ARCHIVE = "tests/mainnet_genesis.json"

NEW_CHAIN_ID = "local-testnet"

# Tokens configuration
UATOM_STAKE_INCREASE = 550000000 * 1000000
UATOM_LIQUID_TOKEN_INCREASE = 175000000 * 1000000

# The Coinbase validator is being replaced with the earth node
cb_val = Validator()
cb_val.self_delegation_address = "cosmos1a3yjj7d3qnx4spgvjcwjq9cw9snrrrhu3rw8nv"
cb_val.self_delegation_public_key = "Ar7QZgBj/ZF6OFqFP5N1M2CoWYdwQcJyVBI/lgOAAaLu"
cb_val.operator_address = "cosmosvaloper1a3yjj7d3qnx4spgvjcwjq9cw9snrrrhu5h6jll"
cb_val.public_key = "NK3/1mb/ToXmxlcyCK8HYyudDn4sttz1sXyyD+42x7I="
cb_val.address = "F8C01C0681578AA700D736D675C9992065F65E3E"
cb_val.consensus_address = "cosmosvalcons1lrqpcp5p2792wqxhxmt8tjveypjlvh378gkddu"

test_val = Validator()
test_val.self_delegation_address = "cosmos1r5v5srda7xfth3hn2s26txvrcrntldjumt8mhl"
test_val.self_delegation_public_key = "ArpmqEz3g5rxcqE+f8n15wCMuLyhWF+PO6+zA57aPB/d"
test_val.operator_address = "cosmosvaloper1ju7y3hutxdtvghjyf9rj8fhq63w7hqf3r59lf0"
test_val.public_key = "xAqzjs6UkEg8YvoQy60bxytIocODxoDTNRz4+H81tTc="
test_val.address = "973C48DF8B3356C45E44494723A6E0D45DEB8131"
test_val.consensus_address = "cosmosvalcons1ju7y3hutxdtvghjyf9rj8fhq63w7hqf3h8kr9w"

test_del = Delegator()
test_del.address = "cosmos1r5v5srda7xfth3hn2s26txvrcrntldjumt8mhl"
test_del.public_key = "ArpmqEz3g5rxcqE+f8n15wCMuLyhWF+PO6+zA57aPB/d"

print("Tinkering...")
gentink = GenesisTinker(input_file=GENESIS_ARCHIVE)

gentink.add_task(gentink.replace_validator,
                 old_validator=cb_val,
                 new_validator=test_val)

gentink.add_task(gentink.set_chain_id,
                 chain_id=NEW_CHAIN_ID)

gentink.add_task(gentink.increase_balance,
                 address=test_val.self_delegation_address,
                 amount=UATOM_LIQUID_TOKEN_INCREASE)

gentink.add_task(gentink.increase_delegator_stake_to_validator,
                 delegator=test_del,
                 validator=test_val,
                 increase={'amount': UATOM_STAKE_INCREASE,
                           'denom': 'uatom'})

# Set new governance parameters for convenience
gentink.add_task(gentink.set_min_deposit,
                 min_amount='1',
                 denom='uatom')
gentink.add_task(gentink.set_tally_param,
                 parameter_name='quorum',
                 value='0.000000000000000001')
gentink.add_task(gentink.set_tally_param,
                 parameter_name='threshold',
                 value='0.000000000000000001')
gentink.add_task(gentink.set_voting_period,
                 voting_period='60s')

# Make redelegations faster
gentink.add_task(gentink.set_unbonding_time,
                 unbonding_time='1s')

gentink.run_tasks()
