# Databricks notebook source
# MAGIC %md
# MAGIC # 🦎 INSERT WITH SCHEMA EVOLUTION
# MAGIC New columns show up in the source data? The table grows to fit. No ALTER TABLE, no coordination, no downtime.
# MAGIC
# MAGIC Requires **Runtime 18.1+** and Unity Catalog **managed tables**.
# MAGIC
# MAGIC [Docs](https://docs.databricks.com/aws/en/delta/update-schema.html#schema-evolution-insert) [Data Generator 👻](https://github.com/databricks-solutions/caspers-kitchens)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 🏗️ setup: clone the items table so we have something to evolve
# MAGIC CREATE SCHEMA IF NOT EXISTS caspers_kitchen.demo_schema_evo;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE caspers_kitchen.demo_schema_evo.items
# MAGIC AS SELECT * FROM caspers_kitchen.simulator.items;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 📋 six columns. no vibes. no regret tracking. just food.
# MAGIC DESCRIBE caspers_kitchen.demo_schema_evo.items;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 🚫 a reviewer shows up with extra columns. normal INSERT says absolutely not.
# MAGIC INSERT INTO caspers_kitchen.demo_schema_evo.items
# MAGIC SELECT
# MAGIC   id, category_id, menu_id, brand_id, name, price,
# MAGIC   CASE
# MAGIC     WHEN price > 12 THEN 'main character energy'
# MAGIC     WHEN price > 8 THEN 'solid choice'
# MAGIC     WHEN price > 5 THEN 'sleeper hit'
# MAGIC     ELSE 'why is this on the menu'
# MAGIC   END AS vibe_check,
# MAGIC   CAST(price * 2.5 AS INT) AS estimated_regret_minutes
# MAGIC FROM caspers_kitchen.simulator.items
# MAGIC WHERE brand_id = 1;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- ✅ same INSERT, two extra words, and the table grows to fit
# MAGIC INSERT WITH SCHEMA EVOLUTION INTO caspers_kitchen.demo_schema_evo.items
# MAGIC SELECT
# MAGIC   id, category_id, menu_id, brand_id, name, price,
# MAGIC   CASE
# MAGIC     WHEN price > 12 THEN 'main character energy'
# MAGIC     WHEN price > 8 THEN 'solid choice'
# MAGIC     WHEN price > 5 THEN 'sleeper hit'
# MAGIC     ELSE 'why is this on the menu'
# MAGIC   END AS vibe_check,
# MAGIC   CAST(price * 2.5 AS INT) AS estimated_regret_minutes
# MAGIC FROM caspers_kitchen.simulator.items
# MAGIC WHERE brand_id = 1;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 📋 eight columns now. vibe_check and estimated_regret_minutes just appeared.
# MAGIC DESCRIBE caspers_kitchen.demo_schema_evo.items;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 👀 original rows got NULLs for the new columns. McDoodles rows have values.
# MAGIC SELECT name, price, vibe_check, estimated_regret_minutes
# MAGIC FROM caspers_kitchen.demo_schema_evo.items
# MAGIC ORDER BY vibe_check IS NULL, estimated_regret_minutes DESC
# MAGIC LIMIT 15;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 🧹 cleanup
# MAGIC DROP SCHEMA IF EXISTS caspers_kitchen.demo_schema_evo CASCADE;
