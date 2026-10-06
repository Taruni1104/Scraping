# AI usage

AI assistance was used to scaffold the project structure, draft the scraper and processing modules, and review the assignment requirements. The implementation was reviewed against the supplied Books to Scrape and Quotes to Scrape schemas.

I verified the processing behavior with offline unit tests for whitespace, prices, ratings, tags, validation reasons, and normalized duplicate detection. The final design keeps networking, source-specific parsing, pure transformations, validation, and orchestration in separate modules so each part can be explained and tested.

Known limitations are documented in `README.md`, including the decision not to request every book detail page for category and description.
