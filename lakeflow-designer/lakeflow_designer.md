# 🎨 Lakeflow Designer

Visual, no-code data prep built directly into Databricks. Drag, drop, type in English, get a production-ready pipeline. No per-user license, no separate tool.

**Public Preview** — runs on serverless compute. A workspace admin must enable it in the preview portal first (it's not on by default yet).

[Docs](https://docs.databricks.com/aws/en/designer/) [Blog](https://www.databricks.com/blog/announcing-public-preview-lakeflow-designer) [Data Generator 👻](https://github.com/databricks-solutions/caspers-kitchens)

---

- **Enable first (one-time):** If "Visual data prep" isn't in the + New menu, a workspace admin needs to go to **Admin Settings → Previews** and turn on Lakeflow Designer.
- Click **+ New** in the workspace sidebar → select **Visual data prep**
- A blank canvas opens. Click **Add source** → search for `caspers_kitchen.simulator.items` → add it. Preview the data to show 181 menu items across all brands.
- Add a second source: `caspers_kitchen.simulator.brands`. Preview to show 24 ghost kitchen brands with cuisine types.
- Click the **+** after the items node → **Join**. Join items to brands on `brand_id`. Pick **inner join**. Preview the result — every item now has its brand name and cuisine type next to it.
- Click **+** after the join → **Aggregate**. Group by `brand_name` and `cuisine_type`. Add measures: `COUNT(item_name)` as `menu_size`, `ROUND(AVG(price), 2)` as `avg_price`. Preview: each brand reduced to one row with its menu size and average price.
- Click **+** → **Sort**. Sort by `menu_size` descending. Preview: McDoodles at the top (biggest menu), ScoopCity and FreshPress near the bottom.
- (Optional) Type in the AI prompt bar: "filter to brands with more than 5 items" — watch the operator appear on the canvas automatically.
- Click **Run all** to execute the full pipeline end-to-end. Point out the step-by-step data previews at each node.
- (Optional) Click **Schedule** to attach this as a Lakeflow Job — the visual pipeline generates real Python code under the hood, so it runs the same in production as it does on the canvas.
