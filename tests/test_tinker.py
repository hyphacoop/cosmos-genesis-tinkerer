"""
Test all tinkerer features.
python -m pytest -v --genesis fresh
or
python -m pytest -v --genesis stateful
"""

import pytest
import json
import time
import gzip
from functools import partial
from cosmos_genesis_tinker import GenesisTinker, \
    TinkerTaskList, \
    Validator, \
    Delegator


@pytest.fixture
def input_data(genesis_option):
    if genesis_option == 'fresh':
        # Files and genesis
        infile = 'tests/fresh_genesis.json'
        with open(infile, 'r',  encoding='utf8') as genesis_file:
            input_genesis = json.load(genesis_file)
        outfile = 'tests/tinkered_genesis.json'

        # Replace delegator data
        old_del = Delegator()
        old_del.address = 'cosmos1lj54q70v2mt9e7c5mtp5xgg5n9c0hkas60kec9'
        old_del.public_key = 'Aiu5OMUoNnBnWiWOC/Z/Luyq2XFROqubW5oP4Y8y/Lzz'

        # Replace validator data
        old_val = Validator()
        old_val.self_delegation_address = 'cosmos1lj54q70v2mt9e7c5mtp5xgg5n9c0hkas60kec9'
        old_val.self_delegation_public_key = 'Aiu5OMUoNnBnWiWOC/Z/Luyq2XFROqubW5oP4Y8y/Lzz'
        old_val.address = '19CEF0E87C6FBDED2A2A486069C8F4DD51BD3981'
        old_val.public_key = 'T6bqYkfRS1toJAFN8R34MByeuj1siCx0/0GdIgX8SmI='
        old_val.operator_address = 'cosmosvaloper1lj54q70v2mt9e7c5mtp5xgg5n9c0hkaslmzv5k'
        old_val.consensus_address = 'cosmosvalcons1r880p6rud7776232fpsxnj85m4gm6wvpe2pkp2'

        # Increase delegator stake to validator data
        bonded_pool = 'cosmos1fl48vsnmsdzcv85q5d2q4z5ajdha8yu34mf0eh'
        not_bonded_pool = 'cosmos1tygms3xhhs3yv487phx3dw4a95jn7t7lpm470r'
        stake_denom = 'stake'

    elif genesis_option == 'stateful':
        # Files and genesis

        with gzip.open('tests/stateful_genesis.json.gz', 'r') as file:
            content = file.read()
            outfile = open('tests/stateful_genesis.json', 'wb')
            outfile.write(content)
        with open('tests/stateful_genesis.json', 'r', encoding='utf8') as genesis_file:
            input_genesis = json.load(genesis_file)
        infile = 'tests/stateful_genesis.json'
        # with open(infile, 'r',  encoding='utf8') as genesis_file:
        # input_genesis = json.load(genesis_file)
        outfile = 'tests/tinkered_genesis.json'

        # Replace delegator data
        old_del = Delegator()
        old_del.address = 'cosmos1a3yjj7d3qnx4spgvjcwjq9cw9snrrrhu3rw8nv'
        old_del.public_key = 'Ar7QZgBj/ZF6OFqFP5N1M2CoWYdwQcJyVBI/lgOAAaLu'

        # Replace validator data
        old_val = Validator()
        old_val.self_delegation_address = 'cosmos1a3yjj7d3qnx4spgvjcwjq9cw9snrrrhu3rw8nv'
        old_val.self_delegation_public_key = 'Ar7QZgBj/ZF6OFqFP5N1M2CoWYdwQcJyVBI/lgOAAaLu'
        old_val.address = 'F8C01C0681578AA700D736D675C9992065F65E3E'
        old_val.public_key = 'NK3/1mb/ToXmxlcyCK8HYyudDn4sttz1sXyyD+42x7I='
        old_val.operator_address = 'cosmosvaloper1a3yjj7d3qnx4spgvjcwjq9cw9snrrrhu5h6jll'
        old_val.consensus_address = 'cosmosvalcons1lrqpcp5p2792wqxhxmt8tjveypjlvh378gkddu'

        bonded_pool = 'cosmos1fl48vsnmsdzcv85q5d2q4z5ajdha8yu34mf0eh'
        not_bonded_pool = 'cosmos1tygms3xhhs3yv487phx3dw4a95jn7t7lpm470r'
        stake_denom = 'uatom'

    data_dict = {
        'input_file': infile,
        'output_file': outfile,
        'input_genesis': input_genesis,
        'target_delegator': old_del,
        'target_validator': old_val,
        'bonded_pool': bonded_pool,
        'not_bonded_pool': not_bonded_pool,
        'stake_denom': stake_denom
    }
    yield data_dict


