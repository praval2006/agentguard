# Paginate the Activity API

The activity endpoint gets slow for large workspaces. Add cursor pagination, returning newest entries first, with 25 entries by default and a maximum requested page size of 100. Include a next cursor when more entries are available. Clients should be able to walk the full history without duplicates when no new activity is being written.
