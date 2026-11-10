import {
  startOfMonth, endOfMonth, startOfWeek, endOfWeek,
  eachDayOfInterval, isSameMonth, isSameDay, format, isToday
} from 'date-fns';
import type { CalendarEvent, Task } from '../../types';

interface CalendarGridProps {
  currentDate: Date;
  events: CalendarEvent[];
  taskDeadlines: Task[];
  onDateClick: (date: Date) => void;
  onEventClick: (event: CalendarEvent) => void;
}

export function CalendarGrid({ currentDate, events, taskDeadlines, onDateClick, onEventClick }: CalendarGridProps) {
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const gridStart = startOfWeek(monthStart, { weekStartsOn: 1 });
  const gridEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
  const days = eachDayOfInterval({ start: gridStart, end: gridEnd });

  const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  return (
    <div className="select-none">
      <div className="grid grid-cols-7 mb-1">
        {WEEKDAYS.map((d) => (
          <div key={d} className="text-center text-xs font-medium text-text-muted py-2">{d}</div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {days.map((day) => {
          const dayEvents = events.filter((e) => isSameDay(new Date(e.startTime), day));
          const dayDeadlines = taskDeadlines.filter(
            (t) => t.dueDate && isSameDay(new Date(t.dueDate), day)
          );
          const inCurrentMonth = isSameMonth(day, currentDate);
          const today = isToday(day);

          return (
            <div
              key={day.toISOString()}
              onClick={() => onDateClick(day)}
              className={`min-h-[90px] rounded-lg p-1.5 cursor-pointer border transition-colors ${
                today
                  ? 'border-accent bg-accent/10'
                  : 'border-surface-border hover:border-accent/40 hover:bg-surface-hover'
              } ${!inCurrentMonth ? 'opacity-30' : ''}`}
            >
              <span className={`text-xs font-medium ${today ? 'text-accent' : 'text-text-secondary'}`}>
                {format(day, 'd')}
              </span>
              <div className="flex flex-col gap-0.5 mt-1">
                {dayEvents.slice(0, 2).map((e) => (
                  <button
                    key={e.id}
                    onClick={(ev) => { ev.stopPropagation(); onEventClick(e); }}
                    className="text-left text-[10px] truncate px-1.5 py-0.5 rounded bg-info/20 text-info hover:bg-info/30 transition-colors"
                  >
                    {e.title}
                  </button>
                ))}
                {dayDeadlines.slice(0, 1).map((t) => (
                  <div key={t.id} className="text-[10px] truncate px-1.5 py-0.5 rounded bg-warning/20 text-warning">
                    ⚑ {t.title}
                  </div>
                ))}
                {dayEvents.length > 2 && (
                  <span className="text-[10px] text-text-muted px-1">+{dayEvents.length - 2} more</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
