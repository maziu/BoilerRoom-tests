run tests:

```pytest -vs .```

will run all test_* functions in test_*.py files.

filter test choosing file or using `-k`:

```pytest -vs test_fan.py```
```pytest -vs . -k smoke```
```pytest -vs test_fan.py -k hysteresis```
