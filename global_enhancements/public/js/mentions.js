$(document).ready(function() {
    // Use event delegation to attach the logic to any text editor that comes into focus
    $(document).on('focus', '.ql-editor', function() {
        var $editor = $(this);
        // Check if At.js is already bound to this editor
        if ($editor.data('atwho-bound')) {
            return; // Already initialized
        }
        $editor.data('atwho-bound', true); // Mark as initialized

        $editor.atwho({
            at: "@",
            limit: 10,
            displayTpl: "<li>${label} <small>(${value})</small></li>",
            insertTpl: null,
            appendTo: $editor.parent(),
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
                },
                position: function(offset) {
                    var quill = Quill.find($editor.get(0));
                    if (quill) {
                        var range = quill.getSelection();
                        if (range) {
                            var bounds = quill.getBounds(range.index);
                            offset.top = bounds.bottom;
                            offset.left = bounds.left;
                        }
                    }
                },
                beforeInsert: function(value, $li) {
                    var quill = Quill.find($editor.get(0));
                    if (quill) {
                        var range = quill.getSelection();
                        if (range) {
                            var mention = $li.data('item-data');
                            var text = quill.getText(0, range.index);
                            var at_pos = text.lastIndexOf('@');
                            if (at_pos > -1) {
                                quill.deleteText(at_pos, range.index - at_pos);
                                quill.insertText(at_pos, mention.label, { 'link': '/app/user/' + mention.value });
                                quill.insertText(at_pos + mention.label.length, " ");
                                quill.setSelection(at_pos + mention.label.length + 1);
                            }
                        }
                    }
                    return false; // Prevent at.js from inserting anything
                }
            }
        });
    });
});
