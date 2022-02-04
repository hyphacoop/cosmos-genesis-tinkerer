#!/usr/bin/env python3

import sys
import cosmos_genesis_tinker

if len(sys.argv) == 1:
    print(
        'Usage: ./modify_genesis.py  [new_genesis.json] [exported_genesis.json]')
    # sys.exit(1)

exported_genesis_filename = False
new_genesis_filename = False

if len(sys.argv) > 1:
    new_genesis_filename = sys.argv[1]
if len(sys.argv) > 2:
    exported_genesis_filename = sys.argv[2]

# static values (for now, should be in .json config file)
NODE1_OLD_PUBKEY = "cOQZvh/h9ZioSeUMZB/1Vy1Xo5x2sjrVjlE/qHnYifM="
NODE1_OLD_ADDRESS = "B00A6323737F321EB0B8D59C6FD497A14B60938A"
NODE1_NEW_PUBKEY = "qwiUMxz3llsy45fPvM0a8+XQeAJLvrX3QAEJmRMEEoU="
NODE1_NEW_ADDRESS = "D5AB5E458FD9F9964EF50A80451B6F3922E6A4AA"
NODE1_OLD_COSMOSVALCONS1 = "cosmosvalcons1kq9xxgmn0uepav9c6kwxl4yh599kpyu28e7ee6"
NODE1_NEW_COSMOSVALCONS1 = "cosmosvalcons16k44u3v0m8uevnh4p2qy2xm08y3wdf92xsc3ve"

NODE2_OLD_PUBKEY = "W459Kbdx+LJQ7dLVASW6sAfdqWqNRSXnvc53r9aOx/o="
NODE2_OLD_ADDRESS = "83F47D7747B0F633A6BA0DF49B7DCF61F90AA1B0"
NODE2_NEW_PUBKEY = "oi55Dw+JjLQc4u1WlAS3FsGwh5fd5/N5cP3VOLnZ/H0="
NODE2_NEW_ADDRESS = "7CB07B94FD743E2A8520C2B50DA4B03740643BF5"
NODE2_OLD_COSMOSVALCONS1 = "cosmosvalcons1s0686a68krmr8f46ph6fklw0v8us4gdsm7nhz3"
NODE2_NEW_COSMOSVALCONS1 = "cosmosvalcons10jc8h98awslz4pfqc26smf9sxaqxgwl4vxpcrp"

# user account for delegator (node2)
OLD_DELEGATOR_ADDRESS = "cosmos1qq9ydrjeqalqa3zyqqtdczvuugsjlcc3c7x4d4"
NEW_DELEGATOR_ADDRESS = "cosmos10aak94tfdl3pgt8qe6ga75qh3zkf3anpq8aqg0"
OLD_DELEGATOR_KEY = "AjEkAHzQakRnyUppiM5/hnA6h2D7NkdxExxgiCG+NiDh"
NEW_DELEGATOR_KEY = "A81DhG/5sB6RA8dl/6jtmX0svTc0xJL5NjPPI/q4jJWP"

# binance val
BINANCE_VALIDATOR_ADDRESS = "cosmosvaloper156gqf9837u7d4c4678yt3rl4ls9c5vuursrrzf"
BINANCE_TOKEN_BONDING_POOL = "cosmos1fl48vsnmsdzcv85q5d2q4z5ajdha8yu34mf0eh"

GENESIS_ARCHIVE = "https://github.com/cosmos/vega-test/blob/master/exported_unmodified_genesis.json.gz?raw=true"
GENESIS_SHASUM = "86f29f23f9df51f5c58cb2c2f95e263f96f123801fc9844765f98eca49fe188f"

genesis = cosmos_genesis_tinker.GenesisTinker()

if exported_genesis_filename:
    print("Loading file")
    genesis.load_file(exported_genesis_filename)
else:
    print("Downloading file")
    genesis.load_url(GENESIS_ARCHIVE, GENESIS_SHASUM)

print("Tinkering")

genesis.swap_chain_id("cosmos-genesis-tinker-example")

genesis.swap_validator({
    "pub_key": NODE1_OLD_PUBKEY,
    "address": NODE1_OLD_ADDRESS,
    "consensus_address": NODE1_OLD_COSMOSVALCONS1
}, {
    "pub_key": NODE1_NEW_PUBKEY,
    "address": NODE1_NEW_ADDRESS,
    "consensus_address": NODE1_NEW_COSMOSVALCONS1
})

genesis.swap_validator({
    "pub_key": NODE2_OLD_PUBKEY,
    "address": NODE2_OLD_ADDRESS,
    "consensus_address": NODE2_OLD_COSMOSVALCONS1
}, {
    "pub_key": NODE2_NEW_PUBKEY,
    "address": NODE2_NEW_ADDRESS,
    "consensus_address": NODE2_NEW_COSMOSVALCONS1
})
genesis.swap_delegator(OLD_DELEGATOR_ADDRESS, NEW_DELEGATOR_ADDRESS)

genesis.increase_balance(NEW_DELEGATOR_ADDRESS, 300000000)

STAKE_INCREASE = 6000000000000000
genesis.increase_delegator_stake_to_validator(
    NEW_DELEGATOR_ADDRESS, BINANCE_VALIDATOR_ADDRESS, NODE2_NEW_ADDRESS, STAKE_INCREASE)

print("SHA256SUM:")
print(genesis.generate_shasum())

if new_genesis_filename:
    print("Saving")
    genesis.save_file(new_genesis_filename)
