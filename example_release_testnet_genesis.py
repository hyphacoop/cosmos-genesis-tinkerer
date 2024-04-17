#!/usr/bin/env python
"""
This example will turn a genesis file exported from the release testnet
into a genesis file that has a single validator.
Usage:
$ ./example_release_testnet_genesis.py
To recover the validator key, use the following mnemonic:
abandon abandon abandon abandon abandon abandon abandon abandon
abandon abandon abandon abandon abandon abandon abandon abandon
abandon abandon abandon abandon abandon abandon abandon art
"""
from cosmos_genesis_tinker import Delegator, Validator, GenesisTinker

GENESIS_ARCHIVE = "release-testnet-export.json"

NEW_CHAIN_ID = "release-testnet"

# Tokens configuration
UATOM_STAKE_INCREASE = 5500000000 * 1000000
UATOM_LIQUID_TOKEN_INCREASE = 1750000000 * 1000000

# The earth validator will be replaced
earth_val = Validator()
earth_val.self_delegation_address = "cosmos10v6wvdenee8r9l6wlsphcgur2ltl8ztkvhc8fw"
earth_val.self_delegation_reward_address = "cosmos10v6wvdenee8r9l6wlsphcgur2ltl8ztkvhc8fw"
earth_val.self_delegation_public_key = "AsYk9vGihCDVRd8V70Ti7FgVptqunyRv9S22J2XM9njJ"
earth_val.operator_address = "cosmosvaloper10v6wvdenee8r9l6wlsphcgur2ltl8ztkfrvj9a"
earth_val.public_key = "2j+NkKQHAxu36vduy1sDHJZIeZji7nxnmVIizv07MpE="
earth_val.address = "A8A7A64D1F8FFAF2A5332177F777A5816036D65A"
earth_val.consensus_address = "cosmosvalcons14zn6vngl3la09ffny9mlwaa9s9srd4j65cqc54"

test_val = Validator()
test_val.self_delegation_address = "cosmos1r5v5srda7xfth3hn2s26txvrcrntldjumt8mhl"
test_val.self_delegation_reward_address = "cosmos1r5v5srda7xfth3hn2s26txvrcrntldjumt8mhl"
test_val.self_delegation_public_key = "ArpmqEz3g5rxcqE+f8n15wCMuLyhWF+PO6+zA57aPB/d"
test_val.operator_address = "cosmosvaloper1r5v5srda7xfth3hn2s26txvrcrntldju7lnwmv"
test_val.public_key = "xAqzjs6UkEg8YvoQy60bxytIocODxoDTNRz4+H81tTc="
test_val.address = "973C48DF8B3356C45E44494723A6E0D45DEB8131"
test_val.consensus_address = "cosmosvalcons1ju7y3hutxdtvghjyf9rj8fhq63w7hqf3h8kr9w"

test_del = Delegator()
test_del.address = "cosmos1r5v5srda7xfth3hn2s26txvrcrntldjumt8mhl"
test_del.public_key = "ArpmqEz3g5rxcqE+f8n15wCMuLyhWF+PO6+zA57aPB/d"

print("Tinkering...")
gentink = GenesisTinker(input_file=GENESIS_ARCHIVE)

gentink.add_task(gentink.replace_validator,
                 old_validator=earth_val,
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
gentink.add_task(gentink.add_allowed_ibc_client,
                 allowed_ibc_client='09-localhost')
gentink.add_task(gentink.increase_balance,
                 address='cosmos10d07y265gmmuvt4z0w9aw880jnsr700j6zn9kn',
                 amount=-100000)
gentink.run_tasks()
