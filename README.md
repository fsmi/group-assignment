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
uv run group-assignment
```

## Usage

For the available commands with their parameters and options run

```bash
uv run group-assignment [COMMAND] --help
```

To reproduce the results of a past year run

```bash
uv run group-assignment assign -i historic_data/XXX_input.json -o data/XXX_assignment.json -c historic_data/XXX_config.toml
```

## File Formats

### Input (`-i`)

```json
{
  "groups": {
    <group_id>: {
      "name": str,
      "capacity": int,
      "min_size": int,
      "course_type": "info" | "compsci" | "mathe" | "cds" | "lehramt" | "any",
      "degree_type": "bachelor" | "master" | "any"
    }
  },
  "students": {
    <student_id>: {
      "name": str,
      "course_type": "info" | "compsci" | "mathe" | "cds" | "lehramt",
      "degree_type": "bachelor" | "master", // invalid: compsci bachelor
      "not_fluent_in_german": bool,     // optional, default: false
      "type_specific_assignment": bool
    }
  },
  "teams": {
    <team_id>: [<student_id>]           // each student in exactly one team
  },
  "ratings": {                          // exactly one rating per team
    <team_id>: {<group_id>: int}        // score per group, lower = higher priority; not all groups have to be rated
  }
}
```

### Output (`-o`)

```json
{
  <team_id>: <group_id>                 // every team is assigned to exactly one group
}
```

## Development

This project uses [prek](https://github.com/j178/prek) to run checks and formatters.

Run them manually:

```bash
uv run prek run --all-files
```

To install a git hook, so that they run automatically before each commit, run

```bash
uv run prek install
```

Note that the project's venv needs to be activated when committing for the hook to succeed.
