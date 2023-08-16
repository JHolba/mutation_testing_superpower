# The values behind TDD

# THIS IS A DRAFT!

I am by no means a TDD guru, but I am a believer. That being said, I find it
problematic to apply a all or nothing approach towards it. For instance, what
do you do if your working on 30 year old code, which was definitely *not*
developed with TDD? Is the code irredeemable? Of course not! As Michael
Feathers excellent book "working with legacy software" prescribes, we add
tests and then start refactoring. I have not heard any TDD proponent oppose
this practice. But beware!

> Never trust a test you haven't seen fail
>
> Marit van Dijk
> “Use Testing to Develop Better Software Faster”
> medium.com/97-things/use-testing-to-develop-better-software-faster-9dd2616543d3

The problem: we aren't applying the red part of red, green, refactor. There is no
book keeping which ensures the test guards against some failure.

So what are the things we want to achieve by applying TDD?

* All of the code is designed to be testable
* Every requirement has a test and all code is needed for a requirement
* All tests can fail when the corresponding requirement is not present

These are certainly great goals and TDD is a really efficient way of
getting there. Its like buying the groceries on the way home from work,
you save yourself two trips.

That being said, we really want it to do at least one more thing:

* There should be enough test cases to avoid bugs

Oh yea, right... So let's take a truly toy example borrowed by [Kevlin
Henney's "structure and interpretation of test
cases"](https://www.youtube.com/watch?v=MWsk1h8pv2Q&t=892s). Let's implement
is_leap_year in python.

## leap year mutants

As far as I am concerned, there is only one correct way of doing this
in python:


```python
from calendar import isleap
```

But for the sake of argument, let's have a specification:

> To be a leap year, the year number must be divisible by four – except for
> years divisble by 100, which must also be divisible by 400.

The first part of this specification translates very easily into a test:

```python
import pytest

@pytest.mark.parametrize("year", [1904, 1914, 1918, 1939, 1945, 1908, 2004])
def test_that_only_years_divisible_by_four_are_leap_years(year):
    if year % 4 != 0:
        assert not is_leap_year(year)
    if is_leap_year(year):
        assert year % 4 == 0
```

Now this test has a bit of logic in it, that isn't really necessary. Many would
consider this a bit of a code smell, and I agree. However, it is the direct
translation of the specification. Also, wwriting the test in this way makes it
very easy to translate into a property test using
[hypothesis](hypothesis.works) so you get to have a large amount of test cases
basically for free which I am a big fan of. Hopefully, the logic doesn't
hide anything nefarious away from us...

Now, lets err on the side of following TDD too literally, and get going
with some implementation. Perhaps not everyone would agree at this point,
but later we will have some fun, I promise!

```python
def is_leap_year(year: int) -> bool:
    return year % 4 == 0
```

Clearly flawed, and if you have ever done any programming with dates you
are probably sitting uncomfortably in your chair right now. So lets move swiftly on:

```python
@pytest.mark.parametrize("year", [1600, 1700, 1800, 1900])
def test_that_years_divisible_by_100_are_not_leap_years_unless_divisible_by_400(year):
    if year % 100 == 0:
        assert not is_leap_year(year) or year % 400 == 0

```

which brings us to the final implementation:

```python
def is_leap_year(year: int) -> bool:
    return (year % 4 == 0
      and year % 100 != 0
      or year % 400 == 0
    )
```

As already noted by Kevlin Henney, this isn't very readable for humans, but it
is really easy to create mutants of. There are three comparisons, two boolean
connectives, 3 modulos and 6 integer constants. Each one of those can be
changed to create a mutant. So for instance `year % 4 == 0 and year % 231 != 0
or year % 400 == 0` is an obviously incorrect mutant, while `year % 4 == 0 or
year % 100 != 0 and year % 400 == 0` is more subtle. Luckily, both mutants are
killed by our tests, but how many mutants can we come up with that aren't
killed? Turns out the following implementation passes the tests:


```python
def is_leap_year(year: int) -> bool:
    return False
```

Now, admittedly I have played a bit of a trick. The tests have tried their best
to translate the requirements as written but have conveniently not observed any
of the return values directly. In the specification there is an case hidden by
natural language:


> Year numbers divisible by four and not divisible by 100 are leap years

So lets add that:

```python

@pytest.mark.parametrize("year", [1900, 1908, 1914, 1918, 2004])
def test_that_years_divisible_by_4_and_not_by_100_are_leap_years(year):
    if year % 4 == 0 and year % 100 != 0:
        assert is_leap_year(year)
```




Here is a workflow I have recently started using for legacy code before
refactoring, inspired by [mutation
testing](https://en.wikipedia.org/wiki/Mutation_testing):

1. Create a mutant of the code (preferably one with very undesired behavior or be creative!)
1. If the tests fail: the confidence that refactoring is safe increases
1. else: add a test that *kills the mutant*! If little is known about the requirements of the program
    then use snapshot test.
1. Use source control to remove the mutant

We will have a look at some examples
