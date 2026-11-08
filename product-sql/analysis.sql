-- 1) Event counts and unique users
SELECT event_name, COUNT(*) AS events, COUNT(DISTINCT user_id) AS users
FROM events
GROUP BY event_name
ORDER BY CASE event_name WHEN 'view' THEN 1 WHEN 'signup' THEN 2 ELSE 3 END;

-- 2) User-level funnel. This simple definition does not enforce event order.
WITH user_flags AS (
  SELECT user_id,
         MAX(event_name = 'view') AS viewed,
         MAX(event_name = 'signup') AS signed_up,
         MAX(event_name = 'purchase') AS purchased
  FROM events
  GROUP BY user_id
)
SELECT COUNT(*) AS users,
       SUM(viewed) AS viewed,
       SUM(signed_up) AS signed_up,
       SUM(purchased) AS purchased,
       ROUND(1.0 * SUM(signed_up) / NULLIF(SUM(viewed), 0), 4) AS view_to_signup,
       ROUND(1.0 * SUM(purchased) / NULLIF(SUM(signed_up), 0), 4) AS signup_to_purchase
FROM user_flags;

-- 3) Signup cohorts and day-1/day-7 return (calendar-day definition)
WITH first_signup AS (
  SELECT user_id, MIN(date(event_time)) AS cohort_date
  FROM events WHERE event_name = 'signup' GROUP BY user_id
), activity AS (
  SELECT DISTINCT user_id, date(event_time) AS activity_date
  FROM events
), cohort_sizes AS (
  SELECT cohort_date, COUNT(*) AS cohort_users FROM first_signup GROUP BY cohort_date
), returns AS (
  SELECT f.cohort_date,
         SUM(CASE WHEN julianday(a.activity_date)-julianday(f.cohort_date)=1 THEN 1 ELSE 0 END) AS d1_users,
         SUM(CASE WHEN julianday(a.activity_date)-julianday(f.cohort_date)=7 THEN 1 ELSE 0 END) AS d7_users
  FROM first_signup f LEFT JOIN activity a ON a.user_id=f.user_id
  GROUP BY f.cohort_date
)
SELECT r.cohort_date, c.cohort_users,
       ROUND(1.0*r.d1_users/c.cohort_users, 4) AS d1_retention,
       ROUND(1.0*r.d7_users/c.cohort_users, 4) AS d7_retention
FROM returns r JOIN cohort_sizes c USING(cohort_date)
ORDER BY r.cohort_date;

-- 4) Window function: order each user's events chronologically
SELECT user_id, event_name, event_time,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time) AS event_number,
       LAG(event_name) OVER (PARTITION BY user_id ORDER BY event_time) AS previous_event
FROM events
ORDER BY user_id, event_time
LIMIT 30;
