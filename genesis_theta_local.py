#!/usr/bin/env python3
"""
HOW TO RUN:
$ ./genesis_theta_local.py --output local_testnet_genesis.json

WHAT THIS SCRIPT DOES:

Genesis modification script for a local testnet for Cosmos Hub theta release.
It consists of a single validator node with priv_validator_key.json:

{
    "address": "D5AB5E458FD9F9964EF50A80451B6F3922E6A4AA",
    "pub_key": {
      "type": "tendermint/PubKeyEd25519",
      "value": "qwiUMxz3llsy45fPvM0a8+XQeAJLvrX3QAEJmRMEEoU="
    },
    "priv_key": {
      "type": "tendermint/PrivKeyEd25519",
      "value": "2yjw8d1QrgB5afmg/UAvvqZ8B9rcaPXVQpqjabvQNVirCJQzHPeWWzLjl8+8zRrz5dB4Aku+tfdAAQmZEwQShQ=="
    }
}

And mnemonic for the validator account: `junk appear guide guess bar reject vendor illegal script sting shock afraid detect ginger other theory relief dress develop core pull across hen float`

Which when recovered, gives this account and keys:

address: cosmos1wvvhhfm387xvfnqshmdaunnpujjrdxznr5d5x9
pubkey: '{"@type":"/cosmos.crypto.secp256k1.PubKey","key":"ApDOUyfcamDmnbEO7O4YKnKQQqQ93+gquLfGf7h5clX7"}'
"""
import sys
import cosmos_genesis_tinker
import subprocess
import shutil

GENESIS_ARCHIVE = "./exported_genesis.json"

NEW_CHAIN_ID = "theta-localnet"

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

# We'll be swapping it out with our own node
LOCAL_SELF_DELEGATION_ADDR = "cosmos1wvvhhfm387xvfnqshmdaunnpujjrdxznr5d5x9"
LOCAL_SELF_DELEGATION_PUBKEY = "ApDOUyfcamDmnbEO7O4YKnKQQqQ93+gquLfGf7h5clX7"
LOCAL_VALIDATOR_OP_ADDRESS = "cosmosvaloper1wvvhhfm387xvfnqshmdaunnpujjrdxznxqep2k"

LOCAL_PUBKEY = "qwiUMxz3llsy45fPvM0a8+XQeAJLvrX3QAEJmRMEEoU="
LOCAL_ADDRESS = "D5AB5E458FD9F9964EF50A80451B6F3922E6A4AA"
LOCAL_CONS_ADDRESS = "cosmosvalcons16k44u3v0m8uevnh4p2qy2xm08y3wdf92xsc3ve" 

PREPROCESSED_FILE = GENESIS_ARCHIVE + ".preprocessed.json"

shutil.copy2(GENESIS_ARCHIVE, PREPROCESSED_FILE)

subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_SELF_DELEGATION_ADDR    + "%" + LOCAL_SELF_DELEGATION_ADDR   + "%g",PREPROCESSED_FILE])
subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_SELF_DELEGATION_PUBKEY  + "%" + LOCAL_SELF_DELEGATION_PUBKEY + "%g",PREPROCESSED_FILE])
subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_VALIDATOR_OP_ADDRESS    + "%" + LOCAL_VALIDATOR_OP_ADDRESS   + "%g",PREPROCESSED_FILE])

subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_PUBKEY       + "%" + LOCAL_PUBKEY       + "%g",PREPROCESSED_FILE])
subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_ADDRESS      + "%" + LOCAL_ADDRESS      + "%g",PREPROCESSED_FILE])
subprocess.call(["sed", "-i", ".bak", "s%" + COINBASE_CONS_ADDRESS + "%" + LOCAL_CONS_ADDRESS + "%g",PREPROCESSED_FILE])

genesis = cosmos_genesis_tinker.GenesisTinker(
    default_input=PREPROCESSED_FILE)

if len(sys.argv) == 1:
    genesis.log_help()

print("Tinkering")

genesis.auto_load()

genesis.swap_chain_id(NEW_CHAIN_ID)

genesis.increase_balance(LOCAL_SELF_DELEGATION_ADDR,
                         UATOM_LIQUID_TOKEN_INCREASE)
genesis.increase_balance(LOCAL_SELF_DELEGATION_ADDR,
                         THETA_LIQUID_TOKEN_INCREASE, "theta")
genesis.increase_balance(LOCAL_SELF_DELEGATION_ADDR,
                         RHO_LIQUID_TOKEN_INCREASE, "rho")
genesis.increase_balance(LOCAL_SELF_DELEGATION_ADDR,
                         LAMBDA_LIQUID_TOKEN_INCREASE, "lambda")
genesis.increase_balance(LOCAL_SELF_DELEGATION_ADDR,
                         EPSILON_LIQUID_TOKEN_INCREASE, "epsilon")

genesis.increase_delegator_stake_to_validator(LOCAL_SELF_DELEGATION_ADDR, LOCAL_VALIDATOR_OP_ADDRESS, LOCAL_ADDRESS, UATOM_STAKE_INCREASE)

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