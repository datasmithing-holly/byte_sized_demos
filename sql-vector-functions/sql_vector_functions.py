# Databricks notebook source
# MAGIC %md
# MAGIC # 🧲 SQL Vector Functions
# MAGIC Find menu item doppelgangers across Casper's ghost kitchens using embedding math in pure SQL. No Python, no UDFs, no leaving the warehouse.
# MAGIC
# MAGIC Requires **Runtime 18.1+** and a SQL warehouse or cluster with AI Functions enabled.
# MAGIC
# MAGIC [Docs](https://docs.databricks.com/aws/en/sql/language-manual/functions/vector_cosine_similarity.html) [Data Generator 👻](https://github.com/databricks-solutions/caspers-kitchens)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 🏗️ setup: embed every menu item name (takes ~30s, only needs to run once before recording)
# MAGIC CREATE SCHEMA IF NOT EXISTS caspers_kitchen.demo_vectors;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE caspers_kitchen.demo_vectors.item_embeddings AS
# MAGIC SELECT
# MAGIC   i.id,
# MAGIC   i.name AS item_name,
# MAGIC   b.name AS brand_name,
# MAGIC   b.cuisine_type,
# MAGIC   i.price,
# MAGIC   CAST(ai_query('databricks-gte-large-en', i.name) AS ARRAY<FLOAT>) AS embedding
# MAGIC FROM caspers_kitchen.simulator.items i
# MAGIC JOIN caspers_kitchen.simulator.brands b ON i.brand_id = b.brand_id;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 🔍 which items across ALL brands are closest to McDoodles' "Big Stack"?
# MAGIC WITH target AS (
# MAGIC   SELECT embedding FROM caspers_kitchen.demo_vectors.item_embeddings WHERE item_name = 'Big Stack'
# MAGIC )
# MAGIC SELECT
# MAGIC   ie.item_name,
# MAGIC   ie.brand_name,
# MAGIC   ie.cuisine_type,
# MAGIC   ie.price,
# MAGIC   ROUND(vector_cosine_similarity(ie.embedding, t.embedding), 4) AS similarity
# MAGIC FROM caspers_kitchen.demo_vectors.item_embeddings ie
# MAGIC CROSS JOIN target t
# MAGIC WHERE ie.item_name != 'Big Stack'
# MAGIC ORDER BY similarity DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 🎯 which brands have the most similar menus? average each brand's embeddings into a single "vibe vector" and compare
# MAGIC WITH brand_vibes AS (
# MAGIC   SELECT
# MAGIC     brand_name,
# MAGIC     cuisine_type,
# MAGIC     vector_avg(embedding) AS vibe
# MAGIC   FROM caspers_kitchen.demo_vectors.item_embeddings
# MAGIC   GROUP BY brand_name, cuisine_type
# MAGIC )
# MAGIC SELECT
# MAGIC   a.brand_name AS brand_a,
# MAGIC   b.brand_name AS brand_b,
# MAGIC   a.cuisine_type AS cuisine_a,
# MAGIC   b.cuisine_type AS cuisine_b,
# MAGIC   ROUND(vector_cosine_similarity(a.vibe, b.vibe), 4) AS menu_similarity
# MAGIC FROM brand_vibes a
# MAGIC CROSS JOIN brand_vibes b
# MAGIC WHERE a.brand_name < b.brand_name
# MAGIC ORDER BY menu_similarity DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 🧹 cleanup
# MAGIC DROP SCHEMA IF EXISTS caspers_kitchen.demo_vectors CASCADE;
