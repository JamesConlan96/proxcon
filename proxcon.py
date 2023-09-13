#!/usr/bin/env python3


import argparse
from getpass import getpass
from ipaddress import IPv4Address
import os
import sys
from tabulate import tabulate


proxyConf = "/etc/proxychains4.conf"
dotPath = os.path.join(os.path.expanduser(f"~{os.getlogin()}"), ".proxcon")


def genParser() -> argparse.ArgumentParser:
    """Generates a CLI argument parser
    @return Argument parser object
    """
    parser = argparse.ArgumentParser(description="A utility for quickly " +
                                     "switching proxychains proxies")
    subparsers = parser.add_subparsers()
    parserSwitch = subparsers.add_parser("switch",
                                         help="switch to a proxy definition")
    parserSwitch.set_defaults(func=switch, file=proxyConf)
    parserAdd = subparsers.add_parser("add", help="add a proxy definition")
    parserAdd.set_defaults(func=add)
    parserUpdate = subparsers.add_parser("update",
                                         help="update a proxy definition")
    parserUpdate.add_argument('-r', "--rename", action="store",
                               help="new name for proxy definition")
    parserUpdate.set_defaults(func=update)
    for subparser in [(parserAdd, True), (parserUpdate, False)]:
        subparser[0].add_argument('-t', "--type", action="store",
                                  choices=["http", "raw", "socks4", "socks5"],
                                  help="proxy type", required=subparser[1])
        subparser[0].add_argument('-i', "--ipv4", action="store",
                                  type=IPv4Address,
                                  help="proxy server IPv4 address",
                                  required=subparser[1])
        subparser[0].add_argument('-p', "--port", action="store", type=int,
                                  help="proxy server port",
                                  required=subparser[1])
        subparser[0].add_argument('-u', "--user", action="store",
                                  help="username for proxy authentication")
        subparser[0].add_argument('-P', "--pass", action="store_true", 
                                  dest="passw", help="a password is required " +
                                  "to access the proxy")
    parserList = subparsers.add_parser("list",
                                         help="list all proxy definitions")
    parserList.set_defaults(func=listDefs)
    parserActive = subparsers.add_parser("active",
                                         help="show active proxy definition")
    parserActive.set_defaults(func=showActive, file=proxyConf)
    for subparser in [parserAdd, parserSwitch, parserActive]:
        subparser.add_argument('-f', '--file', action="store",
                               default=proxyConf,
                               help="proxychains configuration file to use " +
                               f"(default: '{proxyConf}')")
    parserDelete = subparsers.add_parser("delete",
                                         help="delete a proxy definition")
    parserDelete.set_defaults(func=delete)
    for subparser in [parserSwitch, parserAdd, parserUpdate, parserDelete]:
        subparser.add_argument("name", action="store",
                               help="name of proxy definition")
    return parser

def yesNo(prompt: str) -> bool:
        """Prompts the user for a yes/no response
        @param prompt: Prompt to display to the user
        @return: True if yes, False if no
        """
        yn = input(f"{prompt} (y/n): ")
        if yn.lower() == 'y':
            return True
        elif yn.lower() == 'n':
            return False
        else:
            return yesNo(prompt)

def checkArgs(args: argparse.Namespace) -> argparse.Namespace:
    """Validates CLI arguments
    @param args: Parsed CLI arguments
    @return Validated CLI arguments
    """
    if hasattr(args, "ipv4") and args.ipv4 is not None:
        args.ipv4 = format(args.ipv4) # Convert to string
    if hasattr(args, "port") and args.port is not None:
        if not 0 < args.port <= 65535:
            sys.exit(f"'{args.port}' is not a valid port number")
    if hasattr(args, "user") and hasattr(args, "passw"):
        if args.func == add:
            if args.user is None and args.passw:
                sys.exit("Please specify a username (-u <username>)")
            if args.user is not None and args.passw is False:
                args.passw = "<PROMPT_ON_SWITCH>"
        elif args.func == update:
            if args.user is not None and args.passw is False:
                yn = yesNo("You have updated a username but not a password. " +
                           "Do you wish to keep the existing password " +
                           "configuration?")
                if not yn:
                    args.passw = "<PROMPT_ON_SWITCH>"
                    print("Users will be prompted for the password on switch")
    if hasattr(args, "passw") and args.passw:
        passw = getpass("Password (Leave blank to prompt for password on " +
                        "switch): ")
        if passw == "":
            args.passw = "<PROMPT_ON_SWITCH>"
        elif passw == getpass("Confirm Password: "):
            args.passw = passw
        else:
            sys.exit("Passwords did not match")
    return args

