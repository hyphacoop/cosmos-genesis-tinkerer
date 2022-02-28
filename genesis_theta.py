#!/usr/bin/env python3

# NOTE: these replacements don't quite work and are WIP. See genesis_theta_local.py for local testnet instructions.
# Addresses
# hy-hydrogen self-delegation account cosmos1lapm2cq4qjrl4fm5xcftfhg245m63d30mswfjp
# hy-hydrogen operator address cosmosvaloper1lapm2cq4qjrl4fm5xcftfhg245m63d307y6u7j
# Modifications
# 1. change the chain-id to theta-testnet
# 2. add tokens to the hy-hydrogen self-delegation account

"""
  "name" = "hy-hydrogen"
  "address": "E5C2AF993220B200C1C86E83BBE06A35F960B829",
  "pub_key": {
    "type": "tendermint/PubKeyEd25519",
    "value": "1Lt+cRGXjtRDlQSoQ+DPWj/GNYOzl+0U+7BFAvruu5s="
  }
"""

import sys
import cosmos_genesis_tinker

# static values (for now, should be in .json config file)
NEW_CHAIN_ID = "theta-testnet"
HYDROGEN_SELF_DELEGATION_ADDR = "cosmos1lapm2cq4qjrl4fm5xcftfhg245m63d30mswfjp"
HYDROGEN_VAL_OP = "cosmosvaloper1lapm2cq4qjrl4fm5xcftfhg245m63d307y6u7j"
HYDROGEN_VAL_ADDR = "E5C2AF993220B200C1C86E83BBE06A35F960B829"
HYDROGEN_CONS_ADDR = "cosmosvalcons1uhp2lxfjyzeqpswgd6pmhcr2xhukpwpfheam88" 

# Note that you can get the consensus addr by `gaiad keys parse $HYDROGEN_VAL_ADDR`

GENESIS_ARCHIVE = "./exported_genesis.json"
GENESIS_SHASUM = "3b541c005dfd79e7286630281422f95465cee8e89f2dce09119bdfb1b61850b0"

UATOM_STAKE_INCREASE = 550000000 * 1000000
UATOM_LIQUID_TOKEN_INCREASE = 175000000 * 1000000

THETA_LIQUID_TOKEN_INCREASE = 1000
RHO_LIQUID_TOKEN_INCREASE = 1000
LAMBDA_LIQUID_TOKEN_INCREASE = 1000
EPSILON_LIQUID_TOKEN_INCREASE = 1000

genesis = cosmos_genesis_tinker.GenesisTinker(
    default_input=GENESIS_ARCHIVE, default_shasum=GENESIS_SHASUM)

if len(sys.argv) == 1:
    genesis.log_help()

print("Tinkering")

genesis.auto_load()

genesis.swap_chain_id(NEW_CHAIN_ID)

genesis.increase_balance(HYDROGEN_SELF_DELEGATION_ADDR,
                         UATOM_LIQUID_TOKEN_INCREASE)
genesis.increase_balance(HYDROGEN_SELF_DELEGATION_ADDR,
                         THETA_LIQUID_TOKEN_INCREASE, "theta")
genesis.increase_balance(HYDROGEN_SELF_DELEGATION_ADDR,
                         RHO_LIQUID_TOKEN_INCREASE, "rho")
genesis.increase_balance(HYDROGEN_SELF_DELEGATION_ADDR,
                         LAMBDA_LIQUID_TOKEN_INCREASE, "lambda")
genesis.increase_balance(HYDROGEN_SELF_DELEGATION_ADDR,
                         EPSILON_LIQUID_TOKEN_INCREASE, "epsilon")

genesis.increase_delegator_stake_to_validator(
    HYDROGEN_SELF_DELEGATION_ADDR, HYDROGEN_VAL_OP, HYDROGEN_VAL_ADDR, UATOM_STAKE_INCREASE)

print("SHA256SUM:")
print(genesis.generate_shasum())

if not genesis.auto_save():
    print('Not saving')
