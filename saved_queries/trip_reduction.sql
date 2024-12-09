select count(trip_id) from bike_trips
where 
  date(start_time) >= date('2024-07-01') AND date(start_time) < date('2024-08-01')
  AND (
    cast(start_time as time) >= '07:00:00' and cast(start_time as time) <= '09:00:00'
    OR
    cast(start_time as time) >= '16:00:00' and cast(start_time as time) <= '18:00:00'
  )
limit 10