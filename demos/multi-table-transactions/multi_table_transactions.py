# Databricks notebook source

# MAGIC %md
# MAGIC # Multi-Table Transactions in Databricks
# MAGIC
# MAGIC Databricks now supports atomic transactions that span multiple tables.
# MAGIC Everything inside a `BEGIN ATOMIC ... END` block either succeeds together or rolls back together.
# MAGIC No more partial updates. No more inconsistent state between related tables.
# MAGIC
# MAGIC | | |
# MAGIC |---|---|
# MAGIC | **Status** | Public Preview (March 2026) |
# MAGIC | **Requires** | Runtime 18.0+, Unity Catalog managed tables, catalog-managed commits |
# MAGIC | **Docs** | [ATOMIC compound statement](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-txn-begin-atomic), [Transaction modes](https://docs.databricks.com/aws/en/transactions/transaction-modes) |
# MAGIC | **Data** | [Casper's Kitchens](https://github.com/databricks-solutions/caspers-kitchens) — a simulated ghost kitchen with deliveries, line items, and driver information |
# MAGIC
# MAGIC ### What this demo covers
# MAGIC 1. Create two summary tables from Casper's delivery data (kitchen revenue + driver stats)
# MAGIC 2. Use `BEGIN ATOMIC ... END` to update both tables in one atomic operation
# MAGIC 3. Show a deliberately failing transaction where both tables roll back cleanly

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup: Create two summary tables
# MAGIC
# MAGIC We'll create two tables that need to stay in sync:
# MAGIC - `kitchen_daily_revenue` — total revenue and order count per restaurant per day
# MAGIC - `driver_daily_stats` — deliveries completed and average duration per driver per day
# MAGIC
# MAGIC In a real system, these would be materialised summaries that get refreshed together. If one updates but the other doesn't, your reports disagree with each other.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS casper.demo_transactions;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE casper.demo_transactions.kitchen_daily_revenue AS
# MAGIC SELECT
# MAGIC   l.restaurant_name,
# MAGIC   DATE(d.delivery_start) AS order_date,
# MAGIC   COUNT(DISTINCT d.order_id) AS total_orders,
# MAGIC   SUM(l.total_price) AS total_revenue
# MAGIC FROM casper.kitchen_orders.deliveries d
# MAGIC JOIN casper.kitchen_orders.line_items l
# MAGIC   ON d.order_id = l.order_id
# MAGIC WHERE DATE(d.delivery_start) < '2026-03-01'
# MAGIC GROUP BY l.restaurant_name, DATE(d.delivery_start);

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE casper.demo_transactions.driver_daily_stats AS
# MAGIC SELECT
# MAGIC   d.driver_id,
# MAGIC   dr.contract_type,
# MAGIC   DATE(d.delivery_start) AS delivery_date,
# MAGIC   COUNT(*) AS deliveries_completed,
# MAGIC   ROUND(AVG(d.delivery_duration), 1) AS avg_delivery_mins,
# MAGIC   SUM(d.delivery_fee) AS total_fees_earned
# MAGIC FROM casper.kitchen_orders.deliveries d
# MAGIC JOIN casper.delivery_drivers.drivers dr
# MAGIC   ON d.driver_id = dr.driver_id
# MAGIC WHERE DATE(d.delivery_start) < '2026-03-01'
# MAGIC GROUP BY d.driver_id, dr.contract_type, DATE(d.delivery_start);

# COMMAND ----------

# MAGIC %md
# MAGIC Quick sanity check: what do these tables look like?

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM casper.demo_transactions.kitchen_daily_revenue
# MAGIC ORDER BY order_date DESC, total_revenue DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM casper.demo_transactions.driver_daily_stats
# MAGIC ORDER BY delivery_date DESC, deliveries_completed DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ## The problem: updating two tables without atomicity
# MAGIC
# MAGIC Imagine new delivery data comes in for March. You need to refresh both summary tables.
# MAGIC Without multi-table transactions, if the second statement fails (timeout, bad data, permissions issue),
# MAGIC your kitchen revenue table has March data but your driver stats table doesn't.
# MAGIC Now your revenue reports and driver performance reports tell different stories.

# COMMAND ----------

# MAGIC %md
# MAGIC ## The fix: BEGIN ATOMIC ... END
# MAGIC
# MAGIC Wrap both updates in an atomic block. Either both tables get the March data, or neither does.

# COMMAND ----------