def checkDot():
    """Checks proxcon dot file"""
    try:
        open(dotPath, 'a+').close()
    except:
        sys.exit(f"Cannot open proxcon configuration file '{dotPath}" +
                 "', do you have the correct permissions?")

def checkProx(confPath: str):
    """Checks proxychains config file
    @param confPath: Path to proxychains configuration file
    """
    if os.path.isfile(confPath):
        try:
            open(confPath, 'r+').close()
        except:
            sys.exit(f"Cannot open proxychains configuration file '{confPath}" +
                     "' for writing. Do you have the correct permissions?")
    else:
        sys.exit(f"Proxychains configuration file '{confPath}' does not exist")

def getDefs() -> list:
    """Reads the proxcon dot file and returns a list of lines
    @return List of proxy definitions
    """
    with open(dotPath, 'r') as f:
        lines = f.readlines()
    defs = []
    for line in lines:
        if line.strip() == "":
            continue
        split = line.rstrip().split("\t")
        if not 4 <= len(split) <= 6:
            sys.exit(f"Line '{line}' is not a valid proxy definition")    
        user = split[4] if len(split) >= 5 else None
        passw = split[5] if len(split) == 6 else None
        defs.append({
            "Name": split[0],
            "Type": split[1],
            "IPv4": split[2],
            "Port": split[3],
            "Username": user,
            "Password": passw
        })
    return defs

def checkName(name: str, defs: list):
    """Checks if a proxy definition with a given name exists and errors if so
    @param name: Name to check for
    @param defs: List of proxy definitions to check against
    """
    for defi in defs:
        if name == defi['Name']:
            sys.exit(f"A proxy definition with name '{name}' already " +
                     "exists")

def genOutLine(name: str, type: str, ipv4: str, port: int, user: str,
               passw: str) -> str:
    """Generates an output line
    @param name: Proxy definition name
    @param type: Proxy type
    @param ipv4: Proxy IPv4 address
    @param port: Proxy port
    @param user: Proxy username
    @param passw: Proxy password
    @return Output line
    """
    proxDef = f"{name}\t{type}\t{ipv4}\t{port}"
    if user and user is not None:
        proxDef += f"\t{user}"
    if passw and passw is not None:
        proxDef += f"\t{passw}"
    return proxDef

def add(args: argparse.Namespace):
    """Adds a proxy definition with the given parameters
    @param args: Validated CLI arguments
    """
    defs = getDefs()
    checkName(args.name, defs)
    proxDef = "\n" if len(defs) else ""
    proxDef += genOutLine(args.name, args.type, args.ipv4, args.port, args.user,
                          args.passw)
    with open(dotPath, 'a') as f:
        f.write(proxDef)
    if yesNo("Proxy definition added successfully. Would you like to switch " +
             "to it now?"):
        switch(args)

