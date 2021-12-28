# User Preferences

The `users.UserConfig` model holds individual preferences for each user in the form of JSON data. This page serves as a manifest of all recognized user preferences in NetBox.

## Available Preferences

| Name                    | Description |
|-------------------------|-------------|
| data_format             | Preferred format when rendering raw data (JSON or YAML) |
| pagination.per_page     | The number of items to display per page of a paginated table |
| tables.${table}.columns | The ordered list of columns to display when viewing the table |
| ui.colormode            | Light or dark mode in the user interface |