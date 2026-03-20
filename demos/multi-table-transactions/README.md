# Multi-Table Transactions

Databricks now supports atomic transactions across multiple tables using `BEGIN ATOMIC ... END`. This demo shows the feature using [Casper's Kitchens](https://github.com/databricks-solutions/caspers-kitchens) delivery data.

## What's in the demo

1. Create two summary tables from Casper's delivery data (kitchen revenue + driver stats)
2. Use `BEGIN ATOMIC ... END` to update both tables in one atomic operation
3. Show a deliberately failing transaction where both tables roll back cleanly

## Requirements

- Databricks Runtime 18.0+
- Unity Catalog managed tables
- Casper's Kitchens data deployed to a `casper` catalog

## Status

Public Preview (March 2026)

## Links

- [ATOMIC compound statement docs](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-txn-begin-atomic)
- [Transaction modes](https://docs.databricks.com/aws/en/transactions/transaction-modes)
