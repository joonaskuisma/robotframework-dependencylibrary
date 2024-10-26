# Robot Framework Dependency Library

Declare dependencies between tests.

Ideally tests are independent, but when tests depend on earlier tests,
`DependencyLibrary` makes it easy to explicitly declare these dependencies
and have tests that depend on each other do the right thing.

The `DependencyLibrary` provides two [Robot Framework](https://robotframework.org/) keywords: `Depends On Test`
and `Depends On Suite` for defining dependencies between tests and suites. 
Starting with version 5.0.0 of `robotframework-dependencylibrary`, 
the library also includes a `DependencySolver`.

`DependencySolver` is a pre-run modifier for Robot Framework, designed to 
execute dependent test chains. For instance, if Test C depends on Test B, 
and Test B in turn depends on Test A, then all three tests must be run to 
ensure Test C can execute successfully. However, if you run Robot Framework with
the command `robot -t 'test C' <path_to_your_test_folder>`, Test C will fail 
because this command does not select Tests B and A.

For more details on using the `DependencySolver`, please refer to the section 
[Using DependencySolver](##using-dependencysolver).

## Versioning

This library\'s version numbers follow the [SemVer 2.0.0
specification](https://semver.org/spec/v2.0.0.html).

## Installation

```cmd
pip install robotframework-dependencylibrary
```

You can verify a successful installation with the following command:

```cmd
DependencySolver --version
```

## Using DependencyLibrary

First, include the library in your tests:

``` robotframework
*** Settings ***
Library    DependencyLibrary
```

Typical usage:

``` robotframework
*** Test cases ***
Passing Test
    No operation

A Test that Depends on "Passing Test"
    Depends On Test    Passing Test
    Log    The rest of the keywords in this test will run as normal.
```
> [!NOTE]
> `DependencySolver` recognizes only `Depends On` keywords defined in `[Setup]`
sections, even though these keywords can technically be used in other parts of 
the test. Therefore, it is recommended to specify all dependencies under the 
`[Setup]` section, using the built-in keyword `Run Keywords` if needed. 
Dependencies, after all, are prerequisites for running a test.

When you need to declare multiple dependencies, just repeat the keyword:

``` robotframework
*** Test cases ***
Another Passing Test
    No operation

A Test that Depends on Both "Passing Test" and "Another Passing Test"
    [Setup]    Run Keywords    Depends On Test    Passing Test
    ...    AND    Depends On Test    Another Passing Test
    Log    The rest of the keywords in this test will run as normal.
```

You can also depend on the statuses of entire test suites:

``` robotframework
*** Test cases ***
A Test that Depends on an Entire Test Suite Passing
    [Setup]    Depends On Suite    Some Test Suite Name
    Log    The rest of the keywords will run if that whole suite passed.
```

Note that to depend on a suite or a test from another suite, you must
either run Robot Framework with `--listener DependencyLibrary`, or that
suite must also include `DependencyLibrary` in its `*** Settings ***`. 
Additionally, you can define `DependencyLibrary` in a common 
`some_name.resource` file that is accessible across all suites.

### Skipped Dependencies

If a dependency was skipped, the depending test is also skipped:

``` robotframework
*** Test cases ***
Skipped Test
    Skip    This test is skipped for some reason.

A Test that Depends on "Skipped Test"
    [Setup]    Depends On Test    Skipped Test
    Log    The rest of the keywords (including this log) will NOT run!
```

The skip message follows this format:

    Dependency not met: test case 'Skipped Test' was skipped.

### Failing Dependencies

If a dependency failed, the depending test is skipped instead of
redundantly failing as well:

``` robotframework
*** Test cases ***
Failing Test
    Fail    This test failed for some reason.

A Test that Depends on "Failing Test"
    [Setup]    Depends On Test    Failing Test
    Log    The rest of the keywords (including this log) will NOT run!
```

The skip message follows this format:

    Dependency not met: test case 'Failing Test' failed.

### Mistake Warnings

If you depend on a test or suite that does not exist or has not run yet,

``` robotframework
*** Test cases ***
A Test that Depends on "Missing Test"
    Depends On Test    Missing Test
```

the test will warn and the warning message follows this format:

    Dependency not met: test case 'Missing Test' not found.

If you make a test depend on itself or on the suite that contains it,

``` robotframework
*** Test cases ***
Depends on Self
    Depends On Test    Depends on Self
```

the test will warn and the warning message follows this format:

    Dependency not met: test case 'Depends on Self' mid-execution.

## Using DependencySolver

After you have defined the dependencies of each test in the `[Setup]` section by
using `Depends On Test` or `Depends On Suite` keywords, then pre-run modifier 
`DependencySolver` checks all `[Setup]` sections and solve dependencies before 
running tests. You could use `Depends On Test` or `Depends On Suite` keywords 
multiple times and/or together with other setup keywords by using build-in 
`Run Keywords` at first.

Write test setup as follows:

```RobotFramework
*** Settings ***
Library    DependencyLibrary


*** Test cases ***
Test A
    [Setup]    Do Test Setup...
    [Tags]    tagA
    Do Something...

Test B
    [Setup]    Run Keywords    Depends On Test    name=Test A
    ...    AND    Do Test Setup...
    [Tags]    tagB
    Do Something...

Test C
    [Setup]    Run Keywords    Depends On Test    name=Test B
    ...    AND    Do Test Setup...
    [Tags]    tagC
    Do Something...

```

> [!IMPORTANT]
> `DependencySolver` does not impact the execution order of tests but simply includes the necessary tests and excludes the unnecessary ones. Dependencies can form any tree structure; however, cyclic dependencies (e.g., A -> B and B -> A) will result in an error.

When you have written test dependencies in `[Setup]` sections like above, then 
by using `DependencySolver` as `prerunmodifier` you could run whole dependency 
chain C -> B -> A by command:

```cmd
robot --prerunmodifier DependencyLibrary.DependencySolver:-t:"Test C" <other_robot_commands> <path_to_your_test_folder>
```

Additionally, you could use tags also (but only static, not dynamic tags):
```cmd
robot --prerunmodifier DependencyLibrary.DependencySolver:-i:tagC <other_robot_commands> <path_to_your_test_folder>
```

You can also use shortcut `DependencySolver`. This actually calls `robot` with
`--prerunmodifier`, but it is propably more useful when you do not have any 
(or at least not many) `<other_robot_commands>`. If you have already navigated 
to `<path_to_your_test_folder>`, you does not need to give `--folder` option, 
because default is current directory:

```cmd
DependencySolver -t "test C"
```
Or
```cmd
DependencySolver -i "tagC"
```
These commands will have the same effect as the two commands mentioned above.

For more options and help, please run

```cmd
DependencySolver --help
```

`DependencySolver` generates the following two files in the current directory:

- **DependencySolver.log**: An internal log showing the process of traversing and selecting dependencies.
- **DependencySolver.pabot.txt**: A file for use with [Pabot](https://pabot.org/), detailing how the selected tests can be run in parallel while respecting dependencies.
