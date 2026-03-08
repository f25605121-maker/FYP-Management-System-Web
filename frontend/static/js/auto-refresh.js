/**
 * Smart AJAX Auto-Refresh for Dashboard Pages
 * - Silently fetches updated content every 30 seconds via AJAX
 * - Updates the page content WITHOUT a full reload (no flash/flicker)
 * - Preserves scroll position, open modals, active tabs, sidebar sections
 * - Pauses when user is typing, has a modal open, or is actively interacting
 */
(function () {
    const REFRESH_INTERVAL = 30000; // 30 seconds
    const IDLE_THRESHOLD = 5000;    // must be idle 5s before refresh fires

    let lastActivity = Date.now();
    let refreshTimer = null;
    let isFetching = false;

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
        // Modal open
        if (document.querySelector('.modal.show, .modal.in')) return true;

        // Typing in input/textarea/select
        var active = document.activeElement;
        if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.tagName === 'SELECT')) {
            return true;
        }

        // Dropdown open
        if (document.querySelector('.dropdown-menu.show')) return true;

        // Recent activity
        if (Date.now() - lastActivity < IDLE_THRESHOLD) return true;

        return false;
    }

    // Get the current active section ID (admin dashboard)
    function getActiveSectionId() {
        var sec = document.querySelector('.content-section.active');
        if (sec) return sec.id;
        // fallback: check display style
        var sections = document.querySelectorAll('.content-section');
        for (var i = 0; i < sections.length; i++) {
            if (sections[i].style.display === 'block' || 
                (!sections[i].style.display && !sections[i].classList.contains('d-none'))) {
                return sections[i].id;
            }
        }
        return null;
    }

    // Get active tab IDs
    function getActiveTabs() {
        var tabs = [];
        document.querySelectorAll('.nav-link.active[data-bs-toggle="tab"], .nav-link.active[data-bs-toggle="pill"]').forEach(function(t) {
            var href = t.getAttribute('href') || t.getAttribute('data-bs-target');
            if (href) tabs.push(href);
        });
        return tabs;
    }

    // Selectors for the main content areas to update on each dashboard
    // These are the containers whose innerHTML we swap
    function getRefreshTargets() {
        var targets = [];

        // Admin dashboard: stats-grid, each content-section's card bodies
        var statsGrid = document.querySelector('.stats-grid');
        if (statsGrid) targets.push({ selector: '.stats-grid', el: statsGrid });

        // All card bodies with tables or dynamic content
        document.querySelectorAll('.card-body .table tbody').forEach(function(tbody) {
            // Create a unique selector using closest card's header text
            targets.push({ el: tbody, type: 'tbody' });
        });

        // Stat cards
        document.querySelectorAll('.stat-card').forEach(function(card) {
            targets.push({ el: card, type: 'stat-card' });
        });

        // Activity items
        var activityContainer = document.querySelector('.recent-activity .card-body, .activity-list');
        if (activityContainer) targets.push({ el: activityContainer, type: 'activity' });

        // Badge counts in sidebar
        document.querySelectorAll('.sidebar .badge, .sidebar-nav .badge').forEach(function(b) {
            targets.push({ el: b, type: 'badge' });
        });

        // Progress bars
        document.querySelectorAll('.progress-bar').forEach(function(pb) {
            targets.push({ el: pb, type: 'progress' });
        });

        return targets;
    }

    // Do the soft AJAX refresh
    function doRefresh() {
        if (isUserBusy() || isFetching) {
            scheduleRefresh(5000);
            return;
        }

        isFetching = true;

        // Save current state
        var scrollX = window.scrollX;
        var scrollY = window.scrollY;
        var activeSectionId = getActiveSectionId();
        var activeTabs = getActiveTabs();

        // Fetch current page via AJAX
        fetch(window.location.href, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin'
        })
        .then(function(response) {
            if (!response.ok) throw new Error('HTTP ' + response.status);
            return response.text();
        })
        .then(function(html) {
            // Parse the fetched HTML
            var parser = new DOMParser();
            var newDoc = parser.parseFromString(html, 'text/html');

            // Update the main content area
            // Try common content wrappers used across dashboards
            var contentSelectors = [
                '.main-content',           // admin dashboard
                '.col-lg-10.main-content', // admin
                '.container-fluid > .row', // general
                'main',                     // semantic main
                '.container'                // fallback
            ];

            var updated = false;
            for (var i = 0; i < contentSelectors.length; i++) {
                var oldEl = document.querySelector(contentSelectors[i]);
                var newEl = newDoc.querySelector(contentSelectors[i]);
                if (oldEl && newEl) {
                    // Swap inner HTML 
                    oldEl.innerHTML = newEl.innerHTML;
                    updated = true;
                    break;
                }
            }

            // If no main wrapper found, try swapping individual content sections
            if (!updated) {
                // Swap all content-section divs individually
                newDoc.querySelectorAll('.content-section').forEach(function(newSec) {
                    var oldSec = document.getElementById(newSec.id);
                    if (oldSec) {
                        oldSec.innerHTML = newSec.innerHTML;
                    }
                });

                // Also update stats grid
                var newStats = newDoc.querySelector('.stats-grid');
                var oldStats = document.querySelector('.stats-grid');
                if (newStats && oldStats) {
                    oldStats.innerHTML = newStats.innerHTML;
                }

                // Update sidebar badges
                var newBadges = newDoc.querySelectorAll('.sidebar .badge');
                var oldBadges = document.querySelectorAll('.sidebar .badge');
                newBadges.forEach(function(nb, idx) {
                    if (oldBadges[idx]) oldBadges[idx].textContent = nb.textContent;
                });

                updated = true;
            }

            if (updated) {
                // Restore active section (admin dashboard)
                if (activeSectionId) {
                    document.querySelectorAll('.content-section').forEach(function(sec) {
                        sec.classList.remove('active');
                        sec.style.display = 'none';
                    });
                    var targetSec = document.getElementById(activeSectionId);
                    if (targetSec) {
                        targetSec.classList.add('active');
                        targetSec.style.display = 'block';
                    }

                    // Re-activate sidebar link
                    document.querySelectorAll('.sidebar .nav-link, .section-link').forEach(function(link) {
                        link.classList.remove('active');
                        if (link.getAttribute('data-section') === activeSectionId) {
                            link.classList.add('active');
                        }
                    });
                }

                // Restore active tabs
                activeTabs.forEach(function(tabHref) {
                    var tabTrigger = document.querySelector(
                        '[data-bs-toggle="tab"][href="' + tabHref + '"], ' +
                        '[data-bs-toggle="tab"][data-bs-target="' + tabHref + '"], ' +
                        '[data-bs-toggle="pill"][href="' + tabHref + '"], ' +
                        '[data-bs-toggle="pill"][data-bs-target="' + tabHref + '"]'
                    );
                    if (tabTrigger && typeof bootstrap !== 'undefined') {
                        try { new bootstrap.Tab(tabTrigger).show(); } catch(e) { tabTrigger.click(); }
                    }
                });

                // Re-bind event listeners that were in the page scripts
                rebindEventListeners();

                // Restore scroll position
                window.scrollTo(scrollX, scrollY);
            }
        })
        .catch(function(err) {
            console.warn('[Auto-Refresh] Error:', err.message);
        })
        .finally(function() {
            isFetching = false;
            scheduleRefresh();
        });
    }

    // Re-bind event listeners after DOM swap
    function rebindEventListeners() {
        // Section links (admin dashboard sidebar navigation)
        document.querySelectorAll('.section-link').forEach(function(link) {
            // Remove old listener by cloning
            var newLink = link.cloneNode(true);
            link.parentNode.replaceChild(newLink, link);
            newLink.addEventListener('click', function(e) {
                e.preventDefault();
                var targetSection = this.getAttribute('data-section');
                if (!targetSection) return;

                document.querySelectorAll('.section-link').forEach(function(l) { l.classList.remove('active'); });
                document.querySelectorAll('.content-section').forEach(function(s) {
                    s.classList.remove('active');
                    s.style.display = 'none';
                });

                var sidebarLink = document.querySelector('.sidebar .section-link[data-section="' + targetSection + '"]');
                if (sidebarLink) sidebarLink.classList.add('active');

                var sec = document.getElementById(targetSection);
                if (sec) {
                    sec.classList.add('active');
                    sec.style.display = 'block';
                }
                window.scrollTo(0, 0);
            });
        });

        // Quick action card hover effects
        document.querySelectorAll('.quick-action-card').forEach(function(card) {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px) scale(1.02)';
            });
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });

        // View profile buttons
        document.querySelectorAll('.view-profile-btn').forEach(function(button) {
            button.addEventListener('click', function() {
                var profileName = document.getElementById('profileName');
                var profileEmail = document.getElementById('profileEmail');
                var profileRole = document.getElementById('profileRole');
                if (profileName) profileName.textContent = this.getAttribute('data-user-name') || '';
                if (profileEmail) profileEmail.textContent = this.getAttribute('data-user-email') || '';
                var role = this.getAttribute('data-user-role') || '';
                if (profileRole) profileRole.textContent = role.charAt(0).toUpperCase() + role.slice(1);

                var studentInfo = document.getElementById('studentProfileInfo');
                var supervisorInfo = document.getElementById('supervisorProfileInfo');
                if (studentInfo) studentInfo.classList.add('d-none');
                if (supervisorInfo) supervisorInfo.classList.add('d-none');

                if (role === 'student') {
                    var prog = document.getElementById('profileProgram');
                    var sem = document.getElementById('profileSemester');
                    if (prog) prog.textContent = this.getAttribute('data-program') || 'Not specified';
                    if (sem) sem.textContent = (this.getAttribute('data-semester') || 'Not specified');
                    if (studentInfo) studentInfo.classList.remove('d-none');
                } else if (role === 'supervisor') {
                    var deg = document.getElementById('profileDegree');
                    var spec = document.getElementById('profileSpecialization');
                    var aff = document.getElementById('profileAffiliation');
                    if (deg) deg.textContent = this.getAttribute('data-degree') || 'Not specified';
                    if (spec) spec.textContent = this.getAttribute('data-specialization') || 'Not specified';
                    if (aff) aff.textContent = this.getAttribute('data-affiliation') || 'Not specified';
                    if (supervisorInfo) supervisorInfo.classList.remove('d-none');
                }
            });
        });

        // View group members buttons
        document.querySelectorAll('.view-members-btn').forEach(function(button) {
            button.addEventListener('click', function() {
                var groupId = this.getAttribute('data-group-id');
                var modalBody = document.querySelector('#membersModal .modal-body');
                if (!modalBody) return;
                modalBody.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-primary" role="status"></div></div>';
                
                var membersModal = document.getElementById('membersModal');
                if (membersModal && typeof bootstrap !== 'undefined') {
                    new bootstrap.Modal(membersModal).show();
                }

                var url = window.location.origin + '/admin/group/' + groupId + '/members';
                fetch(url)
                    .then(function(r) { return r.json(); })
                    .then(function(members) {
                        var html = '';
                        if (members.length > 0) {
                            html = '<ul class="list-group">';
                            members.forEach(function(m) { html += '<li class="list-group-item">' + m.name + ' (' + m.email + ')</li>'; });
                            html += '</ul>';
                        } else {
                            html = '<p class="text-muted">No members assigned</p>';
                        }
                        modalBody.innerHTML = html;
                    })
                    .catch(function() { modalBody.innerHTML = '<p class="text-danger">Error loading members</p>'; });
            });
        });

        // Report download buttons
        document.querySelectorAll('.report-download-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var url = this.getAttribute('data-url');
                var originalText = this.innerHTML;
                var button = this;
                button.disabled = true;
                button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
                window.location.href = url;
                setTimeout(function() {
                    button.disabled = false;
                    button.innerHTML = originalText;
                }, 3000);
            });
        });

        // Sidebar toggle (mobile)
        var sidebarToggle = document.getElementById('sidebarToggle');
        var sidebarNav = document.getElementById('sidebarNav');
        var sidebarOverlay = document.getElementById('sidebarOverlay');
        if (sidebarToggle && sidebarNav) {
            sidebarToggle.addEventListener('click', function() {
                sidebarNav.classList.toggle('show');
                if (sidebarOverlay) sidebarOverlay.classList.toggle('show');
            });
            if (sidebarOverlay) {
                sidebarOverlay.addEventListener('click', function() {
                    sidebarNav.classList.remove('show');
                    sidebarOverlay.classList.remove('show');
                });
            }
        }

        // Student checkbox counters (admin add project modal)
        var projectCheckboxes = document.querySelectorAll('.project-student-checkbox');
        var projectCountSpan = document.getElementById('project_selected_count');
        if (projectCheckboxes.length > 0 && projectCountSpan) {
            projectCheckboxes.forEach(function(cb) {
                cb.addEventListener('change', function() {
                    projectCountSpan.textContent = document.querySelectorAll('#addProjectModal input[name="student_ids"]:checked').length;
                });
            });
        }
    }

    function scheduleRefresh(interval) {
        if (refreshTimer) clearTimeout(refreshTimer);
        refreshTimer = setTimeout(doRefresh, interval || REFRESH_INTERVAL);
    }

    // Start on page load
    function init() {
        scheduleRefresh();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Pause when page is hidden, resume when visible
    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            if (refreshTimer) clearTimeout(refreshTimer);
        } else {
            scheduleRefresh();
        }
    });
})();