def test_task_order(input_data):
    data = input_data
    new_del = Delegator()
    new_del.address = 'cosmos123'
    new_del.public_key = 'key456'
    new_val = Validator()
    new_val.self_delegation_address = 'a'
    new_val.self_delegation_public_key = 'b'
    new_val.address = 'c'
    new_val.public_key = 'd'
    new_val.operator_address = 'e'
    new_val.consensus_address = 'f'

    in_filename = data['input_file']
    out_filename = data['output_file']
    new_name = 'tinkered-chain'

    start_time = time.time()

    gentink = GenesisTinker(input_file=in_filename, output_file=out_filename)
    gentink.add_task(gentink.replace_delegator,
                     old_delegator=data['target_delegator'],
                     new_delegator=new_del)
    gentink.add_task(gentink.set_chain_id, chain_id=new_name)
    gentink.add_task(gentink.replace_validator,
                     old_validator=data['target_validator'],
                     new_validator=new_val)
    sad_result = gentink.run_tasks()
    gentink.clear_tasks()

    gentink2 = GenesisTinker(input_file=in_filename, output_file=out_filename)
    gentink2.add_task(gentink2.replace_delegator,
                      old_delegator=data['target_delegator'],
                      new_delegator=new_del)
    gentink2.add_task(gentink2.replace_validator,
                      old_validator=data['target_validator'],
                      new_validator=new_val)
    gentink2.add_task(gentink2.set_chain_id, chain_id=new_name)
    happy_result = gentink2.run_tasks()

    end_time = time.time()

    assert sad_result
    assert happy_result is None


def test_set_chain_id(input_data):
    data = input_data

    in_filename = data['input_file']
    out_filename = data['output_file']
    new_name = 'tinkered-chain'

    start_time = time.time()

    gentink = GenesisTinker(input_file=in_filename, output_file=out_filename)
    gentink.add_task(gentink.set_chain_id, chain_id=new_name)
    gentink.run_tasks()

    end_time = time.time()
    print(f'Time elapsed: {end_time-start_time:.3f}s', end=' ')

    with open(out_filename, 'r') as new_file:
        new_genesis = json.load(new_file)
    assert new_genesis['chain_id'] == new_name


def test_set_unbonding_time(input_data):
    data = (input_data)

    new_time = '5s'
    in_filename = data['input_file']
    out_filename = data['output_file']
    start_time = time.time()

    gentink = GenesisTinker(input_file=in_filename, output_file=out_filename)
    gentink.add_task(gentink.set_unbonding_time, unbonding_time=new_time)
    gentink.run_tasks()

    end_time = time.time()
    print(f'Time elapsed: {end_time-start_time:.3f}s', end=' ')

    with open(out_filename, 'r') as new_file:
        new_genesis = json.load(new_file)
    assert new_genesis['app_state']['staking']['params']['unbonding_time'] == new_time


