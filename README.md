# Cosmos Genesis Tinker

You can get more docs by invoking `pydoc3 cosmos_genesis_tinker`.
TODO: Add the output to the README or it's own .md file

## API

Tinkering with genesis files

```python
import cosmos_genesis_tinker

genesis = cosmos_genesis_tinker.GenesisTinker()

genesis.load_file(file)
genesis.save_file(file)
old  = {
"pub_key": "",
"address": "",
"consensus_address": ""
}
genesis.swap_validator(old, new)
genesis.swap_delegator(old_adddress, new_address)
genesis.increase_balance(address, increase=300000000, denom="uatom")
genesis.increase_validator_power(validator_address, power_increase=DEFAULT_POWER)
genesis.increase_validator_stake(operator_address, increase=DEFAULT_POWER*POWER_TO_TOKENS)
genesis.increase_delegator_stake(delegator_address, increase=DEFAULT_POWER*POWER_TO_TOKENS)
```
