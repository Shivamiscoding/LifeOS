import type { CalendarEvent, Task } from '../../types';

interface CalendarGridProps {
  currentDate: Date;
  events: CalendarEvent[];
  taskDeadlines: Task[];
  onDateClick: (date: Date) => void;
  onEventClick: (event: CalendarEvent) => void;
}

function isSameCalendarDay(d1: Date, d2: Date): boolean {
  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
  );
}

export function CalendarGrid({ currentDate, events, taskDeadlines, onDateClick, onEventClick }: CalendarGridProps) {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);

  // Monday = 0, Sunday = 6
  let firstDayIndex = firstDayOfMonth.getDay() - 1;
  if (firstDayIndex < 0) firstDayIndex = 6;

  const days: Date[] = [];

  // Previous month trailing days
  for (let i = firstDayIndex; i > 0; i--) {
    days.push(new Date(year, month, 1 - i));
  }

  // Current month days
  for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
    days.push(new Date(year, month, i));
  }

  // Next month leading days to complete the weeks
  const remaining = (7 - (days.length % 7)) % 7;
  for (let i = 1; i <= remaining; i++) {
    days.push(new Date(year, month + 1, i));
  }

  const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const today = new Date();

  return (
    <div className="select-none">
      <div className="grid grid-cols-7 mb-1">
        {WEEKDAYS.map((d) => (
          <div key={d} className="text-center text-xs font-medium text-text-muted py-2">{d}</div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {days.map((day) => {
          const dayEvents = events.filter((e) => isSameCalendarDay(new Date(e.startTime), day));
          const dayDeadlines = taskDeadlines.filter(
            (t) => t.dueDate && isSameCalendarDay(new Date(t.dueDate), day)
          );
          const inCurrentMonth = day.getMonth() === month;
          const isTodayDay = isSameCalendarDay(day, today);

          return (
            <div
              key={day.toISOString()}
              onClick={() => onDateClick(day)}
              className={`min-h-[90px] rounded-lg p-1.5 cursor-pointer border transition-colors ${
                isTodayDay
                  ? 'border-accent bg-accent/10'
                  : 'border-surface-border hover:border-accent/40 hover:bg-surface-hover'
              } ${!inCurrentMonth ? 'opacity-30' : ''}`}
            >
              <span className={`text-xs font-medium ${isTodayDay ? 'text-accent' : 'text-text-secondary'}`}>
                {day.getDate()}
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