def test_governance_functions(input_data):
    """
    Tests the following:
    set_max_deposit_period
    set_min_deposit
    set_tally_param
    """
    data = (input_data)

    in_filename = data['input_file']
    out_filename = data['output_file']
    new_time = '5s'
    new_amount = '1000000'
    new_denom = 'uatom'
    new_params = [{'name': 'quorum', 'value': "0.000000000000000001"},
                  {'name': 'threshold', 'value': "0.000000000000000001"}]
    start_time = time.time()

    gentink = GenesisTinker(input_file=in_filename, output_file=out_filename)
    gentink.add_task(gentink.set_max_deposit_period,
                     max_deposit_period=new_time)
    gentink.add_task(gentink.set_min_deposit,
                     min_amount=new_amount,
                     denom=new_denom)
    for parameter in new_params:
        gentink.add_task(gentink.set_tally_param,
                         parameter_name=parameter['name'],
                         value=parameter['value'])
    gentink.run_tasks()

    end_time = time.time()
    print(f'Time elapsed: {end_time-start_time:.3f}s', end=' ')

    # max_deposit_period
    with open(out_filename, 'r') as new_file:
        new_genesis = json.load(new_file)
    assert new_genesis['app_state']['gov']['deposit_params']['max_deposit_period'] == new_time

    # min_deposit
    min_deps = new_genesis['app_state']['gov']['deposit_params']['min_deposit']
    for deposit in min_deps:
        if deposit['denom'] == new_denom:
            assert deposit['amount'] == new_amount
            break

    # tally_param
    tally_params = new_genesis['app_state']['gov']['tally_params']
    for parameter in new_params:
        assert tally_params[parameter['name']] == parameter['value']


def test_create_coin(input_data):
    data = (input_data)

    in_filename = data['input_file']
    out_filename = data['output_file']
    new_denom = 'myco'
    new_amount = '9000'
    start_time = time.time()

    gentink = GenesisTinker(input_file=in_filename, output_file=out_filename)
    gentink.add_task(gentink.create_coin,
                     denom=new_denom,
                     amount=new_amount)
    gentink.run_tasks()

    end_time = time.time()
    print(f'Time elapsed: {end_time-start_time:.3f}s', end=' ')

    with open(out_filename, 'r') as new_file:
        new_genesis = json.load(new_file)
    supply = new_genesis['app_state']['bank']['supply']
    denoms = [coin['denom'] for coin in supply]
    assert new_denom in denoms
    for coin in supply:
        if coin['denom'] == new_denom:
            assert coin['amount'] == new_amount


