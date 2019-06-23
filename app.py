from lxml import etree
import argparse


def check_args():
    parser = argparse.ArgumentParser(description="""
    PyUi2Html Parser 2019 (Faysal Al-Banna)
    """)
    parser.add_argument('IF', type=str, help="The File to parse")
    parser.add_argument(
        'OF',
        type=str,
        help="File to save to",
        default=sys.stdout,
        nargs='?'
    )
    return parser.parse_args()


if __name__ == "__main__":
    import sys
    print(check_args())
