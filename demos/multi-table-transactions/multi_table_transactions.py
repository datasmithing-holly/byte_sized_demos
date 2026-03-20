# Databricks notebook source

# MAGIC %md
# MAGIC # Multi-Table Transactions
# MAGIC `BEGIN ATOMIC ... END` wraps multiple table writes into one unit. Everything commits together, or everything rolls back. No more half-updated summary tables.
# MAGIC
# MAGIC Requires **Runtime 18.0+** and Unity Catalog managed tables.
# MAGIC
# MAGIC [Docs](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-txn-begin-atomic)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- two tables that need to stay in sync: one for what kitchens earned, one for what drivers earned
# MAGIC CREATE SCHEMA IF NOT EXISTS caspers_kitchen.demo_transactions;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE caspers_kitchen.demo_transactions.kitchen_totals (kitchen STRING, orders INT, revenue DECIMAL(10,2));
# MAGIC INSERT INTO caspers_kitchen.demo_transactions.kitchen_totals VALUES
# MAGIC   ('Sizzle & Spice', 12, 384.50), ('Urban Umami', 8, 290.00), ('Pepper Patch', 15, 412.75);
# MAGIC
# MAGIC CREATE OR REPLACE TABLE caspers_kitchen.demo_transactions.driver_totals (driver STRING, deliveries INT, fees DECIMAL(10,2));
# MAGIC INSERT INTO caspers_kitchen.demo_transactions.driver_totals VALUES
# MAGIC   ('Driver A', 20, 95.00), ('Driver B', 15, 71.50);

# COMMAND ----------

# MAGIC %sql
# MAGIC -- both tables updated in one atomic block: either both commit or neither does
# MAGIC BEGIN ATOMIC
# MAGIC   INSERT INTO caspers_kitchen.demo_transactions.kitchen_totals VALUES ('Burger Barn', 6, 178.00);
# MAGIC   INSERT INTO caspers_kitchen.demo_transactions.driver_totals VALUES ('Driver C', 6, 28.50);
# MAGIC END;
# MAGIC
# MAGIC SELECT 'kitchen_totals' AS tbl, * FROM caspers_kitchen.demo_transactions.kitchen_totals
# MAGIC UNION ALL
# MAGIC SELECT 'driver_totals', * FROM caspers_kitchen.demo_transactions.driver_totals;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- now break the second statement on purpose: fake_column doesn't exist
# MAGIC -- the first INSERT is valid but gets rolled back with the second
# MAGIC BEGIN ATOMIC
# MAGIC   INSERT INTO caspers_kitchen.demo_transactions.kitchen_totals VALUES ('Ghost Kitchen', 1, 9999.99);
# MAGIC   INSERT INTO caspers_kitchen.demo_transactions.driver_totals SELECT fake_column FROM caspers_kitchen.demo_transactions.driver_totals;
# MAGIC END;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- no Ghost Kitchen. the valid insert was rolled back with the broken one.
# MAGIC SELECT * FROM caspers_kitchen.demo_transactions.kitchen_totals WHERE kitchen = 'Ghost Kitchen';

# COMMAND ----------

# MAGIC %md
# MAGIC **Use it if** you do cross-table writes that need to stay in sync (summary refreshes, staging to production moves, anything where half-done is worse than not-done).
# MAGIC
# MAGIC **Skip it if** your tables aren't in Unity Catalog, you need manual COMMIT/ROLLBACK control (`BEGIN TRANSACTION` is the separate feature for that), or you're not on 18.0 yet.