def test_replace_delegator(input_data):
    data = (input_data)

    in_filename = data['input_file']
    out_filename = data['output_file']
    old_genesis = data['input_genesis']
    old_del = data['target_delegator']
    new_del = Delegator()
    new_del.address = 'cosmos123'
    new_del.public_key = 'key456'

    start_time = time.time()

    gentink = GenesisTinker(input_file=in_filename, output_file=out_filename)
    gentink.add_task(gentink.replace_delegator,
                     old_delegator=old_del,
                     new_delegator=new_del)

    gentink.run_tasks()
    end_time = time.time()
    print(f'Time elapsed: {end_time-start_time:.3f}s', end=' ')

    with open(out_filename, 'r') as new_file:
        new_genesis = json.load(new_file)

    # Make sure the old delegator does not show anywhere in the new genesis
    # and has been replaced
    # 1. Address would show up in:
    # app_state.auth.accounts where the account has type '/cosmos.auth.v1beta1.BaseAccount
    accounts = old_genesis['app_state']['auth']['accounts']
    base_accounts = [acct['address']
                     for acct in accounts if acct['@type'] == '/cosmos.auth.v1beta1.BaseAccount']

    if old_del.address in base_accounts:
        accounts = new_genesis['app_state']['auth']['accounts']
        base_accounts = [acct['address']
                         for acct in accounts if acct['@type'] == '/cosmos.auth.v1beta1.BaseAccount']
        assert old_del.address not in base_accounts
        assert new_del.address in base_accounts

    # app_state.bank.balances
    balances = old_genesis['app_state']['bank']['balances']
    balance_addrs = [bal['address'] for bal in balances]
    if old_del.address in balance_addrs:
        balances = new_genesis['app_state']['bank']['balances']
        balance_addr = [bal['address'] for bal in balances]
        assert old_del.address not in balance_addr
        assert new_del.address in balance_addr

    # app_state.distribution.delegator_starting_infos
    infos = old_genesis['app_state']['distribution']['delegator_starting_infos']
    info_addrs = [info['delegator_address'] for info in infos]
    if old_del.address in info_addrs:
        infos = new_genesis['app_state']['distribution']['delegator_starting_infos']
        info_addr = [info['delegator_address'] for info in infos]
        assert old_del.address not in info_addr
        assert new_del.address in info_addr

    # app_state.staking.delegations
    dels = old_genesis['app_state']['staking']['delegations']
    del_addrs = [deleg['delegator_address'] for deleg in dels]
    if old_del.address in del_addrs:
        dels = new_genesis['app_state']['staking']['delegations']
        del_addr = [deleg['delegator_address'] for deleg in dels]
        assert old_del.address not in del_addr
        assert new_del.address in del_addr

    # 2. Public key would show up in:
    # app_state.auth.accounts where the account has type '/cosmos.auth.v1beta1.BaseAccount'
    old_accounts = old_genesis['app_state']['auth']['accounts']
    for acct in old_accounts:
        if acct['@type'] == '/cosmos.auth.v1beta1.BaseAccount' \
                and acct['address'] == old_del.address:
            old_del_account = acct
    if old_del_account['pub_key']['key'] == old_del.public_key:
        accounts = new_genesis['app_state']['auth']['accounts']
        for acct in accounts:
            if acct['@type'] == '/cosmos.auth.v1beta1.BaseAccount' \
                    and acct['address'] == new_del.address:
                new_del_account = acct
        assert new_del_account['pub_key']['key'] == new_del.public_key


