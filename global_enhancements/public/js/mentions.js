$(document).ready(function() {
    // Use event delegation to attach the logic to any text editor that comes into focus
    $(document).on('focus', '.ql-editor', function() {
        // Check if At.js is already bound to this editor
        if ($(this).data('atwho-bound')) {
            return; // Already initialized
        }
        $(this).data('atwho-bound', true); // Mark as initialized

        $(this).atwho({
            at: "@",
            limit: 10,
            displayTpl: "<li>${label} <small>(${value})</small></li>",
            insertTpl: '<a href="/app/user/${value}" class="mention-link">${label}</a>',
            callbacks: {
                remoteFilter: function(query, callback) {
                    frappe.call({
                        method: 'global_enhancements.global_enhancements.api.search_users',
                        args: {
                            search_term: query
                        },
                        callback: function(r) {
                            if (r.message) {
                                callback(r.message);
                            }
                        }
                    });
                }
            }
        });
    });
});

