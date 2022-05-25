#!/usr/bin/env python
"""
Genesis modification script on a stateful genesis file.
This example will turn a genesis file exported from mainnet
into the genesis used for theta-testnet-001.
Usage:
$ ./genesis_theta.py
"""
from cosmos_genesis_tinker import Delegator, Validator, GenesisTinker

GENESIS_ARCHIVE = "tests/stateful_genesis.json"

NEW_CHAIN_ID = "theta-testnet-001"

# Tokens configuration
UATOM_STAKE_INCREASE = 550000000 * 1000000
UATOM_LIQUID_TOKEN_INCREASE = 175000000 * 1000000

THETA_LIQUID_TOKEN_INCREASE = 1000
RHO_LIQUID_TOKEN_INCREASE = 1000
LAMBDA_LIQUID_TOKEN_INCREASE = 1000
EPSILON_LIQUID_TOKEN_INCREASE = 1000

# The Coinbase validator is being replaced with the earth node
cb_val = Validator()
cb_val.self_delegation_address = "cosmos1a3yjj7d3qnx4spgvjcwjq9cw9snrrrhu3rw8nv"
cb_val.self_delegation_public_key = "Ar7QZgBj/ZF6OFqFP5N1M2CoWYdwQcJyVBI/lgOAAaLu"
cb_val.operator_address = "cosmosvaloper1a3yjj7d3qnx4spgvjcwjq9cw9snrrrhu5h6jll"
cb_val.public_key = "NK3/1mb/ToXmxlcyCK8HYyudDn4sttz1sXyyD+42x7I="
cb_val.address = "F8C01C0681578AA700D736D675C9992065F65E3E"
cb_val.consensus_address = "cosmosvalcons1lrqpcp5p2792wqxhxmt8tjveypjlvh378gkddu"

earth_val = Validator()
earth_val.self_delegation_address = "cosmos10v6wvdenee8r9l6wlsphcgur2ltl8ztkvhc8fw"
earth_val.self_delegation_public_key = "AsYk9vGihCDVRd8V70Ti7FgVptqunyRv9S22J2XM9njJ"
earth_val.operator_address = "cosmosvaloper10v6wvdenee8r9l6wlsphcgur2ltl8ztkfrvj9a"
earth_val.public_key = "2j+NkKQHAxu36vduy1sDHJZIeZji7nxnmVIizv07MpE="
earth_val.address = "A8A7A64D1F8FFAF2A5332177F777A5816036D65A"
earth_val.consensus_address = "cosmosvalcons14zn6vngl3la09ffny9mlwaa9s9srd4j65cqc54"

earth_del = Delegator()
earth_del.address = "cosmos10v6wvdenee8r9l6wlsphcgur2ltl8ztkvhc8fw"
earth_del.public_key = "AsYk9vGihCDVRd8V70Ti7FgVptqunyRv9S22J2XM9njJ"

print("Tinkering...")
gentink = GenesisTinker(input_file=GENESIS_ARCHIVE)

gentink.add_task(gentink.replace_validator,
                 old_validator=cb_val,
                 new_validator=earth_val)

gentink.add_task(gentink.set_chain_id,
                 chain_id=NEW_CHAIN_ID)

gentink.add_task(gentink.increase_balance,
                 address=earth_val.self_delegation_address,
                 amount=UATOM_LIQUID_TOKEN_INCREASE)
gentink.add_task(gentink.increase_balance,
                 address=earth_val.self_delegation_address,
                 amount=THETA_LIQUID_TOKEN_INCREASE,
                 denom='theta')
gentink.add_task(gentink.increase_balance,
                 address=earth_val.self_delegation_address,
                 amount=RHO_LIQUID_TOKEN_INCREASE,
                 denom='rho')
gentink.add_task(gentink.increase_balance,
                 address=earth_val.self_delegation_address,
                 amount=LAMBDA_LIQUID_TOKEN_INCREASE,
                 denom='lambda')
gentink.add_task(gentink.increase_balance,
                 address=earth_val.self_delegation_address,
                 amount=EPSILON_LIQUID_TOKEN_INCREASE,
                 denom='epsilon')

gentink.add_task(gentink.increase_delegator_stake_to_validator,
                 delegator=earth_del,
                 validator=earth_val,
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
