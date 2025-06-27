# 🏗️ Kiến trúc Bot Nông Trại

## 📊 Tổng quan hệ thống

```
Discord Bot (bot.py)
├── Database Layer (database/)
│   ├── database.py - Connection & queries
│   └── models.py - Data models
├── Features (features/)
│   ├── profile.py - User management
│   ├── farm.py - Core farming + sell logic
│   ├── shop.py - Shopping system
│   ├── daily.py - Daily rewards
│   ├── weather.py - Weather + notifications
│   ├── events.py - Seasonal/random events
│   └── leaderboard.py - Rankings
└── Utils (utils/)
    ├── embeds.py - Discord UI builders
    └── helpers.py - Game calculations
```

## 🔄 Task Scheduling

### Current Tasks
1. **WeatherCog** 
   - `weather_notification_task`: 30 phút
   - `market_notification_task`: 15 phút
2. **EventsCog**
   - `check_events`: 1 giờ

### Task Dependencies
- Market notifications cần weather và event data
- Weather task có rate limiting (900 calls/day)
- Event task độc lập

## 🎯 Data Flow

### Price Calculation Flow
```
1. User calls f!sell
2. FarmCog gets weather modifier from WeatherCog
3. FarmCog gets event modifier from EventsCog
4. calculate_crop_price() applies modifiers
5. Update database & send result
```

### Notification Flow
```
1. market_notification_task (15 min)
2. Get weather modifier from weather API/cache
3. Get event modifier from EventsCog
4. Calculate combined modifier
5. Compare with threshold -> Send notification if changed
6. Update database with new modifier
```

## ⚡ Integration Points

### WeatherCog ↔ FarmCog
- `get_current_weather_modifier()` → returns (growth_mod, yield_mod)
- Used in: sell command, market command

### EventsCog ↔ FarmCog  
- `get_current_price_modifier()` → returns price bonus
- `current_event` → event data access
- Used in: sell command, market command

### EventsCog ↔ WeatherCog
- `get_current_price_modifier()` → for market notifications
- `current_event` → for notification details

## 🚨 Critical Dependencies

### API Rate Limits
- OpenWeatherMap: 900 calls/day
- Cache duration: 30 minutes
- Fallback: Mock data if limit exceeded

### Database Constraints
- Users table: Primary key user_id
- Crops table: Foreign key to users
- Notifications: One per guild

## 🔧 Best Practices

### Error Handling
- Always check if cogs exist before accessing
- Graceful degradation for missing APIs
- Default values for all modifiers

### Performance
- Cache weather data (30 min)
- Batch database operations
- Minimize cross-cog dependencies

### Consistency
- Use utility methods for complex logic
- Centralize price calculations
- Standardize embed creation

## 🛡️ Safety Measures

### Rate Limiting
- Track daily API calls
- Reset counter at midnight
- Return cached/mock data when limited

### Data Validation
- Validate plot indices
- Check user permissions
- Verify channel access

### Error Recovery
- Handle division by zero
- Fallback to default modifiers
- Graceful task failures

## 📈 Scaling Considerations

### Current Limitations
- Single SQLite database
- In-memory caching
- No horizontal scaling

### Future Improvements
- PostgreSQL for multi-server
- Redis for caching
- Separate notification service
- Event-driven architecture 