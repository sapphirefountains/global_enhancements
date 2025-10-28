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
            insertTpl: "${label}", // We'll handle insertion ourselves
            appendTo: $editor.parent(),
            functionOverrides: {
                insert: function(content, $li) {
                    var quill = Quill.find($editor.get(0));
                    if (quill) {
                        var range = quill.getSelection(true); // Get focus for the current range
                        if (range) {
                            var mention = $li.data('item-data');
                            var text = quill.getText(0, range.index);
                            var at_pos = text.lastIndexOf('@');

                            if (at_pos > -1) {
                                var Delta = quill.constructor.import('delta');
                                var delta = new Delta()
                                    .retain(at_pos)
                                    .delete(range.index - at_pos) // Delete the typed query
                                    .insert(mention.label, { 'link': '/app/user/' + mention.value })
                                    .insert(' '); // Add a space after the mention

                                quill.updateContents(delta, 'user');
                                // Move the cursor after the inserted mention and space
                                quill.setSelection(at_pos + mention.label.length + 1, 0, 'silent');
                            }
                        }
                    }
                }
            },
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
                // The position callback is crucial for placing the popup correctly
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
                    // We must return the offset for at.js to use
                    return offset;
                }
            }
        });
    });
});
