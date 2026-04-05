# postfix-limit
Simple mail limiter for postfix (check_policy_service)

~~~
PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install

# and same for clean uninstall
PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx uninstall postfixlimit
~~~

## Protocol specification
https://www.postfix.org/SMTPD_POLICY_README.html

## Integration with postfix
add this to `smtpd_recipient_restrictions` in `main.cf`:
~~~
smtpd_recipient_restrictions = 
        check_policy_service inet:127.0.0.1:4455
~~~


## Example config file
~~~

~~~