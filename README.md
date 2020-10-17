## Complex solution

Intel Core i7-7700HQ

```diff 
+ tests.py::test_bnb[C125.9] Best available score: 44.75270108043218, heuristic best score: 30
Found new solution:  31
Found new solution:  33
Found new solution:  34
+ Best solution results 34
+ Elapsed time: 336.6159083843231

+ tests.py::test_bnb[keller4] Best available score: 20.722710259749416, heuristic best score: 11
Found new solution:  11
- Return by timeout
+ Best solution results 11
+ Elapsed time: 1800.7376623153687

+ tests.py::test_bnb[brock200_2] Best available score: 27.407342425310613, heuristic best score: 9
Found new solution:  9
Found new solution:  10
Found new solution:  11
- Return by timeout
+ Best solution results 11
+ Elapsed time: 1801.7121336460114

+ tests.py::test_bnb[p_hat300-1] Best available score: 20.999999999999993, heuristic best score: 7
Found new solution:  7
Found new solution:  8
- Return by timeout
+ Best solution results 8
+ Elapsed time: 1807.7082471847534
```
## Heuristics
``` diff
tests.py::test_heuristic[C125.9]
Heuristic cliue size 30. Actual best clique size 34

tests.py::test_heuristic[keller4]
Heuristic cliue size 11. Actual best clique size 11

tests.py::test_heuristic[brock200_2]
Heuristic cliue size 9. Actual best clique size 12

tests.py::test_heuristic[p_hat300-1]
Heuristic cliue size 7. Actual best clique size 8

```
