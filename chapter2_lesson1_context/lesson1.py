# import os
# from dotenv import load_dotenv
# from pycardano import BlockFrostChainContext
# load_dotenv()

# project_id= os.getenv("BLOCKFROST_PROJECT_ID")

# print(project_id)

# # project_id = 'preprodCtJxvR4JpFpGEwm7G3SmkGWmrYUjNAc4'

# blockfrost_context = BlockFrostChainContext(
#     project_id=project_id,
#     base_url="https://cardano-preprod.blockfrost.io/api"
# )

# print(f"Slot hiện tại: {blockfrost_context.last_block_slot}")

# print(f"Epoch hiện tại: {blockfrost_context.epoch}")

from pycardano import OgmiosChainContext

OGMIOS_HOST='https://ogmios15n53hr3m28uexqltyr7.cardano-preprod-v6.ogmios-m1.dmtr.host'
OGMIOS_PORT=443
OGMIOS_SECURE=True

context = OgmiosChainContext(
    host=OGMIOS_HOST,
    port=OGMIOS_PORT,
    secure=OGMIOS_SECURE
)

# tip = context.last_block_slot
print(f'Network: {context.network}')
# print(f"Slot hiện tại: {tip}")
