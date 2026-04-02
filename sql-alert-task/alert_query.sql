-- 🕵️ brands that got onboarded without a menu (data quality check)
SELECT b.name AS brand, b.cuisine_type, COUNT(i.id) AS item_count
FROM caspers_kitchen.simulator.brands b
LEFT JOIN caspers_kitchen.simulator.items i ON b.brand_id = i.brand_id
GROUP BY b.name, b.cuisine_type
HAVING COUNT(i.id) = 0
