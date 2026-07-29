# SQL 入门：SELECT、WHERE 和 JOIN

## SELECT

`SELECT` 用来查询字段。`SELECT name, score FROM students;` 表示从学生表里取姓名和成绩。

## WHERE

`WHERE` 用来过滤数据。`WHERE score >= 60` 只返回及格记录。多个条件可以用 `AND` 和 `OR` 组合。

## ORDER BY 和 LIMIT

`ORDER BY score DESC` 按成绩从高到低排序。`LIMIT 10` 只取前 10 条。

## JOIN

`JOIN` 用来把多张表按关联字段连起来。订单表和用户表可以通过 `user_id` 关联，查询用户姓名和订单金额。

## 练习

设计 `students` 和 `courses` 两张表，查询每个学生选择了哪些课程，并按学生姓名排序。
