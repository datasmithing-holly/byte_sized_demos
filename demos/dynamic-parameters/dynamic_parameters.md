# 🎛️ Dynamic Parameters in the SQL Editor

The SQL editor's new Dynamic dropdown widget type populates a parameter list from a saved query instead of a static list. When the underlying data changes, the dropdown updates automatically.

Requires the **new SQL editor** (not classic). SQL warehouse only (not notebooks).

[Docs](https://docs.databricks.com/aws/en/sql/user/sql-editor/parameter-widgets#dynamic-dropdown) [Data Generator 👻](https://github.com/databricks-solutions/caspers-kitchens)

---

## The problem

Static dropdown parameters go stale. Someone adds a new brand to the ghost kitchen empire and the dropdown still shows last month's list. You either maintain it by hand or people type wrong values.

Dynamic dropdowns fix this: point the widget at a saved query and the options stay current.

## Step 1: Create and save the source query

Open the SQL editor. Paste this and run it:

```sql
-- 👻 every brand in the ghost kitchen empire, always up to date
SELECT DISTINCT name FROM caspers_kitchen.simulator.brands ORDER BY name
```

Save it as **Brand List** (Ctrl/Cmd + S).

This is the query the dropdown will pull from. Any time a new brand gets onboarded, it shows up here automatically.

## Step 2: Create the main query

Open a new SQL editor tab. Paste this:

```sql
-- 🍔 what's on the menu?
SELECT i.name AS item, i.price, b.cuisine_type
FROM caspers_kitchen.simulator.items i
JOIN caspers_kitchen.simulator.brands b ON i.brand_id = b.brand_id
WHERE b.name = :brand
ORDER BY i.price DESC
```

A `:brand` parameter widget appears above the results pane.

## Step 3: Wire up the dynamic dropdown

1. Click the **gear icon** (⚙️) next to the `:brand` widget
2. Set **Widget type** → Dynamic dropdown
3. In the **Query** field, select the **Brand List** query you saved in step 1
4. Pick a **Default parameter value** (try McDoodles, they have 15 items)
5. Click **Apply Changes**

Run the query. The dropdown now lists every brand from the saved query.

## Step 4: See it stay current

Pick different brands from the dropdown and re-run. Notice:

- **McDoodles** has 15 items (of course they do)
- **NootroNourish** has 4 items and a cuisine type of "Nootropic Cafe" (for when you want your lunch to also be a brain supplement)
- **The Golden Falafel** has 0 items because it was just onboarded via a multi-table transaction and hasn't built its menu yet

If someone adds a new brand to `caspers_kitchen.simulator.brands`, it appears in the dropdown next time you open it. No widget editing needed.

## Cleanup

Nothing to clean up. Both queries live in your saved queries and can be deleted from there if you want.
