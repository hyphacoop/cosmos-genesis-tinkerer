"""
Genesis Tinker

This module provides an interface for modifying Cosmos genesis files.

1. Create a Genesis Tinker object specifying input and output files
2. Create Delegator and Validator objects as required
2. Add tasks
3. Run tasks
4. The specified output file will have the new configuration

See fresh_genesis_tinker.py for an example.
"""

import json
from hashlib import sha256
from zipfile import ZipFile
from io import BytesIO
import gzip
import tarfile
import functools
import bisect
import shutil
import subprocess
import os
import requests


class Validator:
    """
    Provides access functions for details
    associated with a validator:
    Self-delegation address
    Self-delegation public key
    Validator address
    Validator public key
    Validator operator address
    Validator consensus address
    """

    def __init__(self):
        """
        Initializes all attributes to None
        """
        self._self_del_addr = None
        self._self_del_pub = None
        self._addr = None
        self._pub = None
        self._oper_addr = None
        self._cons_addr = None

    @property
    def self_delegation_address(self):
        """
        Getter function for self_delegation_address
        """
        return self._self_del_addr

    @self_delegation_address.setter
    def self_delegation_address(self, addr):
        self._self_del_addr = addr

    @property
    def self_delegation_public_key(self):
        """
        Getter function for self_delegation_public_key
        """
        return self._self_del_pub

    @self_delegation_public_key.setter
    def self_delegation_public_key(self, pub):
        self._self_del_pub = pub

    @property
    def address(self):
        """
        Getter function for address
        """
        return self._addr

    @address.setter
    def address(self, addr):
        self._addr = addr

    @property
    def public_key(self):
        """
        Getter function for public_key
        """
        return self._pub

    @public_key.setter
    def public_key(self, pub):
        self._pub = pub

    @property
    def operator_address(self):
        """
        Getter function for operator_address
        """
        return self._oper_addr

    @operator_address.setter
    def operator_address(self, addr):
        self._oper_addr = addr

    @property
    def consensus_address(self):
        """
        Getter function for consensus_address
        """
        return self._cons_addr

    @consensus_address.setter
    def consensus_address(self, addr):
        self._cons_addr = addr


class Delegator:
    """
    Provides access functions for details
    associated with a delegator:
    Public key
    Address
    """

    def __init__(self):
        """
        Initializes all attributes to None
        """
        self._addr = None
        self._pub = None

    @property
    def address(self):
        """
        Getter function for address
        """
        return self._addr

    @address.setter
    def address(self, addr):
        self._addr = addr

    @property
    def public_key(self):
        """
        Getter function for public_key
        """
        return self._pub

    @public_key.setter
    def public_key(self, pub):
        self._pub = pub


class TinkerTaskList:
    """
    Provides access functions to the tasks to be performed:
    add
    tasks
    next
    """
    _bytes_tasks = []
    _json_tasks = []
    _bytes_tasks_names = ('replace_validator', 'replace_delegator')
    _phase = 'bytes'
    _user_tasks = []

    def add(self, task):
        """
        Adds task to one of these two lists:
        self._bytes_tasks if the task is in self._bytes_tasks_names
        self._json_tasks otherwise
        """
        self._user_tasks.append(task)
        if task.func.__name__ in self._bytes_tasks_names:
            self._bytes_tasks.append(task)
        else:
            self._json_tasks.append(task)

    def user_tasks(self):
        """
        Returns the tasks in the order submitted by the user
        """
        return self._user_tasks

    def tasks(self):
        """
        Returns the full task list
        """
        return self._bytes_tasks + self._json_tasks

    def next(self):
        """
        Returns the next task in the queue
        It sets the phase to json every time
        it returns a json task.
        """
        if len(self._bytes_tasks) > 0:
            return self._bytes_tasks.pop(0)
        if len(self._json_tasks) > 0:
            self._phase = 'json'
            return self._json_tasks.pop(0)
        return None

    def phase(self):
        """
        Getter function for phase
        """
        return self._phase

    def clear(self):
        """
        Resets the task lists and phase
        """
        self._user_tasks = []
        self._bytes_tasks = []
        self._json_tasks = []
        self._phase = 'bytes'


