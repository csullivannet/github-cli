# github-cli

A simple CLI tool to interact with the GitHub API. Gets PRs from provided org
and repos and optionally filters them for more precise output.

Example usage:

```
# Basic call
cli --org nginx-proxy \
  --repo nginx-proxy \
  --labels status/pr-needs-tests type/feat

# Strict label matching with age requirement
cli --org nginx-proxy \
  --repo nginx-proxy \
  --labels status/pr-needs-tests type/feat \
  --all-labels \
  --max-age 100

# Verbose output written to file
cli --org nginx-proxy \
  --repo nginx-proxy acme-companion \
  --labels status/pr-needs-tests type/feat \
  --file output.json \
  --verbose
```

## Setting up your environment

### Prerequisites

This CLI tool was designed for use with python3. Please ensure you have python3
v3.9+ installed. [Get it here.](https://www.python.org/downloads/)

`pip` is also required. You probably already have it on your system, but just in
case you don't you can follow instructions on how to install it
[here](https://pip.pypa.io/en/stable/installing/). There may be other more
convenient options depending upon your operating system.

### Python Dependencies

Dependencies can be installed by running:

```
pip install --user pipenv
pipenv shell
pipenv install
```

### Installation

While in the virtualenv (activated with `pipenv shell`):

```
python3 setup.py install
```

You may now run the command `cli` within the python virtual environment.
This is the preferred approach as it is easier to clean up and control the
environment.

If desired, you may also place an alias to the binary on the PATH. While in the
virtualenv, run:

```
sudo ln -s $(which cli) /usr/local/bin/cli
```

You may also install globally in one step (available anywhere):

```
sudo python3 setup.py install
```

This method is not recommended as it is harder to clean up and has a higher risk
of mismatched dependencies with other tools and libraries.


## Running

`cli` has the following switches:

- `--org`: A single GitHub org to check.
- `--repo`: Space separated list of repos to check, from org above.
- `--max-age`: Maximum age of PR, in days.
- `--labels`: Space separated list of labels. Will only return PRs that have one
              of these labels.
- `--all-labels`: Requires that all of the labels provided by the above switch
                  are present. If there are labels in addition to these, they
                  are ignored.
- `--file`: The path to a file to write output to. Otherwise output is directed
            to STDOUT.
- `--verbose`: By default

## Developing

Development requires extra packages. At this point only a linter has been set
up. Install the linter with:

```
pipenv shell
pipenv install --dev
```

## TODO

- Add unit tests
- Add unit test workflow for GHA
- Exact match of labels (do not ignore extra labels found)
- Minimum age switch
- Query issues instead of PRs
