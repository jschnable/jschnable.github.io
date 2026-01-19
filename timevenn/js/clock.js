// SVG Radial Clock Renderer

const CLOCK_CONFIG = {
    outerRadius: 180,
    innerRadius: 50,
    ringWidth: 22,
    ringGap: 4,
    hourMarkLength: 8,
    hourLabelRadius: 190,

    colors: {
        background: '#0f172a',
        clockFace: '#1e293b',
        hourMark: '#475569',
        hourLabel: '#94a3b8',
        core: '#4ade80',
        stretch: '#fbbf24',
        sleep: '#475569',
        overlapCore: '#22d3ee',      // Cyan - all in office hours
        overlapStretch: '#a78bfa',   // Purple - at least one in stretch
        selection: '#ffffff',
        currentTime: '#f43f5e',
        currentTimeGlow: 'rgba(244, 63, 94, 0.4)',
        cities: ['#f472b6', '#60a5fa', '#34d399', '#fbbf24', '#a78bfa']
    }
};

class ClockRenderer {
    constructor(svgElement) {
        this.svg = svgElement;
        this.cities = [];
        this.referenceDate = new Date();
        this.referenceTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

        // Selection state
        this.selection = null; // { startHour, endHour }
        this.isDragging = false;
        this.dragStartHour = null;
        this.onSelectionChange = null; // Callback for selection changes

        this.setupDragHandlers();
    }

    setupDragHandlers() {
        this.svg.addEventListener('mousedown', (e) => this.handleDragStart(e));
        this.svg.addEventListener('mousemove', (e) => this.handleDragMove(e));
        this.svg.addEventListener('mouseup', (e) => this.handleDragEnd(e));
        this.svg.addEventListener('mouseleave', (e) => this.handleDragEnd(e));

        // Touch support
        this.svg.addEventListener('touchstart', (e) => this.handleDragStart(e), { passive: false });
        this.svg.addEventListener('touchmove', (e) => this.handleDragMove(e), { passive: false });
        this.svg.addEventListener('touchend', (e) => this.handleDragEnd(e));
    }

    getEventPosition(e) {
        const rect = this.svg.getBoundingClientRect();
        const svgSize = Math.min(rect.width, rect.height);
        const scale = 400 / svgSize; // viewBox is 400x400

        let clientX, clientY;
        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        } else {
            clientX = e.clientX;
            clientY = e.clientY;
        }

        // Convert to SVG coordinates (centered at 0,0)
        const x = (clientX - rect.left - rect.width / 2) * scale;
        const y = (clientY - rect.top - rect.height / 2) * scale;

