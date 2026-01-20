frappe.ready(function () {
	// 1. Default Landing Page Logic
	// Check if the current route is empty (root) or just 'desk'
	const route = frappe.get_route();
	if (!route || route.length === 0 || (route.length === 1 && route[0] === "desk")) {
		frappe.set_route("desk", "home");
	}

	// 2. Sidebar "Home" Link Injection
	const HOME_ITEM_CLASS = "custom-home-sidebar-item";

	const injectHomeItem = () => {
		// Prevent duplicate injection
		if ($(`.${HOME_ITEM_CLASS}`).length > 0) return;

		// Find the "Workspaces" sidebar item.
		// We look for a label containing "Workspaces" and traverse up to the main item container.
		// Standard Frappe sidebar structure usually involves .standard-sidebar-item or .sidebar-item-container
		const $workspacesLabel = $('.sidebar-item-label:contains("Workspaces")');

		if ($workspacesLabel.length === 0) return;

		// Find the actionable item container (usually the parent or close ancestor)
		const $workspacesItem = $workspacesLabel.closest(".standard-sidebar-item");

		if ($workspacesItem.length === 0) return;

		// Clone the item to inherit styles (padding, hover effects, etc.)
		const $homeItem = $workspacesItem.clone();

		// Add custom class for identification and preventing duplicates
		$homeItem.addClass(HOME_ITEM_CLASS);
		$homeItem.removeClass("selected"); // Ensure it doesn't look active initially

		// Update the label
		$homeItem.find(".sidebar-item-label").text("Home");

		// Update the icon
		// Frappe icons are usually <use href="#icon-name">
		const $iconUse = $homeItem.find(".icon use");
		if ($iconUse.length > 0) {
			$iconUse.attr("href", "#icon-home");
		} else {
			// Fallback: try to replace the icon container content if structure is different
			$homeItem.find(".sidebar-item-icon").html(frappe.utils.icon("home", "md"));
		}

		// Update the click behavior
		$homeItem.off("click"); // Remove existing listeners from the clone
		$homeItem.on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			frappe.set_route("desk", "home");
		});

		// Insert the Home item BEFORE the Workspaces item
		$workspacesItem.before($homeItem);
	};

	// Use MutationObserver to watch for Sidebar rendering
	// The sidebar might be re-rendered during navigation or initialization
	const observer = new MutationObserver((mutations) => {
		// Quick check to see if we need to inject
		if ($(`.${HOME_ITEM_CLASS}`).length === 0) {
			injectHomeItem();
		}
	});

	// Observe the body because the sidebar container might be created dynamically
	observer.observe(document.body, {
		childList: true,
		subtree: true,
	});

	// Try injecting immediately in case DOM is already ready
	injectHomeItem();
});
