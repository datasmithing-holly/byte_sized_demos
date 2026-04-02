# 🚨 SQL Alert Task for Jobs

You can now add a SQL alert as a task in a Databricks job. The job evaluates the alert condition as part of your workflow, so data quality checks and threshold monitors run alongside your pipeline instead of on a separate schedule.

**Beta** - workspace admin needs to enable the preview first. Requires a serverless or pro SQL warehouse.

[Docs](https://docs.databricks.com/aws/en/jobs/alert) [Data Generator 👻](https://github.com/databricks-solutions/caspers-kitchens)

---

- Create a new alert: paste `alert_query.sql` into the alert editor (finds brands with no menu items). Set condition to **Count** of **brand** > **0**, pick the serverless warehouse, add yourself as subscriber
- Save the alert and give it a name (e.g. "🕵️ Menuless Brands")
- Create a new job: Jobs & Pipelines → Create → Job
- Click **Add another task type** → search **SQL Alert** → select it
- Pick the alert you just created, optionally override the warehouse and subscribers
- Run the job. The Golden Falafel triggers the alert (onboarded via multi-table transaction, still no menu)
- The task **succeeds** either way. "Succeeded" means the alert evaluated without errors, not that the condition was OK. Check the alert status separately for TRIGGERED vs OK.
