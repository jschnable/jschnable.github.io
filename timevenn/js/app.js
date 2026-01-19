// Main Application Logic

class WorldChatClockApp {
    constructor() {
        this.selectedCities = [];
        this.maxCities = 5;
        this.timeOffset = 0; // Minutes offset from now
        this.clock = null;
        this.updateInterval = null;

        this.init();
    }

    init() {
        // Initialize clock renderer
        const svgElement = document.getElementById('clock-svg');
        this.clock = new ClockRenderer(svgElement);

        // Set up selection callback
        this.clock.onSelectionChange = (selection) => this.handleSelectionChange(selection);

        // Set up event listeners
        this.setupSearchInput();
        this.setupCityPanel();
        this.setupTimeControls();
        this.setupShareButton();
        this.setupSelectionPanel();

        // Load state from URL if present
        this.loadFromURL();

        // Initial render
        this.updateClock();

        // Start real-time updates
        this.startRealtimeUpdates();
    }

    setupSearchInput() {
        const input = document.getElementById('city-search-input');
        const suggestions = document.getElementById('city-suggestions');
        let highlightedIndex = -1;

        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query.length < 1) {
                this.hideSuggestions();
                return;
            }

            const results = fuzzySearch(query, CITIES, 8);
            this.showSuggestions(results);
            highlightedIndex = -1;
        });

        input.addEventListener('keydown', (e) => {
            const items = suggestions.querySelectorAll('.suggestion-item');

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                highlightedIndex = Math.min(highlightedIndex + 1, items.length - 1);
                this.updateHighlight(items, highlightedIndex);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                highlightedIndex = Math.max(highlightedIndex - 1, 0);
                this.updateHighlight(items, highlightedIndex);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (highlightedIndex >= 0 && items[highlightedIndex]) {
                    items[highlightedIndex].click();
                }
            } else if (e.key === 'Escape') {
                this.hideSuggestions();
                input.blur();
            }
        });

        input.addEventListener('focus', () => {
            const query = input.value.trim();
            if (query.length >= 1) {
                const results = fuzzySearch(query, CITIES, 8);
                this.showSuggestions(results);
            }
        });

        // Close suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.city-search')) {
                this.hideSuggestions();
            }
        });
    }

    showSuggestions(results) {
        const suggestions = document.getElementById('city-suggestions');
        suggestions.innerHTML = '';

        if (results.length === 0) {
            suggestions.classList.remove('active');
            return;
        }

        results.forEach(cityData => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.innerHTML = `
                <div class="suggestion-city">${cityData.city}</div>
                <div class="suggestion-country">${cityData.country}</div>
            `;
            div.addEventListener('click', () => {
                this.addCity(cityData);
                document.getElementById('city-search-input').value = '';
                this.hideSuggestions();
            });
            suggestions.appendChild(div);
        });

        suggestions.classList.add('active');
    }

    hideSuggestions() {
        const suggestions = document.getElementById('city-suggestions');
        suggestions.classList.remove('active');
    }

    setupCityPanel() {
        const clearAllBtn = document.getElementById('clear-all-cities-btn');
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', () => {
                this.clearAllCities();
            });
        }
    }

    updateHighlight(items, index) {
        items.forEach((item, i) => {
            item.classList.toggle('highlighted', i === index);
        });
    }

    addCity(cityData) {
        // Check if already selected
        if (this.selectedCities.find(c => c.city === cityData.city)) {
            return;
        }

        // Check max cities
        if (this.selectedCities.length >= this.maxCities) {
            return;
        }

        this.selectedCities.push(cityData);
        this.renderSelectedCities();
        this.updateClock();
        this.updateURL();
    }

    removeCity(cityData) {
        this.selectedCities = this.selectedCities.filter(c => c.city !== cityData.city);
        this.renderSelectedCities();
        this.updateClock();
        this.updateURL();
    }

    renderSelectedCities() {
        const container = document.getElementById('selected-cities');
        container.innerHTML = '';

        this.selectedCities.forEach((city, index) => {
            const color = CLOCK_CONFIG.colors.cities[index % CLOCK_CONFIG.colors.cities.length];
            const currentTime = formatTime(city.timezone, this.getReferenceDate());

            const div = document.createElement('div');
            div.className = 'city-tag';
            div.style.borderLeftColor = color;
            div.innerHTML = `
                <div class="city-tag-color" style="background: ${color}"></div>
                <div class="city-tag-info">
                    <div class="city-tag-name">${city.city}</div>
                    <div class="city-tag-time">${currentTime}</div>
                </div>
                <button class="city-tag-remove" title="Remove">&times;</button>
            `;

            div.querySelector('.city-tag-remove').addEventListener('click', () => {
                this.removeCity(city);
            });

            container.appendChild(div);
        });

        // Update hint visibility
        const hint = document.querySelector('.hint');
        if (hint) {
            hint.style.display = this.selectedCities.length >= this.maxCities ? 'none' : 'block';
        }
    }

    setupTimeControls() {
        const slider = document.getElementById('time-slider');
        const nowBtn = document.getElementById('now-btn');

        slider.addEventListener('input', (e) => {
            this.timeOffset = parseInt(e.target.value, 10);
            this.updateClock();
            this.updateTimeDisplay();
        });

        nowBtn.addEventListener('click', () => {
            this.timeOffset = 0;
            slider.value = 0;
            this.updateClock();
            this.updateTimeDisplay();
        });
    }

    getReferenceDate() {
        return getOffsetDate(this.timeOffset);
    }

    updateClock() {
        this.clock.setCities(this.selectedCities);
        this.clock.setReferenceDate(this.getReferenceDate());
        this.updateTimeDisplay();
    }

    updateTimeDisplay() {
        const display = document.getElementById('time-display');
        const date = this.getReferenceDate();
        const localTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        display.textContent = formatTime(localTimezone, date);

        // Also update city times
        this.renderSelectedCities();
    }

    startRealtimeUpdates() {
        // Update every minute
        this.updateInterval = setInterval(() => {
            if (this.timeOffset === 0) {
                this.updateClock();
            }
        }, 60000);
    }

    setupShareButton() {
        const shareBtn = document.getElementById('share-btn');
        const feedback = document.getElementById('share-feedback');

        shareBtn.addEventListener('click', async () => {
            const url = window.location.href;

            try {
                await navigator.clipboard.writeText(url);
                feedback.textContent = 'Copied!';
                setTimeout(() => {
                    feedback.textContent = '';
                }, 2000);
            } catch (err) {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = url;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                feedback.textContent = 'Copied!';
                setTimeout(() => {
                    feedback.textContent = '';
                }, 2000);
            }
        });
    }

    updateURL() {
        const cityIds = this.selectedCities.map(c => getCityId(c));
        const hash = cityIds.length > 0 ? '#' + cityIds.join(',') : '';
        history.replaceState(null, '', window.location.pathname + hash);
    }

    loadFromURL() {
        const hash = window.location.hash.slice(1);

        if (!hash) {
            // Load default demo cities: Bonn, Germany and Mexico City, Mexico
            this.loadDefaultCities();
            return;
        }

        const cityIds = hash.split(',').filter(id => id.length > 0);

        cityIds.forEach(id => {
            const cityName = id.replace(/-/g, ' ');
            const city = findCity(cityName);
            if (city && this.selectedCities.length < this.maxCities) {
                this.selectedCities.push(city);
            }
        });

        this.renderSelectedCities();
    }

    loadDefaultCities() {
        const defaultCities = ['Bonn', 'Mexico City'];

        defaultCities.forEach(name => {
            const city = findCity(name);
            if (city) {
                this.selectedCities.push(city);
            }
        });

        this.renderSelectedCities();
    }

    clearAllCities() {
        this.selectedCities = [];
        this.renderSelectedCities();
        this.updateClock();
        this.updateURL();
    }

    setupSelectionPanel() {
        const clearBtn = document.getElementById('clear-selection-btn');
        const copyBtn = document.getElementById('copy-times-btn');

        clearBtn.addEventListener('click', () => {
            this.clock.clearSelection();
        });

        copyBtn.addEventListener('click', () => {
            this.copySelectionToClipboard();
        });
    }

    handleSelectionChange(selection) {
        const panel = document.getElementById('selection-panel');

        if (!selection || this.selectedCities.length === 0) {
            panel.classList.add('hidden');
            return;
        }

        panel.classList.remove('hidden');
        this.renderSelectionTimes(selection);
    }

    renderSelectionTimes(selection) {
        const container = document.getElementById('selection-times');
        const durationContainer = document.getElementById('selection-duration');
        container.innerHTML = '';

        const normalizedSelection = this.clock.getNormalizedSelection();
        if (!normalizedSelection) return;

        const { startHour, endHour } = normalizedSelection;
        const referenceDate = this.getReferenceDate();
        const referenceTimezone = this.clock.referenceTimezone;

        // Calculate and display duration
        let duration = endHour - startHour;
        if (duration < 0) duration += 24;
        const hours = Math.floor(duration);
        const minutes = Math.round((duration - hours) * 60);

        let durationText;
        if (hours === 0) {
            durationText = `${minutes} minutes`;
        } else if (minutes === 0) {
            durationText = hours === 1 ? '1 hour' : `${hours} hours`;
        } else {
            durationText = `${hours}h ${minutes}m`;
        }
        durationContainer.textContent = durationText;

        this.selectedCities.forEach((city, index) => {
            const color = CLOCK_CONFIG.colors.cities[index % CLOCK_CONFIG.colors.cities.length];

            // Convert selection hours to this city's timezone
            const startInCity = this.convertHourToTimezone(startHour, referenceTimezone, city.timezone, referenceDate);
            const endInCity = this.convertHourToTimezone(endHour, referenceTimezone, city.timezone, referenceDate);

            const startFormatted = this.formatHourAsTime(startInCity);
            const endFormatted = this.formatHourAsTime(endInCity);

            const div = document.createElement('div');
            div.className = 'selection-city';
            div.style.borderLeftColor = color;
            div.innerHTML = `
                <span class="selection-city-name">${city.city}</span>
                <span class="selection-city-time">${startFormatted} - ${endFormatted}</span>
            `;
            container.appendChild(div);
        });
    }

    convertHourToTimezone(hour, fromTimezone, toTimezone, date) {
        // Get timezone offsets
        const fromOffset = getTimezoneOffset(fromTimezone, date);
        const toOffset = getTimezoneOffset(toTimezone, date);
        const diff = toOffset - fromOffset;

        let converted = hour + diff;
        while (converted < 0) converted += 24;
        while (converted >= 24) converted -= 24;

        return converted;
    }

    formatHourAsTime(hour) {
        const h = Math.floor(hour);
        const m = Math.round((hour - h) * 60);
        const period = h >= 12 ? 'PM' : 'AM';
        const hour12 = h === 0 ? 12 : h > 12 ? h - 12 : h;
        return `${hour12}:${m.toString().padStart(2, '0')} ${period}`;
    }

    async copySelectionToClipboard() {
        const normalizedSelection = this.clock.getNormalizedSelection();
        if (!normalizedSelection || this.selectedCities.length === 0) return;

        const { startHour, endHour } = normalizedSelection;
        const referenceDate = this.getReferenceDate();
        const referenceTimezone = this.clock.referenceTimezone;

        // Build email-friendly text
        let text = 'Proposed meeting time:\n\n';

        this.selectedCities.forEach(city => {
            const startInCity = this.convertHourToTimezone(startHour, referenceTimezone, city.timezone, referenceDate);
            const endInCity = this.convertHourToTimezone(endHour, referenceTimezone, city.timezone, referenceDate);

            const startFormatted = this.formatHourAsTime(startInCity);
            const endFormatted = this.formatHourAsTime(endInCity);

            text += `${city.city}: ${startFormatted} - ${endFormatted}\n`;
        });

        const feedback = document.getElementById('copy-feedback');

        try {
            await navigator.clipboard.writeText(text);
            feedback.textContent = 'Copied!';
            setTimeout(() => {
                feedback.textContent = '';
            }, 2000);
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            feedback.textContent = 'Copied!';
            setTimeout(() => {
                feedback.textContent = '';
            }, 2000);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WorldChatClockApp();
});
