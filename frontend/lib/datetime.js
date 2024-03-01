export const formatWeekday = (weekday) =>
  weekday.charAt(0).toUpperCase() + weekday.substr(1);

export const formatTime = (hour, minute) => {
  const date = new Date();
  date.setHours(hour, minute);
  return new Intl.DateTimeFormat(navigator.language, {
    hour: "numeric",
    minute: "numeric",
  }).format(date);
};

export const formatTimeSlot = (timeSlot) =>
  `${formatWeekday(timeSlot.day)} ${formatTime(
    timeSlot.hour,
    timeSlot.minute,
  )}`;
