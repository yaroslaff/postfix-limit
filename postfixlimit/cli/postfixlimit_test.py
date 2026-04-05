
import argparse
import socket
import time

from ..policyhandler import PolicyHandler
from ..config import Config 
from ..limiter import Limiter

def get_args():
    def_config = "/etc/postfixlimit.conf"
    parser = argparse.ArgumentParser("Simple Postfix Limiter (policy service)")
    parser.add_argument("--port", "-p", type=int, default=None,
                        help=f"Listen this port")
    parser.add_argument("--address", "-a", type=str, default=None,
                        help=f"Listen this address")
    parser.add_argument("--config", "-c", type=str, default=def_config,
                        help=f"Read this config (def: {def_config})")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=1,
                        help="Verbosity level: 0=warning, 1=info, 2=debug+all attrs (default 1)")
    parser.add_argument(metavar="VAR=VALUE", dest='vars', nargs='*', help="Additional variables to include in the policy check (e.g., sasl_username=alice)")
    # parser.add_argument("--option", "-o", nargs='*', type=str, metavar="KEY=VAL", help="Override config option (e.g., 'dump_file=') for this run")

    return parser.parse_args()


def send_policy_request(attrs: dict, host='localhost', port=4455) -> str:
    with socket.create_connection((host, port)) as sock:
        f = sock.makefile('rwb')
        for key, value in attrs.items():
            line = f"{key}={value}\n"
            print(line, end='')  # print to console for debugging
            sock.sendall(line.encode())            
        sock.sendall(b"\n")  # empty line = end of request
        
        response = sock.recv(4096).decode().strip()
        return response

def main():
    args = get_args()

    # parse overrides
    config_overrides = {
        'dump_file': None,  # disable dumping to file for test
        'log_file': None,   # disable logging to file for test
    }
    config = Config(args.config, overrides=config_overrides)

    if args.port is not None:
        config.port = args.port
    if args.address is not None:
        config.address = args.address

    attrs = { 
        'request': 'smtpd_access_policy', 
        'protocol_state': 'RCPT', 
        'protocol_name': 'ESMTP', 
        'client_address': '127.0.0.1', 
        'client_name': 'localhost', 
        'client_port': '46764', 
        'reverse_client_name': 'localhost', 
        'server_address': '127.0.0.1', 
        'server_port': '25', 
        'helo_name': 'localhost', 
        'sender': 'a43@example.ccom', 
        'recipient': 'me@example.net', 
        'recipient_count': '0', 'queue_id': '', 
        'instance': 'cab1.69d28e8b.a077f.0', 
        'size': '800', 
        'etrn_domain': '', 
        'stress': '', 
        'sasl_method': '', 
        'sasl_username': '', 
        'sasl_sender': '', 
        'ccert_subject': '', 
        'ccert_issuer': '', 
        'ccert_fingerprint': '', 
        'ccert_pubkey_fingerprint': '', 
        'encryption_protocol': 'TLSv1.3', 
        'encryption_cipher': 'TLS_AES_256_GCM_SHA384', 
        'encryption_keysize': '256', 
        'policy_context': '', 
        'compatibility_level': '2', 
        'mail_version': '3.10.5'
        }

    if args.vars:
        for opt in args.vars:
            if '=' not in opt:
                print(f"Invalid option format: {opt}. Expected KEY=VAL.")
                return
            key, val = opt.split('=', 1)
            attrs[key] = val


    print(args.vars)
    result = send_policy_request(attrs, host=config.address, port=config.port)
    print(result)
