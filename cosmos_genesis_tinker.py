#!/usr/bin/env python3

"""
This module helps you configure Cosmos Chain genesis files for testnets.
TODO: Docs for how to get a genesis file
"""

import json
from hashlib import sha256
from zipfile import ZipFile
from io import BytesIO
import argparse
import gzip
import tarfile
import requests
import bisect

# Default value is the cosmoshub-4 bonded token pool account
TOKEN_BONDING_POOL_ADDRESS = "cosmos1fl48vsnmsdzcv85q5d2q4z5ajdha8yu34mf0eh"
NOT_BONDED_TOKENS_POOL_ADDRESS = "cosmos1tygms3xhhs3yv487phx3dw4a95jn7t7lpm470r"

DEFAULT_POWER = 6000000000
POWER_TO_TOKENS = 1000000
DEFAULT_NAME = "hy-hydrogen"
DEFAULT_PUBKEY = "1Lt+cRGXjtRDlQSoQ+DPWj/GNYOzl+0U+7BFAvruu5s="


def _swap_address_in_list(old_address, new_address, validators):
    found_validator = False
    for validator in validators:
        if validator["address"] == old_address:
            validator["address"] = new_address
            found_validator = True
            break

    if not found_validator:
        raise Exception("Could not find validator address")


class GenesisTinker:  # pylint: disable=R0904
    """
    This class gives you primitives for tinkering with Cosmos chain Genesis Files
    """
    genesis = {}
    should_log_steps = True
    __step_count = 0
    argparse = argparse.ArgumentParser(
        description="Load and modify a cosmos genesis file")

    def __init__(self, default_input=None, default_shasum=None, default_output=None):
        self.argparse.add_argument(
            '--input', help="file path or HTTPS URL to the genesis file", default=default_input)
        self.argparse.add_argument(
            '--shasum', help="for verifying the genesis file on download", default=default_shasum)
        self.argparse.add_argument(
            '--output', help="path for the final genesis file", default=default_output)

        self.args = self.argparse.parse_args()

    def get_app_state(self):
        """
        Get the app state from the genesis file
        """
        return self.genesis["app_state"]

    app_state = property(get_app_state)

    def get_gov(self):
        """
        Get the governance module state from the genesis file
        """
        return self.app_state["gov"]

    gov = property(get_gov)

    def get_validators(self):
        """
        Get the list of validators from the genesis file
        """
        return self.genesis["validators"]

    validators = property(get_validators)

    def log_help(self):
        """
        Log help message to the console if the --help flag wasn't set
        """
        if 'help' not in self.args:
            self.argparse.print_help()

    def log_step(self, message):
        """
        Log a message about the current steps.
        Automatically increments the step_count
        """

        if not self.should_log_steps:
            return -1

        self.__step_count += 1
        step_count = str(self.__step_count)
        print(step_count + ". " + message)

        return step_count

    def load_file(self, path):
        """
        Loads a genesis file from the given path
        """

        self.log_step("Loading genesis from file " + path)

        with open(path, "r", encoding="utf8") as file:
            self.genesis = json.load(file)

        return self

    def load_url(self, url, shasum=None):
        """
        Download and parse a genesis file from the web.
        Optionally specify a sha256 sum to verify the data integrity
        The genesis file can also be stored in a zip file under `genesis.json`
        """

        log_string = "Loading genesis from URL " + url

        if shasum:
            log_string += " with shasum " + shasum

        self.log_step(log_string)

        request = requests.get(url, allow_redirects=True, stream=True)

        # Auto-read from zipfiles
        if '.tar.gz' in url:
            with tarfile.open(fileobj=request.raw, mode='r|gz') as archive:
                archive.list()
                with archive.extractfile('genesis.json') as file:
                    content = file.read()
        elif '.gz' in url:
            with gzip.open(request.raw, 'r') as file:
                content = file.read()
        elif '.zip' in url:
            with ZipFile(BytesIO(request.content), 'r') as archive:
                with archive.open('genesis.json', 'r') as file:
                    content = file.read()
        else:
            content = request.content

        if shasum is not None:
            got_digest = sha256(content).hexdigest()
            if got_digest != shasum:
                raise Exception(
                    "Got invalid digest from remote file", got_digest, shasum)

        self.genesis = json.loads(content)

        return self

    def auto_load(self):
        """
        Attempts to load the genesis file from CLI arguments
        --input CLI flag can be used to specify either a file path or URL
        --shasum CLI fla gcan be used to specify a shasum to verify against
        """

        input_name = self.args.input
        shasum = self.args.shasum

        if input_name is None:
            raise Exception(
                'Unable to load genesis file, please specify the --input flag')

        self.log_step('Autoloading ' + input_name)

        if input_name.startswith('http://') or input_name.startswith('https://'):
            return self.load_url(input_name, shasum)

        return self.load_file(input_name)

    def auto_save(self):
        """
        Attempts to save the genesis file if the --output CLI arg has been specified
        """

        output_name = self.args.output

        if output_name is not None:
            self.log_step("Saving genesis file to " + output_name)
            return self.save_file(output_name)

        return False

    def generate_json(self):
        """
        Generates the JSON for the current genesis state
        """
        return json.dumps(self.genesis, indent=False)

    def generate_shasum(self):
        """
        Generates a sha256 checksum of the genesis file (to verify later)
        """
        content = self.generate_json()
        content_bytes = content.encode('utf-8')
        return sha256(content_bytes).hexdigest()

    def save_file(self, path):
        """
        Save a modified genesis file back to JSON
        """

        self.log_step("Saving genesis to file " + path)

        with open(path, "w", encoding="utf8") as file:
            json.dump(self.genesis, file, indent=False)

        return self

    def swap_max_deposit_period(self, max_deposit_period="1209600s"):
        """
        Swapping governance max_deposit_period
        """

        self.log_step(
            "Swapping governance max deposit period to " + max_deposit_period)

        deposit_params = self.gov["deposit_params"]
        deposit_params["max_deposit_period"] = max_deposit_period

        return self

    def swap_min_deposit(self, min_amount="64000000", denom="uatom"):
        """
        Swap out the min deposit amount for governance.
        Creates a new amount if the denomination doesn't exist
        """

        self.log_step(
            "Swapping min governance deposit amount to " + min_amount + denom)

        deposit_params = self.gov['deposit_params']
        min_deposit = deposit_params['min_deposit']

        has_found_deposit_denom = False

        for deposit in min_deposit:
            if deposit["denom"] == denom:
                has_found_deposit_denom = True
                deposit["amount"] = min_amount

        if not has_found_deposit_denom:
            self.log_step(
                "Adding new deposit denomination since " + denom + " was not found")
            min_deposit.append({"amount": min_amount, "denom": denom})

        return self

    def swap_tally_param(self, parameter_name, value):
        """
        Swap out tally parameters.
        parameter_name should be one of "quorum", "threshold", "veto_threshold"
        """

        self.log_step("Swapping tally parameter " +
                      parameter_name + " to " + value)

        self.gov["tally_params"][parameter_name] = value

        return self

    def swap_voting_period(self, voting_period="1209600s"):
        """
        Swap out the voting period for the governance module
        """

        self.log_step("Swapping governance voting period to " + voting_period)

        self.gov["voting_params"] = voting_period

        return self

    def swap_chain_id(self, chain_id):
        """
        Swap the chain ID with your own name
        """

        self.log_step("Swapping chain id to " + chain_id)

        self.genesis["chain_id"] = chain_id

        return self

    def swap_validator(self, old, new):
        """
        Swaps out an existing validator with a new one

        `old` and `new` should contain the properties `pub_key`, `address`, and `consensus_address`
        e.g.

        old = {
            "pub_key" : "Whatever",
            "address": "Something",
            "consensus_address": "cosmosvalcon..."
        }
        """

        self.log_step("Swapping validator " + str(old) + " to " + str(new))

        staking_validators = self.app_state["staking"]["validators"]
        validators = self.validators
        missed_blocks = self.app_state["slashing"]["missed_blocks"]
        signing_infos = self.app_state["slashing"]["signing_infos"]

        found_validator = False
        for validator in validators:
            if validator["pub_key"]["value"] == old["pub_key"]:
                found_validator = True
                validator["pub_key"]["value"] = new["pub_key"]
                if validator["address"] != old["address"]:
                    raise Exception(
                        "Old address doesn't match old pub key")
                validator["address"] = new["address"]
                break

        if not found_validator:
            raise Exception("Could not find validator")

        found_validator = False
        for validator in staking_validators:
            if validator["consensus_pubkey"]["key"] == old["pub_key"]:
                validator["consensus_pubkey"]["key"] = new["pub_key"]
                found_validator = True
                break

        if not found_validator:
            raise Exception("Could not find validator staking")

        old_consensus_address = old["consensus_address"]
        new_consensus_address = new["consensus_address"]

        _swap_address_in_list(
            old_consensus_address, new_consensus_address, missed_blocks)
        _swap_address_in_list(
            old_consensus_address, new_consensus_address, signing_infos)

        return self

    def swap_delegator(self, old_address, new_address):
        """
        Swaps out an exsiting delegator with a new one
        """

        self.log_step("Swapping delegator address " +
                      old_address + " to " + new_address)

        accounts = self.app_state["auth"]["accounts"]
        balances = self.app_state["bank"]["balances"]
        delegations = self.app_state["staking"]["delegations"]
        starting_infos = self.app_state["distribution"]["delegator_starting_infos"]

        found_account = False
        for account in accounts:
            try:
                if account["address"] == old_address:
                    account["address"] = new_address
                    found_account = True
                    break
            except KeyError:
                pass

        if not found_account:
            raise Exception("Could not find old account address")

        found_balance = False
        for balance in balances:
            if balance["address"] == old_address:
                balance["address"] = new_address
                found_balance = True
                break

        if not found_balance:
            raise Exception('Could not find old balance')

        found_delegation = False
        for delegation in delegations:
            if delegation["delegator_address"] == old_address:
                delegation["delegator_address"] = new_address
                found_delegation = True
                break

        if not found_delegation:
            raise Exception("Could not find old delegator stake")

        for info in starting_infos:
            if info["delegator_address"] == old_address:
                info["delegator_address"] = new_address
                break

        return self

    def create_coin(self, denom, amount="0"):
        """
        Creates a new coin based on a given name if it doesn't exist
        """

        self.log_step("Creating new coin " + denom +
                      " valued at " + str(amount))

        supplies = self.app_state["bank"]["supply"]

        for supply in supplies:
            if supply['denom'] == denom:
                # Already exists, so we don't need to add it
                return self

        # coins must be in ascending sorted order by denom
        bisect.insort_right(supplies, {"denom": denom, "amount": str(amount)}, key=lambda x: x.get("denom")) 
        return self

    def increase_balance(self, address, increase=300000000, denom="uatom"):
        """
        Increases the balance of a person and also the overall supply of uatom
        """

        self.log_step("Increasing balance of " + address +
                      " by " + str(increase) + " " + denom)

        balances = self.app_state["bank"]["balances"]

        found_balance = False
        for balance in balances:
            if balance["address"] == address:
                found_balance = True
                had_coin = False
                for coin in balance["coins"]:
                    if coin["denom"] == denom:
                        old_amount = int(coin["amount"])
                        new_amount = old_amount + increase
                        coin["amount"] = str(new_amount)
                        had_coin = True
                        break
                if not had_coin:
                    # coins must be in ascending sorted order by denom
                    bisect.insort_right(balance["coins"], {"denom": denom, "amount": str(increase)}, key=lambda x: x.get("denom")) 
                break

        if not found_balance:
            raise Exception('Could not find balance for address')

        self.increase_supply(increase, denom)
        return self

    def increase_supply(self, increase, denom="uatom"):
        """
        Increase the total supply of coins of a given denomination
        """

        self.log_step("Increasing supply of " + denom + " by " + str(increase))

        supplies = self.app_state["bank"]["supply"]

        found_coin = False
        for coin in supplies:
            if coin["denom"] == denom:
                old_amount = int(coin["amount"])
                new_amount = old_amount + increase
                coin["amount"] = str(new_amount)
                found_coin = True
                break

        if not found_coin:
            self.create_coin(denom, increase)

        return self

    def increase_validator_power(self, validator_address, power_increase=DEFAULT_POWER, name=DEFAULT_NAME, pub_key=DEFAULT_PUBKEY):
        """
        Increase the staking power of a validator
        Also increases the last total power value

        If validator isn't found in genesis["validators"],
        it doesn't exist in the validator set of top 150 validators
        by voting power. In that case, if the voting power increase
        is larger than the smallest validator by voting power,
        replace the smallest validator

        validators in the genesis["validators"] looks like this:
        {
            'address': 'EBED694E6CE1224FB1E8A2DD8EE63A38568B1E2B',
            'name': 'Umbrella ☔',
            'power': '471680',
            'pub_key':
                {
                    'type': 'tendermint/PubKeyEd25519',
                    'value': 'z/Dg9WU/rlIB+LaQVMMHW/a7rvalfIcyz3VdOwfvguc='
                }
        }
        """

        self.log_step("Increasing validator power of " +
                      validator_address + " by " + str(power_increase))

        validators = self.validators

        found_validator = False
        smallest_validator_index = 0
        smallest_validator_power = int(
            validators[smallest_validator_index]["power"])
        last_total_power = int(
            self.app_state['staking']['last_total_power'])

        for index, validator in enumerate(validators):
            if validator["address"] == validator_address:
                old_power = int(validator["power"])
                new_power = old_power + power_increase
                validator["power"] = str(int(new_power))
                found_validator = True
            if int(validator["power"]) < smallest_validator_power:
                smallest_validator_index = index
                smallest_validator_power = int(validator["power"])

        if not found_validator:
            if smallest_validator_power < power_increase:
                self.log_step("Adding validator to validator set")
                # INSERT NEW VALIDATOR
                self.app_state['staking']['params']['max_validators'] = int(self.app_state['staking']['params']['max_validators'] + 1)
                validators.append({ "address": validator_address,
                    "name": name,
                    "power": str(power_increase),
                    "pub_key": {
                        "type": "tendermint/PubKeyEd25519",
                        "value": pub_key
                    }
                })
                new_last_total_power = last_total_power + power_increase
                # REPLACE SMALLEST VALIDATOR
                #  validators[smallest_validator_index]["power"] = str(
                #    power_increase)
                # validators[smallest_validator_index]["address"] = validator_address
                # validators[smallest_validator_index]["pub_key"]["value"] = pub_key
                # validators[smallest_validator_index]["name"] = name
                # new_last_total_power = last_total_power + \
                #    power_increase - smallest_validator_power
            else:
                raise Exception(
                    'Could not add validator to validator set due to low power')
        else:
            new_last_total_power = last_total_power + power_increase

        self.app_state["staking"]["last_total_power"] = str(
            new_last_total_power)

        return self

    def increase_validator_stake(self, operator_address, increase=DEFAULT_POWER*POWER_TO_TOKENS):
        """
        Increases the stake of a validator as well as its delegator_shares
        """

        self.log_step("Increasing validator stake of " +
                      operator_address + " by " + str(increase))

        staking_validators = self.app_state["staking"]["validators"]

        found_validator = False
        for validator in staking_validators:
            if validator["operator_address"] == operator_address:
                old_amount = int(validator["tokens"])
                if validator["status"] == "BOND_STATUS_UNBONDED":
                    validator["status"] = "BOND_STATUS_BONDED"
                    self.increase_balance(TOKEN_BONDING_POOL_ADDRESS, old_amount)
                    self.increase_balance(NOT_BONDED_TOKENS_POOL_ADDRESS, -1*old_amount)
                new_amount = old_amount + increase
                validator["tokens"] = str(new_amount)
                old_shares = float(validator["delegator_shares"])
                new_shares = old_shares + increase
                validator["delegator_shares"] = str(
                    format(new_shares, ".18f"))

                found_validator = True
                break

        if not found_validator:
            raise Exception("Could not find operator_address")

        return self

    def increase_delegator_stake(self, delegator_address, increase=DEFAULT_POWER*POWER_TO_TOKENS):
        """
        Increases the stake for a delegator
        """

        self.log_step("Increasing delegator stake of " +
                      delegator_address + " by " + str(increase))

        starting_infos = self.app_state["distribution"]["delegator_starting_infos"]

        found_stake = False
        for info in starting_infos:
            if info["delegator_address"] == delegator_address:
                old_stake = float(info["starting_info"]["stake"])
                new_stake = old_stake + increase
                info["starting_info"]["stake"] = str(
                    format(new_stake, ".18f"))
                found_stake = True
                break

        if not found_stake:
            raise Exception("Unable to find delegator_address")

        return self

    def increase_delegator_stake_to_validator(self, delegator, operator_address, validator_address, stake, power_to_tokens=POWER_TO_TOKENS, token_bonding_pool_address=TOKEN_BONDING_POOL_ADDRESS):  # pylint: disable=C0301
        """
        Increase a delegator's stake to a validator.
        Includes increasing token bonding pool balance and validator power
        """

        self.increase_balance(token_bonding_pool_address, stake)
        self.increase_delegator_stake(delegator, stake)
        self.increase_validator_stake(operator_address, stake)
        self.increase_validator_power(
            validator_address, int(stake/power_to_tokens))

        return self
