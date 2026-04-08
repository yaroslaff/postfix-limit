# postfixlimit

A lightweight, modern rate-limiting policy service for Postfix that protects you from outbound spam and runaway application mail.

## Features

- Limits the number of messages sent through the Postfix MTA
- Supports multiple key types: client IP address, SASL authentication username, or sender address
- Flexible rate limit configuration with a global default — e.g. "100 messages per 2 hours"
- Pluggable storage backends: in-memory or Redis
- Three [rate-limiting strategies](https://limits.readthedocs.io/en/stable/strategies.html): fixed-window, moving-window, and sliding-window

## Installation

### Quick Start

```bash
# install from pypi
PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install postfixlimit
# or installl from git repo directly
PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install git+https://github.com/yaroslaff/postfixlimit


wget https://raw.githubusercontent.com/yaroslaff/postfixlimit/refs/heads/master/contrib/postfixlimit.service
wget https://raw.githubusercontent.com/yaroslaff/postfixlimit/refs/heads/master/contrib/postfixlimit.conf

cp postfixlimit.service /etc/systemd/system/
systemctl daemon-reload

cp postfixlimit.conf /etc/
```

Once installed, edit `/etc/postfixlimit.conf` to configure `field`, `default_limit`, and any per-sender limits. Then start the daemon:

```bash
systemctl start postfixlimit
```

To cleanly uninstall:

```bash
PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx uninstall postfixlimit
```

## Systemd Unit File

Copy [contrib/postfixlimit.service](contrib/postfixlimit.service) to `/etc/systemd/system/postfixlimit.service`, then reload and start the service:

```bash
systemctl daemon-reload
systemctl start postfixlimit
```

## Configuration

An example configuration file is provided at [contrib/postfixlimit.conf](contrib/postfixlimit.conf). Save it as `/etc/postfixlimit.conf`:

```ini
# Main server options
[server]
address = 127.0.0.1
port = 4455

# field is one of: sender / sasl_username / client_address
field = sender
default_limit = 5/day
action = DEFER
action_text = Limit ({limit}) exceeded for {field}={key}

# Storage backend: memory:// (default) or Redis
# storage = redis://localhost:6379/
storage = memory://

# Rate-limiting strategy: fixed-window / sliding-window / moving-window
strategy = fixed-window

dump_period = 60
dump_file = /var/lib/postfixlimit/limits.txt
log_file = /var/log/postfixlimit/postfixlimit.log

# Per-sender overrides
[limits]
aaa@example.com = 100 / day
```

## Rate Limit Syntax

postfixlimit uses the [limits](https://github.com/alisaifee/limits) library. Limits follow its [string notation](https://limits.readthedocs.io/en/stable/quickstart.html#rate-limit-string-notation):

```
[count] [per|/] [n (optional)] [second|minute|hour|day|month|year]
```

## Postfix Integration

Add the following to `smtpd_recipient_restrictions` in your Postfix `main.cf`:

```
smtpd_recipient_restrictions =
    check_policy_service inet:127.0.0.1:4455
```

## Viewing Counter State

Every `dump_period` seconds, postfixlimit writes the current counter values to `dump_file`:

```shell
root@micromail:~# cat /var/lib/postfixlimit/limits.txt
Limits (2026-04-08 22:00:04):
  stg: 200 per 1 day remaining: 200
  odoomarketing: 1000 per 1 day remaining: 1000
  odoocare: 7000 per 1 day remaining: 6095
  mainweb: 3000 per 1 day remaining: 2991
```

## Resetting Counters

**Redis storage** — reset a specific counter:

```bash
postfixlimit --reset COUNTERNAME
```

Reset all counters:

```bash
postfixlimit --reset ALL
```

**In-memory storage** — simply restart the daemon; all counters are cleared on startup.

## Developer Reference

Postfix policy protocol specification: https://www.postfix.org/SMTPD_POLICY_README.html