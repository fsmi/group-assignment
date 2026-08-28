# O-Phase Group Assignment Solver

Solver for assigning students to O-Phase groups.

The webapp where students sign up is a separate project and can be found [here](https://git.fsmi.org/o-phase/gruppenzuteilung_gui).

## Installation

This project uses [uv](https://docs.astral.sh/uv/). Set up the project environment with

```bash
uv sync
```

The cli tool is then available as

```bash
uv run group-assignment ...
```

## Usage

For the available commands with their parameters and options run

```bash
uv run group-assignment [COMMAND] --help
```

To reproduce the results of a past year run

```bash
uv run group-assignment assign -i data/XXX_input.json -o data/XXX_output.json -c data/XXX_config.toml
```

## Development

This project uses [prek](https://github.com/j178/prek) to run checks and formatters.

Run them manually:

```bash
uv run prek run --all-files
```

Note that the project's venv needs to be activated for that to succeed.

To install the git hooks, so that the checks run before each commit, run

```bash
uv run prek install
```
