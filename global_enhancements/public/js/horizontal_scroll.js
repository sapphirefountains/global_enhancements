frappe.views.KanbanView = class KanbanView extends frappe.views.KanbanView {
    render() {
        super.render();
        if (this.doctype === 'Opportunity') {
            const observer = new MutationObserver((mutationsList, observer) => {
                for(const mutation of mutationsList) {
                    if (mutation.type === 'childList') {
                        const kanbanContainer = document.querySelector('.kanban-column');
                        if (kanbanContainer) {
                            const parentContainer = kanbanContainer.parentElement;
                            parentContainer.classList.add('horizontal-scroll-container');
                            parentContainer.addEventListener('wheel', function(e) {
                                if (e.target.closest('.kanban-card-container')) {
                                    return;
                                }
                                if (e.deltaY !== 0) {
                                    e.preventDefault();
                                    parentContainer.scrollBy({
                                        left: e.deltaY,
                                        behavior: 'smooth'
                                    });
                                }
                            });
                            observer.disconnect();
                            break;
                        }
                    }
                }
            });

            observer.observe(document.body, { childList: true, subtree: true });
        }
    }
};
