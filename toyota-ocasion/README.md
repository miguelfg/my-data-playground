# ETL and Dashboard of Spanish Toyota second hand car sales

## Description

A demo ETL for gathering spanish oficial Toyota's second-hand car offers, and a streamlit
dashboard app on top.

The ETL is separated in scraping, transformation, mapping, and loading steps. Where the mapping
is meant to standarize the data schema with other sources (here there is only Toyota data).

The dasboard is built with streamlit and seaborn charts.

## Init

```sh
> make init
> make install
```

## Examples

```sh
> make run-etl
> make db-init
> make run-streamlit
```
