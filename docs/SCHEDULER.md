# Query Scheduler Documentation

## Overview

The Discoverer includes a powerful query scheduling system that allows you to automatically execute queries at specified intervals. This is useful for:
- Regular reports
- Data synchronization checks
- Automated monitoring
- Periodic data analysis

## Features

- **Multiple Schedule Frequencies**: Hourly, Daily, Weekly, Monthly, or Custom (Cron)
- **Schedule Management**: Create, pause, resume, and delete schedules
- **Execution Tracking**: Track run count, success/failure rates
- **Manual Execution**: Trigger schedules manually at any time
- **Background Processing**: Scheduler runs automatically in the background

## API Endpoints

### Create Schedule

```bash
POST /api/scheduler
Content-Type: application/json

{
    "name": "Daily User Report",
    "query": "Count users created today",
    "frequency": "daily",
    "schedule": "0 9 * * *",  # 9 AM daily
    "database_ids": ["db1"],
    "description": "Daily user count report"
}
```

**Frequencies:**
- `once` - Run once (far future)
- `hourly` - Every hour
- `daily` - Every day
- `weekly` - Every week
- `monthly` - Every month
- `custom` - Custom cron expression

### List Schedules

```bash
GET /api/scheduler?status=active&page=1&page_size=20
```

**Query Parameters:**
- `status` - Filter by status (active, paused, completed, failed)
- `page` - Page number
- `page_size` - Items per page

### Execute Schedule Manually

```bash
POST /api/scheduler/{schedule_id}/execute
```

### Pause Schedule

```bash
POST /api/scheduler/{schedule_id}/pause
```

### Resume Schedule

```bash
POST /api/scheduler/{schedule_id}/resume
```

### Delete Schedule

```bash
DELETE /api/scheduler/{schedule_id}
```

## Schedule Status

- **active** - Schedule is running and will execute at scheduled times
- **paused** - Schedule is temporarily disabled
- **completed** - One-time schedule has completed
- **failed** - Schedule has encountered too many failures

## Cron Expression Format

For custom schedules, use standard cron format:
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

**Examples:**
- `0 9 * * *` - Every day at 9:00 AM
- `0 */2 * * *` - Every 2 hours
- `0 0 * * 0` - Every Sunday at midnight
- `0 0 1 * *` - First day of every month at midnight

## Response Format

```json
{
    "id": "schedule-uuid",
    "name": "Daily User Report",
    "description": "Daily user count report",
    "query": "Count users created today",
    "database_ids": ["db1"],
    "schedule": "0 9 * * *",
    "frequency": "daily",
    "status": "active",
    "last_run_at": "2024-01-15T09:00:00Z",
    "next_run_at": "2024-01-16T09:00:00Z",
    "run_count": 10,
    "success_count": 9,
    "failure_count": 1
}
```

## Best Practices

1. **Use Descriptive Names**: Name schedules clearly for easy identification
2. **Monitor Failures**: Check `failure_count` regularly
3. **Pause When Needed**: Pause schedules during maintenance
4. **Test First**: Test queries manually before scheduling
5. **Consider Load**: Distribute schedules to avoid peak times
6. **Use Parameters**: For parameterized queries, use query templates

## Limitations

- Scheduler checks for due schedules every 60 seconds
- Maximum concurrent executions: Limited by query service
- In-memory storage: Schedules are stored in memory (persistent storage can be added)

## Future Enhancements

- Persistent storage for schedules
- Email notifications on failure
- Schedule dependencies
- Schedule groups
- Execution history storage
- Retry logic for failed schedules


