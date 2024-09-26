import argparse
from strategies import Strategy

parser = argparse.ArgumentParser(description='Old-but-gold Pacman, some AI for it')
parser.add_argument(
    '--strategy', type=str, default='A*',
    help=f'Used strategy. Possible choices: {", ".join(Strategy.STORAGE_REGISTRY.keys())}'
)

parser.add_argument(
    '--map', type=str, default='10x10',
    help=f'Used map. Possible choices: 10x10, 30x30, 150x150'
)

args = parser.parse_args()
