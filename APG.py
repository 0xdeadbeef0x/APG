import argparse
from C4Audits import C4Audits

argParser = argparse.ArgumentParser()
argParser.add_argument("-c4", "--c4user", help="Your Code4rena handler")
args = argParser.parse_args()

def main():
    c4 = C4Audits()
    c4.createC4(args.c4user)

if __name__ == "__main__":
    main()