class GenesisTinker:  # pylint: disable=R0902,R0904
    """
    Provides primitives for modifying Cosmos genesis files
    """
    genesis = {}
    _task_list = TinkerTaskList()
    _step_count = 0
    _phase = 'bytes'
    _preprocessing = False

    def __init__(self,
                 input_file: str = "genesis.json",
                 shasum: str = "",
                 output_file: str = "tinkered_genesis.json",
                 preprocessing_file: str = "preprocessing.json"):
        self.input_file = input_file
        self.shasum = shasum
        self.output_file = output_file
        self.preprocessing_file = preprocessing_file

    @property
    def app_state(self):
        """
        Get the app state from the loaded genesis file
        """
        return self.genesis["app_state"]

    @property
    def gov(self):
        """
        Get the governance module state from the loaded genesis file
        """
        return self.app_state["gov"]

    @property
    def validators(self):
        """
        Get the list of validators from the loaded genesis file
        """
        return self.genesis["validators"]

    def log_step(self, message):
        """
        Log a message about the current steps.
        Automatically increments the step_count
        """
        self._step_count += 1
        step_count = str(self._step_count)
        print(step_count + ". " + message)

        return step_count

    def add_task(self, new_task, **kwargs):
        """
        When a task is added, we check whether it's a
        - string replacement
        - json structure change
        and append it to the relevant queue.
        """
        self._task_list.add(functools.partial(new_task, **kwargs))

    def tasks(self):
        """
        Return task list from TinkerTaskList object
        """
        return self._task_list.tasks()

    def clear_tasks(self):
        """
        Clear all lists in the TinkerTaskList object
        """
        self._task_list.clear()

    def run_tasks(self):
        """
        Run the list of tasks:
        - All byte operations are done before the json ones
        - All byte operations are done on a the pre-processing
        """

        if self._task_list.tasks() != self._task_list.user_tasks():
            print('Invalid sequence: replace_validator and replace_delegator '
                  'must come before all other functions.')
            print('Expected order:', str(
                [task.func.__name__ for task in self._task_list.tasks()]))
            return True

        while self._task_list.tasks():
            task = self._task_list.next()
            if self._task_list.phase() == 'json' and self._phase == 'bytes':
                # load json only if required
                self._phase = 'json'
                self.auto_load()
            task()

        self._task_list.clear()

        if self._phase == 'json':
            self.save_file(self.output_file)
            content = self.generate_json()
            content_bytes = content.encode('utf-8')
        else:
            shutil.copy2(self.preprocessing_file, self.output_file)
            with open(self.preprocessing_file, 'rb') as infile:
                content_bytes = infile.read()

        print(f'SHA256SUM: {sha256(content_bytes).hexdigest()}')

    def create_preprocessing_file(self):
        """
        Creates a preprocessing json file in which
        all byte replacement operations will take place.
        """
        self.log_step("Creating preprocessing file " +
                      self.preprocessing_file)
        self._preprocessing = True
        subprocess.run(f"jq '.' {self.input_file} > {self.preprocessing_file}",
                check=True, shell=True)
        # shutil.copy2(self.input_file, self.preprocessing_file)

    def replace_delegator(self, old_delegator: Delegator, new_delegator: Delegator):
        """
        Replace an existing delegator with the specified one.
        old_delegator and new_delegator must be Delegator objects

        This function will do a byte replacement on all instances of the old delegator data
        and save the changes to the current pre_processing.json file.
        """
        if not self._preprocessing:
            self.create_preprocessing_file()

        self.log_step("Replacing delegator " + old_delegator.address +
                      " with " + new_delegator.address)
        # Replace every property of the delegator object
        properties = [prop for prop in dir(Delegator) if prop[0] != '_']

        for prop in properties:
            subprocess.run([
                'sed', '-i', 's%' +
                getattr(old_delegator, prop) + '%' +
                getattr(new_delegator, prop) + '%g',
                self.preprocessing_file],
                check=True)

    def replace_validator(self, old_validator: Validator, new_validator: Validator):
        """
        Replace an existing validator with the specified one.
        old_validator and new_validator must be Validator objects

        This function will do a byte replacement on all instances of the old validator data
        and save the changes to the current pre_processing.json file.
        """
        if not self._preprocessing:
            self.create_preprocessing_file()

        self.log_step("Replacing validator " + old_validator.address +
                      " with " + new_validator.address)

        # Replace every property of the validator object
        properties = [prop for prop in dir(Validator) if prop[0] != '_']

        for prop in properties:
            subprocess.run([
                'sed', '-i', 's%' +
                getattr(old_validator, prop) + '%' +
                getattr(new_validator, prop) + '%g',
                self.preprocessing_file],
                check=True)

        # Sort coins in bank balances
        self.log_step("Sorting balances coins")
        subprocess.run(f"jq '.app_state.bank.balances |= map(.coins |= sort_by(.denom))' {self.preprocessing_file} > sorted.json",
                check=True, shell=True)
        subprocess.run(f"mv sorted.json {self.preprocessing_file}",
                check=True, shell=True)

    def load_file(self, path):
        """
        Loads a genesis file from the given path
        """

        self.log_step("Loading genesis from file " + path)

        with open(path, "r", encoding="utf8") as file:
            self.genesis = json.load(file)

        if os.path.isfile(self.preprocessing_file):
            os.remove(self.preprocessing_file)

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
        _phase = 'json'

        return self

    def auto_load(self):
        """
        Attempts to load the genesis file from CLI arguments
        --input CLI flag can be used to specify either a file path or URL
        --shasum CLI fla gcan be used to specify a shasum to verify against
        """

        if self._preprocessing:
            input_name = self.preprocessing_file
        else:
            input_name = self.input_file
            shasum = self.shasum

        if input_name is None:
            raise Exception(
                'Unable to load genesis file, please specify the --input flag')

        self.log_step('Autoloading ' + input_name)

        if input_name.startswith('http://') or input_name.startswith('https://'):
            return self.load_url(input_name, shasum)

        return self.load_file(input_name)

    def generate_json(self):
        """
        Generates the JSON for the current genesis state
        """
        return json.dumps(self.genesis, indent=False)

    def save_file(self, path):
        """
        Save a modified genesis file back to JSON
        """

        self.log_step("Saving genesis to file " + path)

        with open(path, "w", encoding="utf8") as file:
            json.dump(self.genesis, file, indent=False)

        return self

    def generate_shasum(self):
        """
        Generates a sha256 checksum of the genesis file (to verify later)
        """
        content = self.generate_json()
        content_bytes = content.encode('utf-8')
        return sha256(content_bytes).hexdigest()

    def get_bonded_pool_address(self):
        """
        Look through .app_state.auth.accounts,
        check for "name": "bonded_tokens_pool"
        and return the address.
        """
        accounts = self.genesis['app_state']['auth']['accounts']
        for acct in accounts:
            if 'name' in acct.keys() and acct['name'] == 'bonded_tokens_pool':
                return acct['base_account']['address']
        return None

    def get_not_bonded_pool_address(self):
        """
        Look through .app_state.auth.accounts,
        check for "name": "not_bonded_tokens_pool"
        and return the address.
        """
        accounts = self.genesis['app_state']['auth']['accounts']
        for acct in accounts:
            if 'name' in acct.keys() and acct['name'] == 'not_bonded_tokens_pool':
                return acct['base_account']['address']
        return None

    def set_chain_id(self, chain_id: str):
        """
        Swap the chain ID with your own name
        """

        self.log_step(f'Changing chain id from \"{self.genesis["chain_id"]}\" to '
                      f'"{chain_id}"')

        self.genesis["chain_id"] = chain_id

        return self

    def set_unbonding_time(self, unbonding_time: str = "1814400s"):
        """
        Swapping staking unbonding_time
        """

        self.log_step(
            "Swapping staking unbonding_time to " + unbonding_time)

        staking_params = self.app_state["staking"]["params"]
        staking_params["unbonding_time"] = unbonding_time

        return self

    def set_max_deposit_period(self, max_deposit_period: str = "1209600s"):
        """
        Swapping governance max_deposit_period
        """

        self.log_step(
            "Swapping governance max deposit period to " + max_deposit_period)

        deposit_params = self.gov["deposit_params"]
        deposit_params["max_deposit_period"] = max_deposit_period

        return self

    def set_min_deposit(self, min_amount: str = "64000000", denom: str = "uatom"):
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

    def set_tally_param(self, parameter_name: str, value: str):
        """
        Swap out tally parameters.
        parameter_name should be one of "quorum", "threshold", "veto_threshold"
        """

        self.log_step("Swapping tally parameter " +
                      parameter_name + " to " + value)

        self.gov["tally_params"][parameter_name] = value

        return self

    def set_voting_period(self, voting_period: str = "1209600s"):
        """
        Swap out the voting period for the governance module
        """

        self.log_step("Swapping governance voting period to " + voting_period)

        self.gov["voting_params"]["voting_period"] = voting_period

        return self

    def create_coin(self, denom: str, amount: str = '0'):
        """
        Creates a new coin based on a given name if it doesn't exist
        """

        self.log_step("Creating new coin " + denom +
                      " valued at " + amount)

        supplies = self.app_state["bank"]["supply"]

        for supply in supplies:
            if supply['denom'] == denom:
                # Already exists, so we don't need to add it
                return self

        # coins must be in ascending sorted order by denom
        bisect.insort_right(supplies,
                            {'denom': denom, 'amount': amount},
                            key=lambda x: x['denom'])
        return self

    def increase_supply(self, increase: int, denom="uatom"):
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
            self.create_coin(denom, str(increase))

        return self

    def increase_balance(self, address: str, amount: int = 300000000, denom: str = 'uatom'):
        """
        Increases the balance of an account
        and the overall supply of uatom by the same amount
        """

        self.log_step("Increasing balance of " + address +
                      " by " + str(amount) + " " + denom)

        balances = self.app_state["bank"]["balances"]

        found_balance = False
        for balance in balances:
            if balance["address"] == address:
                found_balance = True
                had_coin = False
                for coin in balance["coins"]:
                    if coin["denom"] == denom:
                        old_amount = int(coin["amount"])
                        new_amount = old_amount + amount
                        coin["amount"] = str(new_amount)
                        had_coin = True
                        break
                if not had_coin:
                    # coins must be in ascending sorted order by denom
                    bisect.insort_right(balance["coins"],
                                        {"denom": denom,
                                         "amount": str(amount)},
                                        key=lambda x: x['denom'])
                break

        if not found_balance:
            raise Exception('Could not find balance for address')

        self.increase_supply(amount, denom)
        return self

    def increase_validator_power(self,
                                 operator_address,
                                 validator_address,
                                 power_increase):
        #  name=_name,
        #  pub_key=_pubkey):
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

        # found_validator = False
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
                # found_validator = True
            if int(validator["power"]) < smallest_validator_power:
                smallest_validator_index = index
                smallest_validator_power = int(validator["power"])

        last_validator_powers = self.app_state["staking"]["last_validator_powers"]
        for last_validator_power in last_validator_powers:
            if last_validator_power["address"] == operator_address:
                old_power = int(last_validator_power["power"])
                new_power = old_power + power_increase
                last_validator_power["power"] = str(new_power)
                break

        # TODO what happens if the validator is not in the validator set?
        # There are two ways we can do this, either increasing the number of validators or
        # by replacing the smallest validator
        # OPTION 1: INSERT NEW VALIDATOR
        # OPTION 2: REPLACE SMALLEST VALIDATOR

        new_last_total_power = last_total_power + power_increase

        self.app_state["staking"]["last_total_power"] = str(
            new_last_total_power)

        return self

    def increase_validator_stake(self, operator_address: str, increase: int, denom: str = 'uatom'):
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
                    self.log_step("Changing bond status to BOND_STATUS_BONDED")
                    validator["status"] = "BOND_STATUS_BONDED"
                    self.increase_balance(
                        self.get_bonded_pool_address(), old_amount, denom=denom)
                    self.increase_balance(
                        self.get_not_bonded_pool_address(), -1*old_amount, denom=denom)
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

    def increase_delegator_stake(self, delegator: Delegator, increase: int):
        """
        Increases the stake for a delegator
        """

        self.log_step("Increasing delegator stake of " +
                      delegator.address + " by " + str(increase))

        starting_infos = self.app_state["distribution"]["delegator_starting_infos"]

        found_stake = False
        for info in starting_infos:
            if info["delegator_address"] == delegator.address:
                old_stake = float(info["starting_info"]["stake"])
                new_stake = old_stake + increase
                info["starting_info"]["stake"] = str(
                    format(new_stake, ".18f"))
                found_stake = True
                break

        if not found_stake:
            raise Exception("Unable to find delegator_address")

        return self

    def increase_delegator_stake_to_validator(self,
                                              delegator: Delegator,
                                              validator: Validator,
                                              increase: dict):
        """
        Increase a delegator's stake to a validator.
        Includes increasing token bonding pool balance and validator power.
        The "increase" argument is a dictionary with keys 'amount' and 'denom'.
        """
        power_to_tokens = 1000000
        self.increase_balance(address=self.get_bonded_pool_address(),
                              amount=increase['amount'], denom=increase['denom'])
        self.increase_delegator_stake(
            delegator=delegator, increase=increase['amount'])
        self.increase_validator_stake(operator_address=validator.operator_address,
                                      increase=increase['amount'],
                                      denom=increase['denom'])
        self.increase_validator_power(operator_address=validator.operator_address,
                                      validator_address=validator.address,
                                      power_increase=int(increase['amount'] / power_to_tokens))

        delegations = self.app_state["staking"]["delegations"]

        for delegation in delegations:
            if delegation["delegator_address"] == delegator.address and \
               delegation["validator_address"] == validator.operator_address:
                share_increase = float(increase['amount'])
                self.log_step("Increasing delegations of " + delegator.address +
                              " with " + validator.operator_address + " by " + str(share_increase))
                delegation["shares"] = format(
                    float(delegation["shares"]) + share_increase, ".18f")
        return self
