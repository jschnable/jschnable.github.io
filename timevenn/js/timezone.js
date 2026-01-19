// Timezone calculation utilities using the Intl API

// Time window definitions (in hours)
const TIME_WINDOWS = {
    CORE_START: 9,       // 9 AM
    CORE_END: 17,        // 5 PM
    STRETCH_MORNING_START: 7.5,  // 7:30 AM
    STRETCH_MORNING_END: 9,      // 9 AM
    STRETCH_EVENING_START: 17,   // 5 PM
    STRETCH_EVENING_END: 23,     // 11 PM
};

// Get current time in a specific timezone
function getTimeInTimezone(timezone, date = new Date()) {
    const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone: timezone,
        hour: 'numeric',
        minute: 'numeric',
        hour12: false,
    });

    const parts = formatter.formatToParts(date);
    const hour = parseInt(parts.find(p => p.type === 'hour').value, 10);
    const minute = parseInt(parts.find(p => p.type === 'minute').value, 10);

    return { hour, minute, decimal: hour + minute / 60 };
}

// Get formatted time string for display
function formatTime(timezone, date = new Date()) {
    return new Intl.DateTimeFormat('en-US', {
        timeZone: timezone,
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
    }).format(date);
}

// Get the timezone offset in hours relative to UTC
function getTimezoneOffset(timezone, date = new Date()) {
    // Create formatters for UTC and target timezone
    const utcFormatter = new Intl.DateTimeFormat('en-US', {
        timeZone: 'UTC',
        hour: 'numeric',
        minute: 'numeric',
        hour12: false,
    });

    const tzFormatter = new Intl.DateTimeFormat('en-US', {
        timeZone: timezone,
        hour: 'numeric',
        minute: 'numeric',
        hour12: false,
    });

    const utcParts = utcFormatter.formatToParts(date);
    const tzParts = tzFormatter.formatToParts(date);

    const utcHour = parseInt(utcParts.find(p => p.type === 'hour').value, 10);
    const utcMinute = parseInt(utcParts.find(p => p.type === 'minute').value, 10);
    const tzHour = parseInt(tzParts.find(p => p.type === 'hour').value, 10);
    const tzMinute = parseInt(tzParts.find(p => p.type === 'minute').value, 10);

    let hourDiff = tzHour - utcHour;
    let minuteDiff = tzMinute - utcMinute;

    // Handle day boundary
    if (hourDiff > 12) hourDiff -= 24;
    if (hourDiff < -12) hourDiff += 24;

    return hourDiff + minuteDiff / 60;
}

// Calculate time windows for a city given a reference time
// Returns an array of { start, end, type } where start/end are in hours (0-24)
function calculateTimeWindows(timezone, referenceDate = new Date()) {
    const windows = [];

    // Core office hours (9-17)
    windows.push({
        start: TIME_WINDOWS.CORE_START,
        end: TIME_WINDOWS.CORE_END,
        type: 'core'
    });

    // Morning stretch (7:30-9)
    windows.push({
        start: TIME_WINDOWS.STRETCH_MORNING_START,
        end: TIME_WINDOWS.STRETCH_MORNING_END,
        type: 'stretch'
    });

    // Evening stretch (17-23)
    windows.push({
        start: TIME_WINDOWS.STRETCH_EVENING_START,
        end: TIME_WINDOWS.STRETCH_EVENING_END,
        type: 'stretch'
    });

    return windows;
}

// Convert local hour in one timezone to hour in another timezone
function convertHour(hour, fromTimezone, toTimezone, date = new Date()) {
    const fromOffset = getTimezoneOffset(fromTimezone, date);
    const toOffset = getTimezoneOffset(toTimezone, date);
    const diff = toOffset - fromOffset;

    let converted = hour + diff;
    if (converted < 0) converted += 24;
    if (converted >= 24) converted -= 24;

    return converted;
}

// Get time windows for a city relative to another city's local time
// referenceTimezone: the timezone we're viewing from
// targetTimezone: the timezone we want windows for
function getRelativeTimeWindows(referenceTimezone, targetTimezone, date = new Date()) {
    const windows = calculateTimeWindows(targetTimezone, date);
    const refOffset = getTimezoneOffset(referenceTimezone, date);
    const targetOffset = getTimezoneOffset(targetTimezone, date);
    const diff = targetOffset - refOffset;

    return windows.map(w => ({
        start: normalizeHour(w.start + diff),
        end: normalizeHour(w.end + diff),
        type: w.type,
        wraps: w.start + diff < 0 || w.end + diff >= 24
    }));
}

// Normalize hour to 0-24 range
function normalizeHour(hour) {
    while (hour < 0) hour += 24;
    while (hour >= 24) hour -= 24;
    return hour;
}

// Find overlapping available times for multiple cities
// Returns array of { start, end } in reference timezone hours
function findOverlappingTimes(cities, referenceTimezone = 'UTC', date = new Date()) {
    if (cities.length === 0) return [];
    if (cities.length === 1) {
        // Return the first city's available hours
        const windows = getRelativeTimeWindows(referenceTimezone, cities[0].timezone, date);
        const core = windows.find(w => w.type === 'core');
        const stretches = windows.filter(w => w.type === 'stretch');
        return [
            { start: core.start, end: core.end, type: 'core' },
            ...stretches.map(s => ({ start: s.start, end: s.end, type: 'stretch' }))
        ];
    }

    // Create 24-hour availability arrays for each city
    // Each slot represents 15-minute intervals
    const slots = 96; // 24 * 4
    const availabilities = cities.map(city => {
        const available = new Array(slots).fill(0);
        const windows = getRelativeTimeWindows(referenceTimezone, city.timezone, date);

        windows.forEach(window => {
            const startSlot = Math.floor(window.start * 4);
            const endSlot = Math.floor(window.end * 4);

            if (startSlot <= endSlot) {
                for (let i = startSlot; i < endSlot; i++) {
                    available[i] = window.type === 'core' ? 2 : 1;
                }
            } else {
                // Window wraps around midnight
                for (let i = startSlot; i < slots; i++) {
                    available[i] = window.type === 'core' ? 2 : 1;
                }
                for (let i = 0; i < endSlot; i++) {
                    available[i] = window.type === 'core' ? 2 : 1;
                }
            }
        });

        return available;
    });

    // Find overlapping slots
    const overlap = new Array(slots).fill(0);
    for (let i = 0; i < slots; i++) {
        const minAvailability = Math.min(...availabilities.map(a => a[i]));
        overlap[i] = minAvailability;
    }

    // Convert back to time ranges
    const ranges = [];
    let currentRange = null;

    for (let i = 0; i < slots; i++) {
        if (overlap[i] > 0) {
            if (!currentRange) {
                currentRange = {
                    start: i / 4,
                    type: overlap[i] === 2 ? 'core' : 'stretch'
                };
            } else if ((overlap[i] === 2) !== (currentRange.type === 'core')) {
                // Type changed, close current and start new
                currentRange.end = i / 4;
                ranges.push(currentRange);
                currentRange = {
                    start: i / 4,
                    type: overlap[i] === 2 ? 'core' : 'stretch'
                };
            }
        } else if (currentRange) {
            currentRange.end = i / 4;
            ranges.push(currentRange);
            currentRange = null;
        }
    }

    // Close final range if still open
    if (currentRange) {
        currentRange.end = 24;
        ranges.push(currentRange);
    }

    return ranges;
}

// Get a date object offset by a number of minutes from now
function getOffsetDate(minutesOffset) {
    const date = new Date();
    date.setMinutes(date.getMinutes() + minutesOffset);
    return date;
}
