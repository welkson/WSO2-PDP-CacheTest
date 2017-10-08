## Environment

- Linux Mint x64

- WSO2 5.4.0-alpha2 (also tested with WSO IS 5.3)

- Java 1.8.0_03 (OpenJDK)

- Python 2.7

- Python packages (in requirements.txt)

- PIP 9.0.1 [1]

- Enable Admin ServicesWSDL [2]

References:

[1] https://pip.pypa.io/en/stable/installing/

[2] https://docs.wso2.com/display/IS540/Entitlement+using+SOAP+Service


## Install dependencies

```
pip install -U -r requirements.txt
```

# Tests

- Start WSO2 IS

```
~/wso2is-5.4.0-alpha2/bin/wso2server.sh --start
```

- Delete all Policies in PAP

- Delete all Policies in PDP

- Execute wso2_test.py

```
python wso2_test.py
```

Policy is created in PAP/PDP, and tests with PDP is sucessfull (first test is PERMIT and second test is DENY)

- Delete all Policies in PAP and PDP

- Repeat python tests

All tests result DENY (broken)


