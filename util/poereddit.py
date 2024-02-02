import praw
from datetime import datetime, timedelta
import re
from util import sale


def get_quick_info_widget(subreddit):
    """
    @param: subreddit The target instance of praw.Subreddit
    Get an instance of the Quick Info widget, where the Daily Deals information
    is posted. If not found, return None.

    """
    sidebar_widgets = subreddit.widgets.sidebar
    for widget in sidebar_widgets:
        if isinstance(widget, praw.models.TextArea):
            return widget

    return None
def replace_widget_text(widget, text):
    """
    Change the widget's text to the specified text
    @param: praw.models.TextArea: Target TextArea widget
    @param: text: The text to change to
    """
    widget.mod.update(text=text)

def make_new_text(old_text, last_sale_time):
    """
    Create updated sidebar text
    @param old_text outdated sidebar text
    @param last_sale_time last sale time
    @return updated sidebar markdown
    """
    last_sale_pattern = r"Last sale: .*\n"
    next_sale_pattern = r"Next sale: .*\n"

    # Last / Current sale
    start_time = last_sale_time[0]
    end_time = last_sale_time[1]
    start_time_string = start_time.strftime('%d %B %Y')
    end_time_string = end_time.strftime('%d %B %Y')

    # Next sale
    next_start_time = start_time + timedelta(weeks=3)
    next_end_time = end_time + timedelta(weeks=3)
    next_start_time_string = next_start_time.strftime('%d %B %Y')
    next_end_time_string = next_end_time.strftime('%d %B %Y')

    new_text = re.sub(last_sale_pattern, f"Last sale: {start_time_string} - {end_time_string}\n", old_text)
    new_text = re.sub(next_sale_pattern, f"Next sale: {next_start_time_string} - {next_end_time_string}\n", new_text)

    return new_text


def update_sidebar(reddit):
    """
    Update the Stash Tab Sale dates in the sidebar.
    @param: reddit: praw.models.Reddit object
    """
    subreddit = reddit.subreddit("pathofexile")
    quick_info_widget = get_quick_info_widget(subreddit)
    old_text = quick_info_widget.text

    # Get sale time information
    sale_times = sale.get_current_stash_sale_dates()
    if sale_times: # Not None, which means a sale is currently happening
        # The update the sidebar
        new_text = make_new_text(old_text, sale_times)
        replace_widget_text(quick_info_widget, new_text)
    # Otherwise don't update anything