def test_replace_validator(input_data):
    data = (input_data)

    in_filename = data['input_file']
    out_filename = data['output_file']
    old_genesis = data['input_genesis']
    old_val = data['target_validator']
    new_val = Validator()
    new_val.self_delegation_address = 'a'
    new_val.self_delegation_public_key = 'b'
    new_val.address = 'c'
    new_val.public_key = 'd'
    new_val.operator_address = 'e'
    new_val.consensus_address = 'f'

    start_time = time.time()
    gentink = GenesisTinker(input_file=in_filename, output_file=out_filename)
    gentink.add_task(gentink.replace_validator,
                     old_validator=old_val,
                     new_validator=new_val)
    gentink.run_tasks()
    end_time = time.time()
    print(f'Time elapsed: {end_time-start_time:.3f}s', end=' ')

    # Check results
    with open(out_filename, 'r') as new_file:
        new_genesis = json.load(new_file)

    # Make sure the old validator does not show anywhere in the new genesis
    # and has been replaced
    # 1. Self delegation address would show up in:
    # app_state.auth.accounts where the account has type '/cosmos.auth.v1beta1.BaseAccount'
    accounts = old_genesis['app_state']['auth']['accounts']
    base_accounts = [acct['address']
                     for acct in accounts if acct['@type'] == '/cosmos.auth.v1beta1.BaseAccount']
    if old_val.self_delegation_address in base_accounts:
        accounts = new_genesis['app_state']['auth']['accounts']
        base_accounts = [acct['address']
                         for acct in accounts if acct['@type'] == '/cosmos.auth.v1beta1.BaseAccount']
        assert old_val.self_delegation_address not in base_accounts
        assert new_val.self_delegation_address in base_accounts

    # app_state.bank.balances
    balances = old_genesis['app_state']['bank']['balances']
    balance_addrs = [bal['address'] for bal in balances]
    if old_val.self_delegation_address in balance_addrs:
        balances = new_genesis['app_state']['bank']['balances']
        balance_addr = [bal['address'] for bal in balances]
        assert old_val.self_delegation_address not in balance_addr
        assert new_val.self_delegation_address in balance_addr

    # app_state.distribution.delegator_starting_infos
    infos = old_genesis['app_state']['distribution']['delegator_starting_infos']
    info_addrs = [info['delegator_address'] for info in infos]
    if old_val.self_delegation_address in info_addrs:
        infos = new_genesis['app_state']['distribution']['delegator_starting_infos']
        info_addr = [info['delegator_address'] for info in infos]
        assert old_val.self_delegation_address not in info_addr
        assert new_val.self_delegation_address in info_addr

    # app_state.staking.delegations
    dels = old_genesis['app_state']['staking']['delegations']
    del_addrs = [deleg['delegator_address'] for deleg in dels]
    if old_val.self_delegation_address in del_addrs:
        dels = new_genesis['app_state']['staking']['delegations']
        del_addr = [deleg['delegator_address'] for deleg in dels]
        assert old_val.self_delegation_address not in del_addr
        assert new_val.self_delegation_address in del_addr

    # 2. Self delegation public key would show up in:
    # app_state.auth.accounts where the account has type '/cosmos.auth.v1beta1.BaseAccount'
    old_accounts = old_genesis['app_state']['auth']['accounts']
    for acct in old_accounts:
        if acct['@type'] == '/cosmos.auth.v1beta1.BaseAccount' \
                and acct['address'] == old_val.self_delegation_address:
            old_val_account = acct
    if old_val_account['pub_key']['key'] == old_val.self_delegation_public_key:
        accounts = new_genesis['app_state']['auth']['accounts']
        for acct in accounts:
            if acct['@type'] == '/cosmos.auth.v1beta1.BaseAccount' \
                    and acct['address'] == new_val.self_delegation_address:
                new_val_account = acct
        assert new_val_account['pub_key']['key'] == new_val.self_delegation_public_key

    # 3. Validator address would show up in:
    # validators
    validators = [val['address'] for val in old_genesis['validators']]
    if old_val.address in validators:
        validators = [val['address'] for val in new_genesis['validators']]
        assert old_val.address not in validators
        assert new_val.address in validators

    # 4. Validator public key would show up in:
    # app_state.staking.validators
    validators = [val['consensus_pubkey']['key']
                  for val in old_genesis['app_state']['staking']['validators']]
    if old_val.public_key in validators:
        validators = [val['consensus_pubkey']['key']
                      for val in new_genesis['app_state']['staking']['validators']]
        assert old_val.public_key not in validators
        assert new_val.public_key in validators

    # validators
    validators = [val['pub_key']['value'] for val in old_genesis['validators']]
    if old_val.public_key in validators:
        validators = [val['pub_key']['value']
                      for val in new_genesis['validators']]
        assert old_val.public_key not in validators
        assert new_val.public_key in validators

    # 5. Validator operator address shows up in:
    # app_state.distribution.delegator_starting_infos
    infos = old_genesis['app_state']['distribution']['delegator_starting_infos']
    info_addrs = [info['validator_address'] for info in infos]
    if old_val.operator_address in info_addrs:
        infos = new_genesis['app_state']['distribution']['delegator_starting_infos']
        info_addr = [info['validator_address'] for info in infos]
        assert old_val.operator_address not in info_addr
        assert new_val.operator_address in info_addr

    # app_state.distribution.outstanding_rewards
    rewards = old_genesis['app_state']['distribution']['outstanding_rewards']
    reward_addrs = [reward['validator_address'] for reward in rewards]
    if old_val.operator_address in reward_addrs:
        rewards = new_genesis['app_state']['distribution']['outstanding_rewards']
        reward_addr = [reward['validator_address'] for reward in rewards]
        assert old_val.operator_address not in reward_addr
        assert new_val.operator_address in reward_addr

    # app_state.distribution.validator_accumulated_commissions
    comms = old_genesis['app_state']['distribution']['validator_accumulated_commissions']
    comms_addrs = [comm['validator_address'] for comm in comms]
    if old_val.operator_address in comms_addrs:
        comms = new_genesis['app_state']['distribution']['validator_accumulated_commissions']
        comms_addr = [comm['validator_address'] for comm in comms]
        assert old_val.operator_address not in comms_addr
        assert new_val.operator_address in comms_addr

    # app_state.distribution.validator_accumulated_commissions
    rewards = old_genesis['app_state']['distribution']['validator_current_rewards']
    reward_addrs = [reward['validator_address'] for reward in rewards]
    if old_val.operator_address in reward_addrs:
        rewards = new_genesis['app_state']['distribution']['validator_current_rewards']
        reward_addr = [reward['validator_address'] for reward in rewards]
        assert old_val.operator_address not in reward_addr
        assert new_val.operator_address in reward_addr

    # app_state.distribution.validator_historical_rewards
    rewards = old_genesis['app_state']['distribution']['validator_historical_rewards']
    reward_addrs = [reward['validator_address'] for reward in rewards]
    if old_val.operator_address in reward_addrs:
        rewards = new_genesis['app_state']['distribution']['validator_historical_rewards']
        reward_addr = [reward['validator_address'] for reward in rewards]
        assert old_val.operator_address not in reward_addr
        assert new_val.operator_address in reward_addr

    # app_state.staking.delegations
    dels = old_genesis['app_state']['staking']['delegations']
    delegs = [deleg['validator_address'] for deleg in dels]
    if old_val.operator_address in delegs:
        dels = new_genesis['app_state']['staking']['delegations']
        delegs = [deleg['validator_address'] for deleg in dels]
        assert old_val.operator_address not in delegs
        assert new_val.operator_address in delegs

    # app_state.staking.last_validator_powers
    powers = old_genesis['app_state']['staking']['last_validator_powers']
    validator_powers = [power['address'] for power in powers]
    if old_val.operator_address in validator_powers:
        powers = new_genesis['app_state']['staking']['last_validator_powers']
        val_pows = [power['address'] for power in powers]
        assert old_val.operator_address not in val_pows
        assert new_val.operator_address in val_pows

    # app_state.staking.validators
    vals = old_genesis['app_state']['staking']['validators']
    val_addrs = [val['operator_address'] for val in vals]
    if old_val.operator_address in val_addrs:
        vals = new_genesis['app_state']['staking']['validators']
        val_addr = [val['operator_address'] for val in vals]
        assert old_val.operator_address not in val_addr
        assert new_val.operator_address in val_addr

    # 6. Validator consensus address shows up in:
    # app_state.distribution
    old_previous_proposer = old_genesis['app_state']['distribution']['previous_proposer']
    if old_val.consensus_address == old_previous_proposer:
        previous_proposer = new_genesis['app_state']['distribution']['previous_proposer']
        assert new_val.consensus_address == previous_proposer

    # app_state.slashing.missed_blocks
    missed_blocks = old_genesis['app_state']['slashing']['missed_blocks']
    cons_addrs = [missed['address'] for missed in missed_blocks]
    if old_val.consensus_address in cons_addrs:
        missed_blocks = new_genesis['app_state']['slashing']['missed_blocks']
        cons_addr = [missed['address'] for missed in missed_blocks]
        assert old_val.consensus_address not in cons_addr
        assert new_val.consensus_address in cons_addr

    # app_state.slashing.signing_infos
    infos = old_genesis['app_state']['slashing']['signing_infos']
    signing_addrs = [sign['address'] for sign in infos]
    if old_val.consensus_address in signing_addrs:
        infos = new_genesis['app_state']['slashing']['signing_infos']
        signing_addrs = [sign['address'] for sign in infos]
        assert old_val.consensus_address not in signing_addrs
        assert new_val.consensus_address in signing_addrs

    # app_state.slashing.signing_infos.validator_signing_info
    infos = old_genesis['app_state']['slashing']['signing_infos']
    val_sign_addrs = [sign['validator_signing_info']['address']
                      for sign in infos]
    if old_val.consensus_address in val_sign_addrs:
        infos = new_genesis['app_state']['slashing']['signing_infos']
        val_sign_addrs = [sign['validator_signing_info']['address']
                          for sign in infos]
        assert old_val.consensus_address not in val_sign_addrs
        assert new_val.consensus_address in val_sign_addrs