def update(args: argparse.Namespace):
    """Updates a proxy definition with the given parameters
    @param args: Validated CLI arguments
    """
    defs = getDefs()
    out = ""
    for defi in defs:
        if defi['Name'] == args.name:
            if args.rename is not None:
                checkName(args.rename, defs)
                defi['Name'] = args.rename
            if args.type is not None:
                defi['Type'] = args.type
            if args.ipv4 is not None:
                defi['IPv4'] = args.ipv4
            if args.port is not None:
                defi['Port'] = args.port
            if args.user is not None:
                defi['Username'] = args.user
            if args.passw is not None:
                defi['Password'] = args.passw
        out += genOutLine(defi['Name'], defi['Type'], defi['IPv4'],
                          defi['Port'], defi['Username'], defi['Password'])
        out += "\n"
    with open(dotPath, 'w') as f:
        f.write(out)
    print("Proxy definition updated successfully")

def listDefs(args: argparse.Namespace):
    """Lists proxy definitions
    @param args: Validated CLI arguments
    """
    defs = getDefs()
    for defi in defs:
        defi['Username'] = "N/A" if defi['Username'] == None else \
                           defi['Username']
        defi['Password'] = "N/A" if defi['Password'] == None else \
                           defi['Password']
    try:
        print(tabulate([x.values() for x in defs], defs[0].keys()))
    except:
        sys.exit("No proxy definitions configured")

def showActive(args: argparse.Namespace):
    """Show the active proxy configuration
    @Param args: Validated CLI arguments
    """
    try:
        with open(proxyConf, 'r') as f:
            lines = f.readlines()
    except:
        sys.exit("Could not open proxychains configuration file '" +
                 f"{proxyConf}'")
    proxyList = False
    for line in lines:
        line = line.rstrip("\n")
        if proxyList and line.strip() != "" and \
            not line.strip().startswith("#"):
            print(line)
            break
        if line.strip() == "[ProxyList]":
            proxyList = True

def delete(args: argparse.Namespace):
    """Deletes a specified proxy definition
    @param args: Validated CLI arguments
    """
    defs = getDefs()
    found = False
    for i, defi in enumerate(defs):
        if defi['Name'] == args.name:
            found = True
            yn = yesNo("Are you sure you want to delete proxy definition '" +
                       f"{args.name}'?")
            if yn:
                defs.pop(i)
            else:
                sys.exit()
    if not found:
        sys.exit(f"Proxy definition '{args.name}' does not exist")
    out = ""
    for defi in defs:
        out += genOutLine(defi['Name'], defi['Type'], defi['IPv4'],
                          defi['Port'], defi['Username'], defi['Password'])
        out += "\n"
    with open(dotPath, 'w') as f:
        f.write(out)
    print("Proxy definition deleted successfully")

def switch(args: argparse.Namespace):
    """Switches to a specified proxy definition
    @param args: Validated CLI arguments
    """
    checkProx(args.file)
    defs = getDefs()
    proxLine = ""
    for defi in defs:
        if defi['Name'] == args.name:
            proxLine = f"{defi['Type']}\t{defi['IPv4']}\t{defi['Port']}"
            if defi['Password'] == "<PROMPT_ON_SWITCH>":
                passw = getpass(f"Password for '{args.name}': ")
                if passw == getpass("Confirm Password: "):
                    defi['Password'] = passw
            if defi['Username'] is not None:
                proxLine += f"\t{defi['Username']}\t"
                if defi['Password'] is not None:
                    proxLine += f"{defi['Password']}"
            break
    if proxLine == "":
        sys.exit(f"Proxy definition '{args.name}' does not exist")
    with open(proxyConf, 'r') as f:
        lines = f.readlines()
    replace = False
    out = ""
    for line in lines:
        line = line.rstrip("\n")
        if replace and line.strip() != "" and not line.strip().startswith("#"):
            continue
        if line.strip() == "[ProxyList]":
            replace = True
        out += f"{line}\n"
    out += f"{proxLine}\n"
    with open(proxyConf, 'w') as f:
        f.write(out)
    print("Proxychains configuration updated successfully")
    

def main():
    """Main method"""
    parser = genParser()
    if len(sys.argv) == 1:
        parser.print_usage()
        sys.exit()
    args = parser.parse_args()
    args = checkArgs(args)
    checkDot()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
