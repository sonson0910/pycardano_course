from pycardano import BlockFrostChainContext

PROJECT_ID='preprod3YH93sMzhUDJt2WiaAtYaEOLtfJXw44E'

context = BlockFrostChainContext(project_id=PROJECT_ID, base_url='https://cardano-preprod.blockfrost.io/api')

lastest_block = context.api.block_latest()

print(f'Block Hash: {lastest_block}')

print(f'Absolute Slot: {lastest_block.slot}')

print(f'Epoch: {lastest_block.epoch}')

print(f'Tx count: {lastest_block.tx_count}  transactions')

print(f'gas fee: {lastest_block.fees} lovelace')

print(f'Size: {lastest_block.size} bytes')