def test_increase_balance(input_data):
    # Tests increase_supply as well
    data = (input_data)
    in_filename = data['input_file']
    out_filename = data['output_file']
    old_genesis = data['input_genesis']
    address = data['target_delegator'].address
    delta = 1000000  # 1atom
    denom = 'uatom'

    start_time = time.time()

    gentink = GenesisTinker(input_file=in_filename, output_file=out_filename)
    gentink.add_task(gentink.increase_balance,
                     address=address,
                     amount=delta,
                     denom=denom)
    gentink.run_tasks()

    end_time = time.time()
    print(f'Time elapsed: {end_time-start_time:.3f}s', end=' ')

    with open(out_filename, 'r') as new_file:
        new_genesis = json.load(new_file)

    # Get old balance
    balance = 0
    balances = old_genesis['app_state']['bank']['balances']
    if address in [bal['address'] for bal in balances]:
        coins = balances[[balance['address']
                          for balance in balances].index(address)]['coins']
        for coin in coins:
            if coin['denom'] == denom:
                balance = int(coin['amount'])
    # Get new balance
    balances = new_genesis['app_state']['bank']['balances']
    coins = balances[[balance['address']
                      for balance in balances].index(address)]['coins']
    for coin in coins:
        if coin['denom'] == denom:
            new_balance = int(coin['amount'])

    assert new_balance == balance + delta

    # Get old supply
    supply = 0
    coins = old_genesis['app_state']['bank']['supply']
    for coin in coins:
        if coin['denom'] == denom:
            supply = int(coin['amount'])
    # Get new supply
    coins = new_genesis['app_state']['bank']['supply']
    for coin in coins:
        if coin['denom'] == denom:
            new_supply = int(coin['amount'])

    assert new_supply == supply + delta


