/**
 * Real-time Updates Module
 * Handles WebSocket connections and live dashboard updates for all roles
 */

class RealtimeUpdates {
    constructor(options = {}) {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.dashboardRole = options.role || 'unknown';
        this.userId = options.userId || null;
        this.updateInterval = options.updateInterval || 5000; // Update every 5 seconds
        this.updateTimer = null;
        this.fallbackTimer = null;
        this.fallbackEnabled = false;
        this.callbacks = {};
        
        this.init();
    }

    /**
     * Initialize WebSocket connection
     */
    init() {
        try {
            // Connect to SocketIO server
            this.socket = io({
                reconnection: true,
                reconnectionDelay: this.reconnectDelay,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: this.maxReconnectAttempts
            });

            // Set up event listeners
            this.setupEventListeners();
            
            // Join dashboard room
            this.socket.on('connect', () => {
                console.log('✓ Connected to real-time updates');
                this.reconnectAttempts = 0;
                this.stopFallbackPolling();
                this.socket.emit('join_dashboard', { role: this.dashboardRole, userId: this.userId });
                this.startAutoUpdate();
            });

            this.socket.on('disconnect', () => {
                console.log('✗ Disconnected from real-time updates');
                this.stopAutoUpdate();
                this.startFallbackPolling();
            });

            this.socket.on('connect_error', (error) => {
                console.error('Connection error:', error);
                this.reconnectAttempts++;
                if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                    this.startFallbackPolling();
                }
            });

        } catch (error) {
            console.error('Failed to initialize real-time updates:', error);
            this.startFallbackPolling();
        }
    }

    /**
     * Set up all WebSocket event listeners
     */
    setupEventListeners() {
        // Dashboard update
        this.socket.on('dashboard_update', (data) => {
            console.log('Dashboard update received:', data);
            this.onDashboardUpdate(data);
        });

        // Task/Assignment update
        this.socket.on('task_updated', (data) => {
            console.log('Task update received:', data);
            this.onTaskUpdate(data);
        });

        // New notification
        this.socket.on('new_notification', (data) => {
            console.log('New notification:', data);
            this.onNotification(data);
        });

        // Submission update
        this.socket.on('submission_updated', (data) => {
            console.log('Submission update received:', data);
            this.onSubmissionUpdate(data);
        });

        // Remark received
        this.socket.on('remark_received', (data) => {
            console.log('Remark received:', data);
            this.onRemarkReceived(data);
        });

        // Remark response received by supervisor
        this.socket.on('remark_response_received', (data) => {
            console.log('Remark response received:', data);
            this.onRemarkResponseReceived(data);
        });

        // Error handling
        this.socket.on('error', (data) => {
            console.error('WebSocket error:', data);
        });
    }

    /**
     * Request dashboard data update from server
     */
    requestDashboardUpdate() {
        if (this.socket && this.socket.connected) {
            this.socket.emit('request_dashboard_update', {});
        }
    }

    /**
     * Start auto-updating dashboard
     */
    startAutoUpdate() {
        if (!this.updateTimer) {
            this.requestDashboardUpdate();
            this.updateTimer = setInterval(() => {
                this.requestDashboardUpdate();
            }, this.updateInterval);
        }
    }

    /**
     * Stop auto-updating dashboard
     */
    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    /**
     * Start fallback polling when WebSocket is unavailable
     */
    startFallbackPolling() {
        if (this.fallbackTimer) {
            return;
        }
        this.fallbackEnabled = true;
        this.fetchDashboardFallback();
        this.fallbackTimer = setInterval(() => {
            this.fetchDashboardFallback();
        }, this.updateInterval);
    }

    /**
     * Stop fallback polling
     */
    stopFallbackPolling() {
        if (this.fallbackTimer) {
            clearInterval(this.fallbackTimer);
            this.fallbackTimer = null;
        }
        this.fallbackEnabled = false;
    }

    /**
     * Fetch dashboard update data via HTTP fallback
     */
    async fetchDashboardFallback() {
        try {
            const response = await fetch('/dashboard/update_data', { credentials: 'same-origin' });
            if (!response.ok) {
                throw new Error(`Fallback fetch failed: ${response.status}`);
            }
            const data = await response.json();
            this.onDashboardUpdate(data);
        } catch (error) {
            console.error('Fallback dashboard fetch error:', error);
        }
    }

    /**
     * Handle dashboard update - override in specific implementations
     */
    onDashboardUpdate(data) {
        // Show visual feedback
        this.showUpdateIndicator();
        
        // Dispatch custom event for dashboard to handle
        const event = new CustomEvent('realtimeUpdate', { detail: data });
        document.dispatchEvent(event);
        
        if (this.callbacks.onDashboardUpdate) {
            this.callbacks.onDashboardUpdate(data);
        }
    }

    /**
     * Show visual indicator that dashboard is updating
     */
    showUpdateIndicator() {
        // Update timestamp
        this.updateLastUpdatedTime();
        
        // Show loading indicator briefly
        this.showLoadingIndicator();
        
        // Highlight updated elements
        this.highlightUpdatedElements();
        
        // Show toast notification
        this.showUpdateToast();
    }

    /**
     * Show toast notification for successful update
     */
    showUpdateToast() {
        const toastElement = document.getElementById('updateToast');
        if (toastElement && typeof bootstrap !== 'undefined') {
            const toast = new bootstrap.Toast(toastElement, {
                delay: 3000,
                autohide: true
            });
            toast.show();
        }
    }

    /**
     * Update the last updated timestamp
     */
    updateLastUpdatedTime() {
        const timestampElements = document.querySelectorAll('.last-updated-time');
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        
        timestampElements.forEach(element => {
            element.textContent = `Last updated: ${timeString}`;
            element.style.opacity = '1';
            
            // Fade out after 3 seconds
            setTimeout(() => {
                element.style.transition = 'opacity 1s ease-out';
                element.style.opacity = '0.6';
            }, 3000);
        });
    }

    /**
     * Show loading indicator during update
     */
    showLoadingIndicator() {
        let indicator = document.getElementById('realtime-update-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'realtime-update-indicator';
            indicator.innerHTML = `
                <div class="update-indicator">
                    <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                        <span class="visually-hidden">Updating...</span>
                    </div>
                    <small class="text-muted">Updating...</small>
                </div>
            `;
            indicator.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 0.375rem;
                padding: 0.5rem 1rem;
                box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
                display: none;
                font-size: 0.875rem;
            `;
            document.body.appendChild(indicator);
        }
        
        indicator.style.display = 'block';
        setTimeout(() => {
            indicator.style.display = 'none';
        }, 1500);
    }

    /**
     * Highlight elements that were updated
     */
    highlightUpdatedElements() {
        const updatedElements = document.querySelectorAll('[data-updated]');
        updatedElements.forEach(element => {
            element.classList.add('highlight-update');
            setTimeout(() => {
                element.classList.remove('highlight-update');
            }, 2000);
        });
    }

    /**
     * Handle task update
     */
    onTaskUpdate(data) {
        console.log('Task updated:', data);
        const event = new CustomEvent('taskUpdated', { detail: data });
        document.dispatchEvent(event);
        
        if (this.callbacks.onTaskUpdate) {
            this.callbacks.onTaskUpdate(data);
        }
    }

    /**
     * Handle new notification
     */
    onNotification(data) {
        console.log('New notification:', data);
        
        // Show browser notification if permitted
        if (Notification.permission === 'granted') {
            new Notification(data.title || 'New Notification', {
                body: data.message || '',
                icon: '/static/images/notification-icon.png'
            });
        }

        const event = new CustomEvent('newNotification', { detail: data });
        document.dispatchEvent(event);
        
        if (this.callbacks.onNotification) {
            this.callbacks.onNotification(data);
        }
    }

    /**
     * Handle submission update
     */
    onSubmissionUpdate(data) {
        console.log('Submission updated:', data);
        const event = new CustomEvent('submissionUpdated', { detail: data });
        document.dispatchEvent(event);
        
        if (this.callbacks.onSubmissionUpdate) {
            this.callbacks.onSubmissionUpdate(data);
        }
    }

    /**
     * Handle remark received
     */
    onRemarkReceived(data) {
        console.log('Remark received:', data);
        
        // Show browser notification
        if (Notification.permission === 'granted') {
            new Notification('New Remark', {
                body: data.content || 'You have received a new remark',
                icon: '/static/images/notification-icon.png'
            });
        }

        const event = new CustomEvent('remarkReceived', { detail: data });
        document.dispatchEvent(event);
        
        if (this.callbacks.onRemarkReceived) {
            this.callbacks.onRemarkReceived(data);
        }
    }

    /**
     * Handle remark response received by supervisor
     */
    onRemarkResponseReceived(data) {
        console.log('Remark response received:', data);
        if (Notification.permission === 'granted') {
            new Notification('Student Reply Received', {
                body: data.content || 'A student replied to your remark',
                icon: '/static/images/notification-icon.png'
            });
        }

        const event = new CustomEvent('remarkResponseReceived', { detail: data });
        document.dispatchEvent(event);
        
        if (this.callbacks.onRemarkResponseReceived) {
            this.callbacks.onRemarkResponseReceived(data);
        }
    }

    /**
     * Register callback for specific event
     */
    on(eventName, callback) {
        this.callbacks[eventName] = callback;
    }

    /**
     * Emit event to server
     */
    emit(eventName, data) {
        if (this.socket && this.socket.connected) {
            this.socket.emit(eventName, data);
        }
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
        this.stopAutoUpdate();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealtimeUpdates;
}
