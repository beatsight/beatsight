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
