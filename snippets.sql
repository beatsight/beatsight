D select author_email, count(distinct(author_name)) as name_cnt  from gemserver group by author_email ;
┌──────────────────────────┬──────────┐
│       author_email       │ name_cnt │
│         varchar          │  int64   │
├──────────────────────────┼──────────┤
│ lxy2325@126.com          │        1 │
│ xingyu.li@17zuoye.com    │        1 │
│ lei.yang@17zuoye.com     │        2 │
│ xiez1989@gmail.com       │        1 │

D select author_email, count(distinct(author_name)) as name_cnt, string_agg(distinct(author_name), ', ') as author_names  from gemserver group by author_email ;
┌──────────────────────────┬──────────┬─────────────────┐
│       author_email       │ name_cnt │  author_names   │
│         varchar          │  int64   │     varchar     │
├──────────────────────────┼──────────┼─────────────────┤
│ hui.wu.a@17zuoye.com     │        2 │ hui.wu.a, 吴辉A │
│ baiqiang.wen@17zuoye.com │        1 │ baiqiang wen    │
│ xin.xin@17zuoye.com      │        2 │ xin.xin, 信新   │


-- list a user's commit count for the past two years
SELECT project, SUM(daily_commit_count) AS total_commits
FROM (
  SELECT *
  FROM author_daily_commits
  WHERE author_email = 'xie.zheng@17zuoye.com'
  AND author_date BETWEEN '2022-05-01' AND '2024-05-01'
)
GROUP BY project;

│  project  │ total_commits │
│  varchar  │    int128     │
├───────────┼───────────────┤
│ sicp      │             4 │
│ gemserver │            37 │

-- user's commit count distribution for the past two years
SELECT 
  author_email, 
 'xie.zheng' AS author_name,
  author_date,
  SUM(daily_commit_count) AS daily_commit_count_sum
FROM author_daily_commits
WHERE author_email = 'xie.zheng@17zuoye.com'
  AND author_date BETWEEN '2022-05-23' AND '2024-05-23'
GROUP BY author_email, author_date;

┌───────────────────────┬─────────────┬─────────────┬────────────────────────┐
│     author_email      │ author_name │ author_date │ daily_commit_count_sum │
│        varchar        │   varchar   │    date     │         int128         │
├───────────────────────┼─────────────┼─────────────┼────────────────────────┤
│ xie.zheng@17zuoye.com │ xie.zheng   │ 2022-10-09  │                      1 │
│ xie.zheng@17zuoye.com │ xie.zheng   │ 2022-10-31  │                      3 │
│ xie.zheng@17zuoye.com │ xie.zheng   │ 2022-08-19  │                      4 │
│ xie.zheng@17zuoye.com │ xie.zheng   │ 2022-08-30  │                      2 │
│ xie.zheng@17zuoye.com │ xie.zheng   │ 2022-08-31  │                      1 │
│ xie.zheng@17zuoye.com │ xie.zheng   │ 2022-09-05  │                      2 │
│ xie.zheng@17zuoye.com │ xie.zheng   │ 2022-09-20  │                      2 │

-- all user's commit count distribution in a project

SELECT author_email, FIRST(author_name) AS author_name, COUNT(*) AS commit_count,
       CAST(TO_TIMESTAMP(min(author_timestamp)) AS DATETIME) AS first_commit_datetime,
       CAST(TO_TIMESTAMP(max(author_timestamp)) AS DATETIME) AS lastest_commit_datetime,
FROM sicp
GROUP BY author_email
ORDER BY commit_count DESC;


-- author contribution order by commit count in a project
D select author_email, sum(daily_commit_count) as daily_commit_count_sum from author_daily_commits where project = 'gemserver' group by author_email order by daily_commit_count_sum desc;
┌──────────────────────────┬────────────────────────┐
│       author_email       │ daily_commit_count_sum │
│         varchar          │         int128         │
├──────────────────────────┼────────────────────────┤
│ hui.wu.a@17zuoye.com     │                    192 │
│ xin.xin@17zuoye.com      │                    180 │
│ xingyu.li@17zuoye.net    │                    160 │
│ liming.ma@17zuoye.com    │                    135 │
│ baiqiang.wen@17zuoye.com │                    110 │
│ maliming0121@126.com     │                     95 │
│ xie.zheng@17zuoye.com    │                     37 │
│ lei.yang@17zuoye.com     │                     37 │
│ sirun.wang@17zuoye.net   │                     24 │
│ lxy2325@126.com          │                      9 │
│ mrsmish@yahoo.com        │                      7 │

-- an author's daily commit distribution

D select * from author_daily_commits where project = 'gemserver' and author_email = 'xie.zheng@17zuoye.com' order by author_date;

┌───────────────────────┬─────────────┬────────────────────┬───────────┐
│     author_email      │ author_date │ daily_commit_count │  project  │
│        varchar        │    date     │       int32        │  varchar  │
├───────────────────────┼─────────────┼────────────────────┼───────────┤
│ xie.zheng@17zuoye.com │ 2022-08-18  │                  2 │ gemserver │
│ xie.zheng@17zuoye.com │ 2022-08-19  │                  4 │ gemserver │
│ xie.zheng@17zuoye.com │ 2022-08-30  │                  2 │ gemserver │
│ xie.zheng@17zuoye.com │ 2022-08-31  │                  1 │ gemserver │
│ xie.zheng@17zuoye.com │ 2022-09-05  │                  2 │ gemserver │
│ xie.zheng@17zuoye.com │ 2022-09-08  │                  4 │ gemserver │
│ xie.zheng@17zuoye.com │ 2022-09-20  │                  2 │ gemserver │
│ xie.zheng@17zuoye.com │ 2022-09-23  │                  1 │ gemserver │


select author_date, SUM(daily_commit_count) as daily_commit_count
from author_daily_commits
where project = 'gemserver' and author_email = 'xie.zheng@17zuoye.com'
group by author_date order by author_date;
