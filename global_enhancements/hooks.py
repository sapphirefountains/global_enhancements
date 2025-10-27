app_name = "global_enhancements"
app_title = "Global Enhancements"
app_publisher = "Sapphire Fountains"
app_description = "Enhance features on Frappe globally."
app_email = "info@sapphirefountains.com"
app_license = "mit"

# --- Document Events ---
# This hook triggers on every document save
doc_events = {
    "*": {
        "on_update": "global_enhancements.global_enhancements.mentions.process_mentions_on_update"
    }
}

# --- Include JS and CSS in the desk build ---
# This bundles the assets for every page load
app_include_js = [
    "https://cdnjs.cloudflare.com/ajax/libs/at.js/1.5.4/js/jquery.atwho.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/Caret.js/0.3.1/jquery.caret.min.js",
    "/assets/global_enhancements/js/mentions.js"
]
app_include_css = "https://cdnjs.cloudflare.com/ajax/libs/at.js/1.5.4/css/jquery.atwho.min.css"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "global_enhancements",
# 		"logo": "/assets/global_enhancements/logo.png",
# 		"title": "Global Enhancements",
# 		"route": "/global_enhancements",
# 		"has_permission": "global_enhancements.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/global_enhancements/css/global_enhancements.css"
# app_include_js = "/assets/global_enhancements/js/global_enhancements.js"

# include js, css files in header of web template
# web_include_css = "/assets/global_enhancements/css/global_enhancements.css"
# web_include_js = "/assets/global_enhancements/js/global_enhancements.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "global_enhancements/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "global_enhancements/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "global_enhancements.utils.jinja_methods",
# 	"filters": "global_enhancements.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "global_enhancements.install.before_install"
# after_install = "global_enhancements.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "global_enhancements.uninstall.before_uninstall"
# after_uninstall = "global_enhancements.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "global_enhancements.utils.before_app_install"
# after_app_install = "global_enhancements.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "global_enhancements.utils.before_app_uninstall"
# after_app_uninstall = "global_enhancements.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "global_enhancements.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"global_enhancements.tasks.all"
# 	],
# 	"daily": [
# 		"global_enhancements.tasks.daily"
# 	],
# 	"hourly": [
# 		"global_enhancements.tasks.hourly"
# 	],
# 	"weekly": [
# 		"global_enhancements.tasks.weekly"
# 	],
# 	"monthly": [
# 		"global_enhancements.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "global_enhancements.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "global_enhancements.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "global_enhancements.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["global_enhancements.utils.before_request"]
# after_request = ["global_enhancements.utils.after_request"]

# Job Events
# ----------
# before_job = ["global_enhancements.utils.before_job"]
# after_job = ["global_enhancements.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"global_enhancements.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

