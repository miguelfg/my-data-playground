-- FLUSH TABLE offers_last_seen_available
--
DELETE * FROM offers_last_seen_available;


INSERT FROM seizures
WHERE rowid NOT IN
    (
    SELECT *
    FROM offers_history
    GROUP BY car_vin
    ORDER BY last_seen DESC;
    )
    
