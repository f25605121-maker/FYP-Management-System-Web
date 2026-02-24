/**
 * Smart Auto-Refresh for Dashboard Pages
 * - Refreshes page every 30 seconds to keep data up-to-date
 * - Preserves scroll position, active tabs, sidebar section
 * - Pauses when user is typing, has a modal open, or is actively interacting
 */
(function () {
    const REFRESH_INTERVAL = 30000; // 30 seconds
    const IDLE_THRESHOLD = 5000;    // must be idle for 5s before refresh fires
    const STORAGE_KEY = 'dashAutoRefresh';

    let lastActivity = Date.now();
    let refreshTimer = null;

    // Track user activity
    function onActivity() {
        lastActivity = Date.now();
    }
    document.addEventListener('mousemove', onActivity, { passive: true });
    document.addEventListener('keydown', onActivity, { passive: true });
    document.addEventListener('click', onActivity, { passive: true });
    document.addEventListener('scroll', onActivity, { passive: true });
    document.addEventListener('touchstart', onActivity, { passive: true });

    // Check if user is actively interacting
    function isUserBusy() {
        // Check if a modal is open
        const openModal = document.querySelector('.modal.show, .modal.in');
        if (openModal) return true;

        // Check if user is typing in an input/textarea
        const active = document.activeElement;
        if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.tagName === 'SELECT')) {
            return true;
        }

        // Check if a dropdown is open
        const openDropdown = document.querySelector('.dropdown-menu.show');
        if (openDropdown) return true;

        // Check if user was active recently
        if (Date.now() - lastActivity < IDLE_THRESHOLD) return true;

        return false;
    }

    // Save current page state before refresh
    function saveState() {
        const state = {};

        // Save scroll position
        state.scrollX = window.scrollX;
        state.scrollY = window.scrollY;

        // Save active sidebar link (admin dashboard)
        const activeSidebarLink = document.querySelector('.sidebar .nav-link.active, .sidebar-nav .nav-link.active');
        if (activeSidebarLink) {
            state.activeSidebarHref = activeSidebarLink.getAttribute('href') ||
                activeSidebarLink.getAttribute('data-section') ||
                activeSidebarLink.getAttribute('onclick');
        }

        // Save visible section (admin dashboard sections)
        const visibleSection = document.querySelector('.content-section[style*="display: block"], .content-section:not([style*="display: none"]):not(.d-none)');
        if (visibleSection) {
            state.visibleSectionId = visibleSection.id;
        }

        // Save active Bootstrap tabs (works for any dashboard)
        const activeTabLinks = document.querySelectorAll('.nav-link.active[data-bs-toggle="tab"], .nav-link.active[data-bs-toggle="pill"]');
        state.activeTabs = [];
        activeTabLinks.forEach(function (tab) {
            const href = tab.getAttribute('href') || tab.getAttribute('data-bs-target');
            if (href) state.activeTabs.push(href);
        });

        // Save any sessionStorage flags that the admin dashboard uses
        // (scrollToUsers, scrollToSettings etc. are already handled by existing code)

        state.timestamp = Date.now();
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }

    // Restore page state after refresh
    function restoreState() {
        const raw = sessionStorage.getItem(STORAGE_KEY);
        if (!raw) return;

        try {
            const state = JSON.parse(raw);

            // Only restore if the save was recent (within 10 seconds)
            if (Date.now() - state.timestamp > 10000) {
                sessionStorage.removeItem(STORAGE_KEY);
                return;
            }

            // Restore visible section (admin dashboard)
            if (state.visibleSectionId) {
                const sections = document.querySelectorAll('.content-section');
                sections.forEach(function (sec) {
                    sec.style.display = 'none';
                });
                const target = document.getElementById(state.visibleSectionId);
                if (target) target.style.display = 'block';

                // Also mark the corresponding sidebar link as active
                const sidebarLinks = document.querySelectorAll('.sidebar .nav-link, .sidebar-nav .nav-link');
                sidebarLinks.forEach(function (link) {
                    link.classList.remove('active');
                    const onclick = link.getAttribute('onclick') || '';
                    if (onclick.includes("'" + state.visibleSectionId + "'") ||
                        onclick.includes('"' + state.visibleSectionId + '"')) {
                        link.classList.add('active');
                    }
                });
            }

            // Restore active Bootstrap tabs
            if (state.activeTabs && state.activeTabs.length > 0) {
                state.activeTabs.forEach(function (tabHref) {
                    const tabTrigger = document.querySelector('[data-bs-toggle="tab"][href="' + tabHref + '"], [data-bs-toggle="tab"][data-bs-target="' + tabHref + '"], [data-bs-toggle="pill"][href="' + tabHref + '"], [data-bs-toggle="pill"][data-bs-target="' + tabHref + '"]');
                    if (tabTrigger && typeof bootstrap !== 'undefined') {
                        try {
                            new bootstrap.Tab(tabTrigger).show();
                        } catch (e) {
                            tabTrigger.click();
                        }
                    }
                });
            }

            // Restore scroll position (with slight delay for DOM to settle)
            if (state.scrollY !== undefined) {
                setTimeout(function () {
                    window.scrollTo(state.scrollX || 0, state.scrollY || 0);
                }, 100);
            }

            sessionStorage.removeItem(STORAGE_KEY);

        } catch (e) {
            sessionStorage.removeItem(STORAGE_KEY);
        }
    }

    // Do the refresh
    function doRefresh() {
        if (isUserBusy()) {
            // User is busy, try again in 5 seconds
            scheduleRefresh(5000);
            return;
        }
        saveState();
        location.reload();
    }

    function scheduleRefresh(interval) {
        if (refreshTimer) clearTimeout(refreshTimer);
        refreshTimer = setTimeout(doRefresh, interval || REFRESH_INTERVAL);
    }

    // On page load: restore state and start timer
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            restoreState();
            scheduleRefresh();
        });
    } else {
        restoreState();
        scheduleRefresh();
    }

    // Pause refresh when page is hidden (user switched tab)
    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            if (refreshTimer) clearTimeout(refreshTimer);
        } else {
            // Page is visible again, schedule a refresh
            scheduleRefresh();
        }
    });
})();