def test_increase_delegator_stake_to_validator(input_data):
    """
    # Tests the following functions as well:
    increase_balance
    increase_delegator_stake
    increase_validator_stake
    increase_validator_power
    """
    data = (input_data)

    in_filename = data['input_file']
    out_filename = data['output_file']
    old_genesis = data['input_genesis']
    delegator = data['target_delegator'].address
    operator = data['target_validator'].operator_address
    validator = data['target_validator'].address
    bonded_pool = data['bonded_pool']
    not_bonded_pool = data['not_bonded_pool']
    stake_denom = data['stake_denom']
    delta = 1000000
    power_increase = 1

    start_time = time.time()

    gentink = GenesisTinker(input_file=in_filename, output_file=out_filename)
    gentink.bonded_pool_address = bonded_pool
    gentink.not_bonded_pool_address = not_bonded_pool
    gentink.stake_denom = stake_denom
    gentink.add_task(gentink.increase_delegator_stake_to_validator,
                     delegator=data['target_delegator'],
                     validator=data['target_validator'],
                     increase={'amount': delta, 'denom': stake_denom})
    gentink.run_tasks()

    end_time = time.time()
    print(f'Time elapsed: {end_time-start_time:.3f}s', end=' ')

    with open(out_filename, 'r') as new_file:
        new_genesis = json.load(new_file)

    # 1. Confirm increase to bonding pool balance
    accounts = old_genesis['app_state']['bank']['balances']
    bonding_pool_acct = {}
    for acct in accounts:
        if acct['address'] == bonded_pool:
            bonding_pool_acct = acct
            break
    old_balance = 0
    for coin in bonding_pool_acct['coins']:
        if coin['denom'] == stake_denom:
            old_balance = int(coin['amount'])

    accounts = new_genesis['app_state']['bank']['balances']
    bonding_pool_acct = {}
    for acct in accounts:
        if acct['address'] == bonded_pool:
            bonding_pool_acct = acct
            break
    new_balance = 0
    for coin in bonding_pool_acct['coins']:
        if coin['denom'] == stake_denom:
            new_balance = int(coin['amount'])

    assert old_balance + delta == new_balance

    # 2. Confirm increase to delegator stake
    del_info = {}
    old_infos = old_genesis['app_state']['distribution']['delegator_starting_infos']
    for info in old_infos:
        if info['delegator_address'] == delegator:
            old_stake = info['starting_info']['stake']
            break
    new_infos = new_genesis['app_state']['distribution']['delegator_starting_infos']
    for info in new_infos:
        if info['delegator_address'] == delegator:
            new_stake = info['starting_info']['stake']
            break

    assert f'{float(old_stake) + delta:.18f}' == new_stake

    # 3. Confirm increase to validator stake
    validators = old_genesis['app_state']['staking']['validators']
    old_val_data = {}
    for val in validators:
        if val['operator_address'] == operator:
            old_val_data = val
            break

    validators = new_genesis['app_state']['staking']['validators']
    new_val_data = {}
    for val in validators:
        if val['operator_address'] == operator:
            new_val_data = val
            break

    # check the bonding status
    validator_tokens = int(old_val_data['tokens'])
    if old_val_data['status'] == 'BOND_STATUS_UNBONDED':  # NOT TESTED YET
        assert new_val_data['status'] == 'BOND_STATUS_BONDED'
        # check increased balance on bonded pool
        accounts = old_genesis['app_state']['bank']['balances']
        for acct in accounts:
            if acct['address'] == bonded_pool:
                coins = acct['coins']
                for coin in coins:
                    if coin['denom'] == stake_denom:
                        old_bonded_balance = int(coin['amount'])
                        break
            elif acct['address'] == not_bonded_pool:
                coins = acct['coins']
                for coin in coins:
                    if coin['denom'] == stake_denom:
                        old_not_bonded_balance = int(coin['amount'])
                        break
        accounts = new_genesis['app_state']['bank']['balances']
        for acct in accounts:
            if acct['address'] == bonded_pool:
                coins = acct['coins']
                for coin in coins:
                    if coin['denom'] == stake_denom:
                        new_bonded_balance = int(coin['amount'])
                        break
            elif acct['address'] == not_bonded_pool:
                coins = acct['coins']
                for coin in coins:
                    if coin['denom'] == stake_denom:
                        new_not_bonded_balance = int(coin['amount'])
                        break
        assert old_bonded_balance + validator_tokens == new_bonded_balance
        assert old_not_bonded_balance - validator_tokens == new_not_bonded_balance
    # Validator tokens and delegator shares
    new_amount = validator_tokens + delta
    assert new_val_data['tokens'] == str(new_amount)
    old_shares = float(old_val_data["delegator_shares"])
    new_shares = old_shares + delta
    assert new_val_data["delegator_shares"] == \
        str(format(new_shares, ".18f"))

    # 4. Confirm increase to validator power
    validators = old_genesis['validators']
    for val in validators:
        if val['address'] == validator:
            old_power = int(val['power'])
    for val in new_genesis['validators']:
        if val['address'] == validator:
            new_power = int(val['power'])

    assert old_power + power_increase == new_power

    # 5. Confirm delegation is updated
    for deleg in old_genesis['app_state']['staking']['delegations']:
        if deleg['delegator_address'] == delegator and \
                deleg['validator_address'] == operator:
            old_shares = deleg['shares']
    for deleg in new_genesis['app_state']['staking']['delegations']:
        if deleg['delegator_address'] == delegator and \
                deleg['validator_address'] == operator:
            new_shares = deleg['shares']

    assert f'{float(old_shares) + delta:.18f}' == new_shares
