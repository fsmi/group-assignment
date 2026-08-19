# Historic Data

Data from past years.

## Notes

- [2022-10_input.json](2022-10_input.json)
  - No `min_size` provided for groups -> added as 0
  - Some students had `any` as their degree type -> set to `bachelor`
- [2023-10_input.json](2023-10_input.json)
  - Some students had `any` as their degree type -> set to `bachelor`
- [2024-10_input.json](2024-10_input.json)
  - Some students had `any` as their degree type -> set to `bachelor`
  - Master students per group are limited in a hacky way by creating each group twice with different degree types -> [2024-10_input_mod.json](2024-10_input_mod.json) merges these back into single groups
- [2025-10_assignment.json](2025-10_assignment.json)
  - Not exactly reproducible with the current codebase because of a solver version mismatch

## Anonymize Input File

```bash
jq '.students |= map_values(.name = "-")' input.json > input_anon.json
```
