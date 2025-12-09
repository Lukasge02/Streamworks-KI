"""
Schedule Generator Service
Converts natural language scheduling to Streamworks ScheduleRuleXml format
"""
from datetime import datetime
from typing import Optional


def generate_schedule_xml(
    schedule: Optional[str] = None,
    start_time: Optional[str] = None
) -> str:
    """
    Generate ScheduleRuleXml based on natural language schedule description
    
    Args:
        schedule: Natural language schedule (e.g., "täglich", "wöchentlich", "monatlich")
        start_time: Start time in HH:MM format (e.g., "08:00")
    
    Returns:
        ScheduleRuleXml string for Streamworks
    """
    
    if not schedule:
        # Default: No scheduling, manual trigger only
        return '''&lt;SchedulingRules ShiftRule=&quot;3&quot; ScheduleRuleDialogNotYetVisited=&quot;1&quot;&gt;
  &lt;FixedDates /&gt;
&lt;/SchedulingRules&gt;'''
    
    schedule_lower = schedule.lower()
    
    # Parse start time
    time_part = ""
    if start_time:
        try:
            # Validate time format
            hour, minute = start_time.split(":")
            time_part = f' StartTime=&quot;{start_time}&quot;'
        except:
            pass
    
    # Daily schedule
    if any(word in schedule_lower for word in ["täglich", "daily", "jeden tag", "tag"]):
        return f'''&lt;SchedulingRules ShiftRule=&quot;3&quot;&gt;
  &lt;ScheduleMonths All=&quot;Yes&quot; /&gt;
  &lt;ScheduleDays All=&quot;Yes&quot;{time_part} /&gt;
&lt;/SchedulingRules&gt;'''
    
    # Weekly schedule
    if any(word in schedule_lower for word in ["wöchentlich", "weekly", "jede woche"]):
        # Default: Monday
        weekday = "Mon"
        for day, code in [("montag", "Mon"), ("dienstag", "Tue"), ("mittwoch", "Wed"), 
                          ("donnerstag", "Thu"), ("freitag", "Fri"), ("samstag", "Sat"), ("sonntag", "Sun")]:
            if day in schedule_lower:
                weekday = code
                break
        
        return f'''&lt;SchedulingRules ShiftRule=&quot;3&quot;&gt;
  &lt;ScheduleMonths All=&quot;Yes&quot; /&gt;
  &lt;ScheduleWeekdays {weekday}=&quot;Yes&quot;{time_part} /&gt;
&lt;/SchedulingRules&gt;'''
    
    # Monthly schedule
    if any(word in schedule_lower for word in ["monatlich", "monthly", "jeden monat"]):
        # Default: 1st of month
        day_of_month = "1"
        return f'''&lt;SchedulingRules ShiftRule=&quot;3&quot;&gt;
  &lt;ScheduleMonths All=&quot;Yes&quot; /&gt;
  &lt;ScheduleMonthDays Day{day_of_month}=&quot;Yes&quot;{time_part} /&gt;
&lt;/SchedulingRules&gt;'''
    
    # Hourly schedule
    if any(word in schedule_lower for word in ["stündlich", "hourly", "jede stunde"]):
        return f'''&lt;SchedulingRules ShiftRule=&quot;3&quot;&gt;
  &lt;ScheduleMonths All=&quot;Yes&quot; /&gt;
  &lt;ScheduleIntervals IntervalMinutes=&quot;60&quot; /&gt;
&lt;/SchedulingRules&gt;'''
    
    # Workdays only (Mo-Fr)
    if any(word in schedule_lower for word in ["werktags", "workdays", "mo-fr", "montag bis freitag"]):
        return f'''&lt;SchedulingRules ShiftRule=&quot;3&quot;&gt;
  &lt;ScheduleMonths All=&quot;Yes&quot; /&gt;
  &lt;ScheduleWeekdays Mon=&quot;Yes&quot; Tue=&quot;Yes&quot; Wed=&quot;Yes&quot; Thu=&quot;Yes&quot; Fri=&quot;Yes&quot;{time_part} /&gt;
&lt;/SchedulingRules&gt;'''
    
    # Default fallback
    return f'''&lt;SchedulingRules ShiftRule=&quot;3&quot;&gt;
  &lt;ScheduleMonths All=&quot;Yes&quot; /&gt;
  &lt;ScheduleDays All=&quot;Yes&quot;{time_part} /&gt;
&lt;/SchedulingRules&gt;'''
