#!/usr/bin/env python3
"""
  earth validator
  address: cosmos10v6wvdenee8r9l6wlsphcgur2ltl8ztkvhc8fw
  pubkey: '{"@type":"/cosmos.crypto.secp256k1.PubKey","key":"AsYk9vGihCDVRd8V70Ti7FgVptqunyRv9S22J2XM9njJ"}'
  }
"""
import sys
import cosmos_genesis_tinker
import subprocess
import shutil

GENESIS_ARCHIVE = "./exported_genesis.json"

NEW_CHAIN_ID = "theta-testnet-001"

# Tokens configuration
UATOM_STAKE_INCREASE = 550000000 * 1000000
UATOM_LIQUID_TOKEN_INCREASE = 175000000 * 1000000

THETA_LIQUID_TOKEN_INCREASE = 1000
RHO_LIQUID_TOKEN_INCREASE = 1000
LAMBDA_LIQUID_TOKEN_INCREASE = 1000
EPSILON_LIQUID_TOKEN_INCREASE = 1000

# We'll be swapping the COINBASE validator out
COINBASE_SELF_DELEGATION_ADDR = "cosmos1a3yjj7d3qnx4spgvjcwjq9cw9snrrrhu3rw8nv"
COINBASE_SELF_DELEGATION_PUBKEY = "Ar7QZgBj/ZF6OFqFP5N1M2CoWYdwQcJyVBI/lgOAAaLu"
COINBASE_VALIDATOR_OP_ADDRESS = "cosmosvaloper1a3yjj7d3qnx4spgvjcwjq9cw9snrrrhu5h6jll"

COINBASE_PUBKEY = "NK3/1mb/ToXmxlcyCK8HYyudDn4sttz1sXyyD+42x7I="
COINBASE_ADDRESS = "F8C01C0681578AA700D736D675C9992065F65E3E"
COINBASE_CONS_ADDRESS = "cosmosvalcons1lrqpcp5p2792wqxhxmt8tjveypjlvh378gkddu" 

# We'll be swapping it out with our earth node
EARTH_SELF_DELEGATION_ADDR = "cosmos10v6wvdenee8r9l6wlsphcgur2ltl8ztkvhc8fw"
EARTH_SELF_DELEGATION_PUBKEY = "AsYk9vGihCDVRd8V70Ti7FgVptqunyRv9S22J2XM9njJ"
EARTH_VALIDATOR_OP_ADDRESS = "cosmosvaloper10v6wvdenee8r9l6wlsphcgur2ltl8ztkfrvj9a"

EARTH_PUBKEY = "2j+NkKQHAxu36vduy1sDHJZIeZji7nxnmVIizv07MpE="
EARTH_ADDRESS = "A8A7A64D1F8FFAF2A5332177F777A5816036D65A"
EARTH_CONS_ADDRESS = "cosmosvalcons14zn6vngl3la09ffny9mlwaa9s9srd4j65cqc54" 

PREPROCESSED_FILE = GENESIS_ARCHIVE + ".preprocessed.json"

shutil.copy2(GENESIS_ARCHIVE, PREPROCESSED_FILE)

subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_SELF_DELEGATION_ADDR    + "%" + EARTH_SELF_DELEGATION_ADDR   + "%g",PREPROCESSED_FILE])
subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_SELF_DELEGATION_PUBKEY  + "%" + EARTH_SELF_DELEGATION_PUBKEY + "%g",PREPROCESSED_FILE])
subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_VALIDATOR_OP_ADDRESS    + "%" + EARTH_VALIDATOR_OP_ADDRESS   + "%g",PREPROCESSED_FILE])

subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_PUBKEY       + "%" + EARTH_PUBKEY       + "%g",PREPROCESSED_FILE])
subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_ADDRESS      + "%" + EARTH_ADDRESS      + "%g",PREPROCESSED_FILE])
subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_CONS_ADDRESS + "%" + EARTH_CONS_ADDRESS + "%g",PREPROCESSED_FILE])

genesis = cosmos_genesis_tinker.GenesisTinker(
    default_input=PREPROCESSED_FILE)

if len(sys.argv) == 1:
    genesis.log_help()

print("Tinkering")

genesis.auto_load()

genesis.swap_chain_id(NEW_CHAIN_ID)

genesis.increase_balance(EARTH_SELF_DELEGATION_ADDR,
                         UATOM_LIQUID_TOKEN_INCREASE)
genesis.increase_balance(EARTH_SELF_DELEGATION_ADDR,
                         THETA_LIQUID_TOKEN_INCREASE, "theta")
genesis.increase_balance(EARTH_SELF_DELEGATION_ADDR,
                         RHO_LIQUID_TOKEN_INCREASE, "rho")
genesis.increase_balance(EARTH_SELF_DELEGATION_ADDR,
                         LAMBDA_LIQUID_TOKEN_INCREASE, "lambda")
genesis.increase_balance(EARTH_SELF_DELEGATION_ADDR,
                         EPSILON_LIQUID_TOKEN_INCREASE, "epsilon")

genesis.increase_delegator_stake_to_validator(EARTH_SELF_DELEGATION_ADDR, EARTH_VALIDATOR_OP_ADDRESS, EARTH_ADDRESS, UATOM_STAKE_INCREASE)

# Swap governance parameters for convenience
genesis.swap_min_deposit("1") # 1 uatom
genesis.swap_tally_param("quorum", "0.000000000000000001")
genesis.swap_tally_param("threshold", "0.000000000000000001")
genesis.swap_voting_period("60s")

# Make redelegations faster
genesis.swap_unbonding_time("1s")

print("SHA256SUM:")
print(genesis.generate_shasum())

genesis.auto_save()