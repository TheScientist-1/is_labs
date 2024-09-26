from game import init, start
from settings import args


def main():
    init(
        strategy=args.strategy,
        used_map=args.map
    )
    start()


if __name__ == '__main__':
    main()
