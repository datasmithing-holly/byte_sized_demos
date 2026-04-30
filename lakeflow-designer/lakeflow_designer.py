# Databricks notebook source
# MAGIC %md
# MAGIC # 🎨 Lakeflow Designer
# MAGIC Visual, no-code data prep built directly into Databricks. Drag, drop, type in English, get a production-ready pipeline. No Alteryx license required.
# MAGIC
# MAGIC **Public Preview** — runs on serverless compute. Admin may need to enable it in the preview portal.
# MAGIC
# MAGIC [Docs](https://docs.databricks.com/aws/en/designer/) [Blog](https://www.databricks.com/blog/announcing-public-preview-lakeflow-designer) [Data Generator 👻](https://github.com/databricks-solutions/caspers-kitchens)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Open Designer
# MAGIC Click **+ New** in the workspace sidebar → select **Visual data prep**. A blank canvas opens.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Add sources
# MAGIC - Click **Add source** → search for `caspers_kitchen.simulator.items` → add it. Preview: 181 menu items across all ghost kitchen brands.
# MAGIC - Add a second source: `caspers_kitchen.simulator.brands`. Preview: 24 brands with cuisine types and prep times.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Join items to brands
# MAGIC Click the **+** after the items node → **Join**. Join items to brands on `brand_id`. Pick **inner join**. Preview the result — every item now has its brand name and cuisine type next to it.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Aggregate
# MAGIC Click **+** after the join → **Aggregate**. Group by `brand_name` and `cuisine_type`. Add measures:
# MAGIC - `COUNT(item_name)` as `menu_size`
# MAGIC - `ROUND(AVG(price), 2)` as `avg_price`
# MAGIC
# MAGIC Preview: each brand reduced to one row with its menu size and average price.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Sort
# MAGIC Click **+** → **Sort**. Sort by `menu_size` descending. Preview: McDoodles at the top (biggest menu), ScoopCity and FreshPress near the bottom.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Ask the AI
# MAGIC Type in the AI prompt bar: **"filter to brands with more than 5 items"** — watch the operator appear on the canvas automatically. This is the Genie Code moment.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Run it
# MAGIC Click **Run all** to execute the full pipeline end-to-end. Point out the step-by-step data previews at each node — this is what makes AI-generated transforms reviewable.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Schedule (optional)
# MAGIC Click **Schedule** to attach this as a Lakeflow Job. The visual pipeline generates real Python code under the hood, so it runs the same in production as it does on the canvas. No rewrite needed.