# MAGIC %sql
# MAGIC BEGIN ATOMIC
# MAGIC
# MAGIC   INSERT INTO casper.demo_transactions.kitchen_daily_revenue
# MAGIC   SELECT
# MAGIC     l.restaurant_name,
# MAGIC     DATE(d.delivery_start) AS order_date,
# MAGIC     COUNT(DISTINCT d.order_id) AS total_orders,
# MAGIC     SUM(l.total_price) AS total_revenue
# MAGIC   FROM casper.kitchen_orders.deliveries d
# MAGIC   JOIN casper.kitchen_orders.line_items l
# MAGIC     ON d.order_id = l.order_id
# MAGIC   WHERE DATE(d.delivery_start) >= '2026-03-01'
# MAGIC   GROUP BY l.restaurant_name, DATE(d.delivery_start);
# MAGIC
# MAGIC   INSERT INTO casper.demo_transactions.driver_daily_stats
# MAGIC   SELECT
# MAGIC     d.driver_id,
# MAGIC     dr.contract_type,
# MAGIC     DATE(d.delivery_start) AS delivery_date,
# MAGIC     COUNT(*) AS deliveries_completed,
# MAGIC     ROUND(AVG(d.delivery_duration), 1) AS avg_delivery_mins,
# MAGIC     SUM(d.delivery_fee) AS total_fees_earned
# MAGIC   FROM casper.kitchen_orders.deliveries d
# MAGIC   JOIN casper.delivery_drivers.drivers dr
# MAGIC     ON d.driver_id = dr.driver_id
# MAGIC   WHERE DATE(d.delivery_start) >= '2026-03-01'
# MAGIC   GROUP BY d.driver_id, dr.contract_type, DATE(d.delivery_start);
# MAGIC
# MAGIC END;

# COMMAND ----------

# MAGIC %md
# MAGIC Both tables now have March data. Let's verify:

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'kitchen_daily_revenue' AS table_name,
# MAGIC        MIN(order_date) AS earliest,
# MAGIC        MAX(order_date) AS latest,
# MAGIC        COUNT(*) AS rows
# MAGIC FROM casper.demo_transactions.kitchen_daily_revenue
# MAGIC UNION ALL
# MAGIC SELECT 'driver_daily_stats',
# MAGIC        MIN(delivery_date),
# MAGIC        MAX(delivery_date),
# MAGIC        COUNT(*)
# MAGIC FROM casper.demo_transactions.driver_daily_stats;

# COMMAND ----------

# MAGIC %md
# MAGIC ## What happens when something fails?
# MAGIC
# MAGIC This is the important bit. Let's deliberately break the second statement
# MAGIC by referencing a column that doesn't exist. The first INSERT would succeed on its own,
# MAGIC but because it's inside an atomic block, it gets rolled back too.

# COMMAND ----------

# MAGIC %md
# MAGIC First, let's record the current row counts so we can prove nothing changed:

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'kitchen_daily_revenue' AS table_name, COUNT(*) AS row_count
# MAGIC FROM casper.demo_transactions.kitchen_daily_revenue
# MAGIC UNION ALL
# MAGIC SELECT 'driver_daily_stats', COUNT(*)
# MAGIC FROM casper.demo_transactions.driver_daily_stats;

# COMMAND ----------

# MAGIC %md
# MAGIC Now run the broken transaction:

# COMMAND ----------

# MAGIC %sql
# MAGIC BEGIN ATOMIC
# MAGIC
# MAGIC   -- This statement is valid
# MAGIC   INSERT INTO casper.demo_transactions.kitchen_daily_revenue
# MAGIC   VALUES ('Rollback Test Kitchen', '2099-12-31', 999, 99999.99);
# MAGIC
# MAGIC   -- This statement will fail: "fake_column" doesn't exist
# MAGIC   INSERT INTO casper.demo_transactions.driver_daily_stats
# MAGIC   SELECT fake_column FROM casper.delivery_drivers.drivers;
# MAGIC
# MAGIC END;

# COMMAND ----------

# MAGIC %md
# MAGIC That failed (as expected). Now check the row counts again. They should be identical to before — the valid first INSERT was rolled back along with the broken second one:

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'kitchen_daily_revenue' AS table_name, COUNT(*) AS row_count
# MAGIC FROM casper.demo_transactions.kitchen_daily_revenue
# MAGIC UNION ALL
# MAGIC SELECT 'driver_daily_stats', COUNT(*)
# MAGIC FROM casper.demo_transactions.driver_daily_stats;

# COMMAND ----------

# MAGIC %md
# MAGIC No "Rollback Test Kitchen" row. No partial state. Both tables stayed consistent.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM casper.demo_transactions.kitchen_daily_revenue
# MAGIC WHERE restaurant_name = 'Rollback Test Kitchen';

# COMMAND ----------

# MAGIC %md
# MAGIC ## Who is this for?
# MAGIC
# MAGIC **Use it if:**
# MAGIC - You maintain summary/aggregate tables that need to stay in sync
# MAGIC - You do cross-table data movements (staging → production)
# MAGIC - You need audit-safe updates where partial writes are unacceptable
# MAGIC
# MAGIC **Hold off if:**
# MAGIC - You're not on Runtime 18.0+ yet
# MAGIC - Your tables aren't Unity Catalog managed tables
# MAGIC - You need interactive transactions with manual COMMIT/ROLLBACK (that's a separate feature: `BEGIN TRANSACTION`)
# MAGIC - You're still in the "this is Public Preview and I don't want surprises" camp — fair enough
# MAGIC
# MAGIC **Docs:** [ATOMIC compound statement](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-txn-begin-atomic)