        return { x, y };
    }

    positionToHour(x, y) {
        // Convert cartesian to angle, then to hour
        // Account for clock rotation offset
        const rotationOffset = this.getRotationOffset();
        let angle = Math.atan2(y, x) + Math.PI / 2; // Adjust so 0 is at top
        if (angle < 0) angle += 2 * Math.PI;

        // Add back the rotation offset to get the actual hour
        let hour = (angle / (2 * Math.PI)) * 24 + rotationOffset;
        while (hour < 0) hour += 24;
        while (hour >= 24) hour -= 24;

        return hour;
    }

    // Snap hour to nearest 15-minute interval
    snapToQuarterHour(hour) {
        return Math.round(hour * 4) / 4;
    }

    // Get rotation offset so current time is at top
    getRotationOffset() {
        const time = getTimeInTimezone(this.referenceTimezone, this.referenceDate);
        return time.decimal;
    }

    handleDragStart(e) {
        e.preventDefault();
        const pos = this.getEventPosition(e);
        const distance = Math.sqrt(pos.x * pos.x + pos.y * pos.y);

        // Only start drag if clicking within the clock face
        if (distance <= CLOCK_CONFIG.outerRadius) {
            this.isDragging = true;
            // Snap to nearest 15-minute interval
            this.dragStartHour = this.snapToQuarterHour(this.positionToHour(pos.x, pos.y));
            this.selection = { startHour: this.dragStartHour, endHour: this.dragStartHour };
            this.renderSelection();
        }
    }

    handleDragMove(e) {
        if (!this.isDragging) return;
        e.preventDefault();

        const pos = this.getEventPosition(e);
        // Snap to nearest 15-minute interval
        const currentHour = this.snapToQuarterHour(this.positionToHour(pos.x, pos.y));

        this.selection = {
            startHour: this.dragStartHour,
            endHour: currentHour
        };
        this.renderSelection();

        if (this.onSelectionChange) {
            this.onSelectionChange(this.selection);
        }
    }

    handleDragEnd(e) {
        if (!this.isDragging) return;
        this.isDragging = false;

        // Normalize selection so start < end (unless wrapping)
        if (this.selection) {
            const duration = this.getSelectionDuration();
            // If selection is very small (less than 15 min), clear it
            if (duration < 0.25) {
                this.clearSelection();
            } else if (this.onSelectionChange) {
                this.onSelectionChange(this.selection);
            }
        }
    }

    getSelectionDuration() {
        if (!this.selection) return 0;
        let duration = this.selection.endHour - this.selection.startHour;
        if (duration < 0) duration += 24;
        // Handle reverse selection (dragging counter-clockwise)
        if (duration > 12) duration = 24 - duration;
        return Math.abs(duration);
    }

    clearSelection() {
        this.selection = null;
        this.renderSelection();
        if (this.onSelectionChange) {
            this.onSelectionChange(null);
        }
    }

    // Convert hour (0-24) to angle in radians (current time at top, clockwise)
    hourToAngle(hour) {
        // Subtract rotation offset so current time appears at top
        const rotationOffset = this.getRotationOffset();
        const adjustedHour = hour - rotationOffset;
        return ((adjustedHour / 24) * 2 * Math.PI) - (Math.PI / 2);
    }

    // Convert polar to cartesian coordinates
    polarToCartesian(radius, angle) {
        return {
            x: radius * Math.cos(angle),
            y: radius * Math.sin(angle)
        };
    }

    // Create SVG arc path
    createArcPath(innerRadius, outerRadius, startHour, endHour) {
        const startAngle = this.hourToAngle(startHour);
        const endAngle = this.hourToAngle(endHour);

        const start1 = this.polarToCartesian(outerRadius, startAngle);
        const end1 = this.polarToCartesian(outerRadius, endAngle);
        const start2 = this.polarToCartesian(innerRadius, endAngle);
        const end2 = this.polarToCartesian(innerRadius, startAngle);

        // Handle arcs that cross midnight
        let arcLength = endHour - startHour;
        if (arcLength < 0) arcLength += 24;
        const largeArc = arcLength > 12 ? 1 : 0;

        return [
            `M ${start1.x} ${start1.y}`,
            `A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${end1.x} ${end1.y}`,
            `L ${start2.x} ${start2.y}`,
            `A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${end2.x} ${end2.y}`,
            'Z'
        ].join(' ');
    }

    // Create an SVG element
    createElement(tag, attrs = {}) {
        const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
        for (const [key, value] of Object.entries(attrs)) {
            el.setAttribute(key, value);
        }
        return el;
    }

    // Render the complete clock
    render() {
        // Clear existing content
        this.svg.innerHTML = '';

        // Create groups for layering
        const bgGroup = this.createElement('g', { class: 'clock-bg' });
        const ringsGroup = this.createElement('g', { class: 'clock-rings' });
        const overlapGroup = this.createElement('g', { class: 'clock-overlap' });
        const selectionGroup = this.createElement('g', { class: 'clock-selection' });
        const markersGroup = this.createElement('g', { class: 'clock-markers' });
        const labelsGroup = this.createElement('g', { class: 'clock-labels' });
        const timeGroup = this.createElement('g', { class: 'clock-time' });

        // Draw background circle
        bgGroup.appendChild(this.createElement('circle', {
            cx: 0, cy: 0,
            r: CLOCK_CONFIG.outerRadius,
            fill: CLOCK_CONFIG.colors.clockFace
        }));

        // Draw hour markers and labels
        this.renderHourMarkers(markersGroup, labelsGroup);

        // Draw city rings
        this.renderCityRings(ringsGroup);

        // Draw overlap regions
        this.renderOverlap(overlapGroup);

        // Draw current time indicator
        this.renderCurrentTime(timeGroup);

        // Assemble layers
        this.svg.appendChild(bgGroup);
        this.svg.appendChild(ringsGroup);
        this.svg.appendChild(overlapGroup);
        this.svg.appendChild(selectionGroup);
        this.svg.appendChild(markersGroup);
        this.svg.appendChild(labelsGroup);
        this.svg.appendChild(timeGroup);

        // Store reference for selection rendering
        this.selectionGroup = selectionGroup;

        // Re-render selection if exists
        this.renderSelection();
    }

    renderSelection() {
        if (!this.selectionGroup) return;

        // Clear existing selection
        this.selectionGroup.innerHTML = '';

        if (!this.selection) return;

        let { startHour, endHour } = this.selection;

        // Draw selection arc
        const path = this.createElement('path', {
            d: this.createArcPath(0, CLOCK_CONFIG.outerRadius, startHour, endHour),
            fill: CLOCK_CONFIG.colors.selection,
            opacity: 0.2,
            'pointer-events': 'none'
        });
        this.selectionGroup.appendChild(path);

        // Draw selection boundary lines
        const startAngle = this.hourToAngle(startHour);
        const endAngle = this.hourToAngle(endHour);

        const startOuter = this.polarToCartesian(CLOCK_CONFIG.outerRadius, startAngle);
        const endOuter = this.polarToCartesian(CLOCK_CONFIG.outerRadius, endAngle);

        this.selectionGroup.appendChild(this.createElement('line', {
            x1: 0, y1: 0,
            x2: startOuter.x, y2: startOuter.y,
            stroke: CLOCK_CONFIG.colors.selection,
            'stroke-width': 2,
            opacity: 0.8,
            'pointer-events': 'none'
        }));

        this.selectionGroup.appendChild(this.createElement('line', {
            x1: 0, y1: 0,
            x2: endOuter.x, y2: endOuter.y,
            stroke: CLOCK_CONFIG.colors.selection,
            'stroke-width': 2,
            opacity: 0.8,
            'pointer-events': 'none'
        }));
    }

    renderHourMarkers(markersGroup, labelsGroup) {
        for (let hour = 0; hour < 24; hour++) {
            const angle = this.hourToAngle(hour);
            const innerR = CLOCK_CONFIG.outerRadius - CLOCK_CONFIG.hourMarkLength;
            const outerR = CLOCK_CONFIG.outerRadius;

            const start = this.polarToCartesian(innerR, angle);
            const end = this.polarToCartesian(outerR, angle);

            // Hour tick mark
            markersGroup.appendChild(this.createElement('line', {
                x1: start.x, y1: start.y,
                x2: end.x, y2: end.y,
                stroke: CLOCK_CONFIG.colors.hourMark,
                'stroke-width': hour % 6 === 0 ? 2 : 1
            }));

            // Hour label (every 3 hours)
            if (hour % 3 === 0) {
                const labelPos = this.polarToCartesian(CLOCK_CONFIG.hourLabelRadius, angle);
                const label = hour === 0 ? '12a' :
                              hour === 12 ? '12p' :
                              hour < 12 ? `${hour}a` : `${hour - 12}p`;

                labelsGroup.appendChild(this.createElement('text', {
                    x: labelPos.x,
                    y: labelPos.y,
                    fill: CLOCK_CONFIG.colors.hourLabel,
                    'font-size': '10',
                    'text-anchor': 'middle',
                    'dominant-baseline': 'middle'
                })).textContent = label;
            }
        }
    }

    renderCityRings(ringsGroup) {
        const numCities = this.cities.length;
        if (numCities === 0) return;

        // Calculate ring dimensions
        const availableSpace = CLOCK_CONFIG.outerRadius - CLOCK_CONFIG.innerRadius - 20;
        const ringWidth = Math.min(CLOCK_CONFIG.ringWidth, availableSpace / numCities - CLOCK_CONFIG.ringGap);

        this.cities.forEach((city, index) => {
            const color = CLOCK_CONFIG.colors.cities[index % CLOCK_CONFIG.colors.cities.length];
            const outerR = CLOCK_CONFIG.outerRadius - 15 - (index * (ringWidth + CLOCK_CONFIG.ringGap));
            const innerR = outerR - ringWidth;

            // Get time windows relative to reference timezone
            const windows = getRelativeTimeWindows(this.referenceTimezone, city.timezone, this.referenceDate);

            // Draw base ring (sleep time)
            ringsGroup.appendChild(this.createElement('circle', {
                cx: 0, cy: 0,
                r: (outerR + innerR) / 2,
                fill: 'none',
                stroke: CLOCK_CONFIG.colors.sleep,
                'stroke-width': ringWidth,
                opacity: 0.5
            }));

            // Draw time windows
            windows.forEach(window => {
                const fillColor = window.type === 'core' ? CLOCK_CONFIG.colors.core : CLOCK_CONFIG.colors.stretch;

                // Handle windows that wrap around midnight
                if (window.start > window.end) {
                    // Draw two arcs
                    ringsGroup.appendChild(this.createElement('path', {
                        d: this.createArcPath(innerR, outerR, window.start, 24),
                        fill: fillColor,
                        opacity: 0.8
                    }));
                    ringsGroup.appendChild(this.createElement('path', {
                        d: this.createArcPath(innerR, outerR, 0, window.end),
                        fill: fillColor,
                        opacity: 0.8
                    }));
                } else {
                    ringsGroup.appendChild(this.createElement('path', {
                        d: this.createArcPath(innerR, outerR, window.start, window.end),
                        fill: fillColor,
                        opacity: 0.8
                    }));
                }
            });

            // Draw ring outline
            ringsGroup.appendChild(this.createElement('circle', {
                cx: 0, cy: 0,
                r: outerR,
                fill: 'none',
                stroke: color,
                'stroke-width': 2
            }));

            // Add curved city label on the ring - centered in the sleep zone
            const labelR = (outerR + innerR) / 2; // Center of the ring
            const labelText = `${city.city} · ${formatTime(city.timezone, this.referenceDate)}`;

            // Create a unique ID for this text path
            const pathId = `city-path-${index}`;

            // Find the center of the sleep zone from the actual rendered windows
            // Sleep zone is the gap: from stretch evening end (23) to stretch morning start (7.5)
            // Get the windows which are already converted to reference timezone view
            const sleepStartLocal = 23;  // 11 PM local
            const sleepEndLocal = 7.5;   // 7:30 AM local
            const sleepCenterLocal = 3.25; // 3:15 AM local (center of 23:00 to 7:30)

            // Convert from city local time to reference timezone
            // Use same logic as getRelativeTimeWindows
            const refOffset = getTimezoneOffset(this.referenceTimezone, this.referenceDate);
            const cityOffset = getTimezoneOffset(city.timezone, this.referenceDate);
            const tzDiff = cityOffset - refOffset;

            let labelCenterHour = sleepCenterLocal + tzDiff;

            // Normalize to 0-24 range
            while (labelCenterHour < 0) labelCenterHour += 24;
            while (labelCenterHour >= 24) labelCenterHour -= 24;

            // Calculate arc span - scale based on ring radius
            // Inner rings (smaller radius) need larger angular span to fit same text
            const outerRingRadius = CLOCK_CONFIG.outerRadius - 15; // Reference radius for outermost ring
            const radiusScale = outerRingRadius / labelR;
            const textArcSpan = Math.max(4, labelText.length * 0.22) * radiusScale;
            let startHour = labelCenterHour - textArcSpan / 2;
            let endHour = labelCenterHour + textArcSpan / 2;

            // Determine if label is in top half or bottom half of clock
            // Top half: within 6 hours of current time (rotation offset)
            // The hourToAngle function already accounts for rotation
            const rotationOffset = this.getRotationOffset();
            let hoursFromNow = labelCenterHour - rotationOffset;
            while (hoursFromNow < -12) hoursFromNow += 24;
            while (hoursFromNow > 12) hoursFromNow -= 24;

            const isTopHalf = Math.abs(hoursFromNow) < 6;

            // Create the arc path for text
            const startAngle = this.hourToAngle(startHour);
            const endAngle = this.hourToAngle(endHour);
            const startPos = this.polarToCartesian(labelR, startAngle);
            const endPos = this.polarToCartesian(labelR, endAngle);

            // SVG arc path - reverse direction based on position so text reads correctly
            let arcPath;
            if (isTopHalf) {
                // Top half: draw arc clockwise (sweep flag 1)
                arcPath = `M ${startPos.x} ${startPos.y} A ${labelR} ${labelR} 0 0 1 ${endPos.x} ${endPos.y}`;
            } else {
                // Bottom half: draw arc counter-clockwise (sweep flag 0), from end to start
                arcPath = `M ${endPos.x} ${endPos.y} A ${labelR} ${labelR} 0 0 0 ${startPos.x} ${startPos.y}`;
            }

            // Add path to defs
            const defs = this.svg.querySelector('defs') || this.createElement('defs');
            if (!this.svg.querySelector('defs')) {
                this.svg.insertBefore(defs, this.svg.firstChild);
            }

            const pathEl = this.createElement('path', {
                id: pathId,
                d: arcPath,
                fill: 'none'
            });
            defs.appendChild(pathEl);

            // Create text element with textPath
            const textEl = this.createElement('text', {
                fill: color,
                'font-size': '10',
                'font-weight': '600'
            });

            const textPathEl = this.createElement('textPath', {
                href: `#${pathId}`,
                startOffset: '50%',
                'text-anchor': 'middle'
            });
            textPathEl.textContent = labelText;

            textEl.appendChild(textPathEl);
            ringsGroup.appendChild(textEl);
        });
    }

    renderOverlap(overlapGroup) {
        if (this.cities.length < 2) return;

        const overlaps = findOverlappingTimes(this.cities, this.referenceTimezone, this.referenceDate);

        // Draw overlap indicator in center
        const centerRadius = CLOCK_CONFIG.innerRadius - 5;

        overlaps.forEach(overlap => {
            // Use different colors for core (all office hours) vs stretch (at least one in stretch)
            const fillColor = overlap.type === 'core'
                ? CLOCK_CONFIG.colors.overlapCore
                : CLOCK_CONFIG.colors.overlapStretch;

            if (overlap.start > overlap.end) {
                // Wraps around midnight
                overlapGroup.appendChild(this.createElement('path', {
                    d: this.createArcPath(0, centerRadius, overlap.start, 24),
                    fill: fillColor,
                    opacity: 0.7
                }));
                overlapGroup.appendChild(this.createElement('path', {
                    d: this.createArcPath(0, centerRadius, 0, overlap.end),
                    fill: fillColor,
                    opacity: 0.7
                }));
            } else {
                overlapGroup.appendChild(this.createElement('path', {
                    d: this.createArcPath(0, centerRadius, overlap.start, overlap.end),
                    fill: fillColor,
                    opacity: 0.7
                }));
            }
        });
    }

    renderCurrentTime(timeGroup) {
        const time = getTimeInTimezone(this.referenceTimezone, this.referenceDate);
        const hour = time.decimal;
        const angle = this.hourToAngle(hour);

        // Time indicator line
        const innerPos = this.polarToCartesian(CLOCK_CONFIG.innerRadius - 10, angle);
        const outerPos = this.polarToCartesian(CLOCK_CONFIG.outerRadius + 5, angle);

        // Add glow filter to defs
        const defs = this.svg.querySelector('defs') || this.createElement('defs');
        if (!this.svg.querySelector('defs')) {
            this.svg.insertBefore(defs, this.svg.firstChild);
        }

        // Create glow filter if not exists
        if (!defs.querySelector('#currentTimeGlow')) {
            const filter = this.createElement('filter', {
                id: 'currentTimeGlow',
                x: '-50%', y: '-50%',
                width: '200%', height: '200%'
            });
            const feGaussianBlur = this.createElement('feGaussianBlur', {
                stdDeviation: '3',
                result: 'coloredBlur'
            });
            const feMerge = this.createElement('feMerge');
            const feMergeNode1 = this.createElement('feMergeNode', { in: 'coloredBlur' });
            const feMergeNode2 = this.createElement('feMergeNode', { in: 'SourceGraphic' });
            feMerge.appendChild(feMergeNode1);
            feMerge.appendChild(feMergeNode2);
            filter.appendChild(feGaussianBlur);
            filter.appendChild(feMerge);
            defs.appendChild(filter);

            // Add pulse animation
            const style = this.createElement('style');
            style.textContent = `
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.6; }
                }
                .current-time-indicator {
                    animation: pulse 2s ease-in-out infinite;
                }
            `;
            defs.appendChild(style);
        }

        // Glow line (behind main line)
        timeGroup.appendChild(this.createElement('line', {
            x1: innerPos.x, y1: innerPos.y,
            x2: outerPos.x, y2: outerPos.y,
            stroke: CLOCK_CONFIG.colors.currentTime,
            'stroke-width': 6,
            opacity: 0.3,
            'stroke-linecap': 'round'
        }));

        // Main time indicator line
        const line = this.createElement('line', {
            x1: innerPos.x, y1: innerPos.y,
            x2: outerPos.x, y2: outerPos.y,
            stroke: CLOCK_CONFIG.colors.currentTime,
            'stroke-width': 2,
            'stroke-linecap': 'round',
            filter: 'url(#currentTimeGlow)',
            class: 'current-time-indicator'
        });
        timeGroup.appendChild(line);

        // Outer glow circle
        timeGroup.appendChild(this.createElement('circle', {
            cx: outerPos.x, cy: outerPos.y,
            r: 8,
            fill: CLOCK_CONFIG.colors.currentTime,
            opacity: 0.2
        }));

        // Main circle at the end
        const circle = this.createElement('circle', {
            cx: outerPos.x, cy: outerPos.y,
            r: 5,
            fill: CLOCK_CONFIG.colors.currentTime,
            filter: 'url(#currentTimeGlow)',
            class: 'current-time-indicator'
        });
        timeGroup.appendChild(circle);
    }

    setCities(cities) {
        this.cities = cities;
        this.render();
    }

    setReferenceDate(date) {
        this.referenceDate = date;
        this.render();
    }

    setReferenceTimezone(timezone) {
        this.referenceTimezone = timezone;
        this.render();
    }

    // Get normalized selection with proper start/end order
    getNormalizedSelection() {
        if (!this.selection) return null;

        let { startHour, endHour } = this.selection;

        // Calculate clockwise duration
        let clockwiseDuration = endHour - startHour;
        if (clockwiseDuration < 0) clockwiseDuration += 24;

        // If dragging more than halfway around, reverse direction
        if (clockwiseDuration > 12) {
            return { startHour: endHour, endHour: startHour };
        }

        return { startHour, endHour };
    }
}
