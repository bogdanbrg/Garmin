# Intermediate Layer

## Purpose

The intermediate layer sits between staging and marts in our dbt project structure:

```
staging → intermediate → marts
```

This layer is designed for:

1. **Business Logic Transformations**: Apply business rules and logic that transform staging data into more meaningful entities
2. **Joining Staging Models**: Combine multiple staging models to create enriched datasets
3. **Reusable Building Blocks**: Create models that can be referenced by multiple marts, reducing redundancy
4. **Data Quality & Filtering**: Apply consistent filters and quality checks before data reaches marts

## Models in This Layer

### int_activities_enriched

Combines activity data with weather and gear information to create a comprehensive view of each activity.

**Sources:**
- `stg_activities`: Core activity metrics
- `stg_activity_weather`: Weather conditions during activities
- `stg_activity_gear`: Gear used for activities

**Usage Example:**
This model is used by the `activity_summary` mart to provide business-ready activity analytics.

## Naming Convention

All intermediate models follow the naming pattern: `int_<entity>_<description>`

Examples:
- `int_activities_enriched`
- `int_gear_lifecycle`
- `int_performance_metrics`

## Materialization

Intermediate models are materialized as **views** by default (configured in `dbt_project.yml`). This is because:
- They are typically used by one or a few marts
- Views ensure data freshness without storage overhead
- If performance becomes an issue, specific models can be changed to tables using `{{ config(materialized='table') }}`

## When to Add a New Intermediate Model

Add a new intermediate model when:

1. Multiple marts need the same joined or transformed data
2. Complex business logic should be isolated from marts
3. You want to create a reusable entity that doesn't fit in staging or marts
4. You need to apply consistent data quality rules across multiple marts

## Best Practices

- Keep business logic here, not in staging (staging = light cleaning only)
- Document all transformations in model descriptions
- Use CTEs for readability
- Add data tests in schema.yml
- Consider performance implications of complex joins
