import gettext
import os

locales_dir = os.path.join(os.path.dirname(__file__), "locales")
gettext.bindtextdomain("bcut", locales_dir)
gettext.textdomain("bcut")
_ = gettext.gettext

# Example usage:
# print(_("Hello, World!"))
