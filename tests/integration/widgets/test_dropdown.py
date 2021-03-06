#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2017, Anaconda, Inc. All rights reserved.
#
# Powered by the Bokeh Development Team.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Boilerplate
#-----------------------------------------------------------------------------
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest ; pytest

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports

# External imports

# Bokeh imports
from bokeh.core.enums import ButtonType
from bokeh.layouts import column
from bokeh.models import Circle, ColumnDataSource, CustomAction, CustomJS, Dropdown, Plot, Range1d
from bokeh._testing.util.selenium import RECORD

#-----------------------------------------------------------------------------
# Tests
#-----------------------------------------------------------------------------

pytest_plugins = (
    "bokeh._testing.plugins.bokeh",
)

# XXX (bev) split dropdown (i.e. with default value) has serious problems

items = [("Item 1", "item_1_value"), ("Item 2", "item_2_value"), ("Item 3", "item_3_value")]

@pytest.mark.integration
@pytest.mark.selenium
class Test_Dropdown(object):

    def test_displays_menu_items(self, bokeh_model_page):
        button = Dropdown(label="Dropdown button", menu=items, css_classes=["foo"])

        page = bokeh_model_page(button)

        button_div = page.driver.find_element_by_class_name('foo')
        button = button_div.find_element_by_tag_name("button")
        assert button.text == "Dropdown button"
        button.click()

        links = page.driver.find_elements_by_css_selector('ul li a')
        assert len(links) == 3

        for i, link in enumerate(links):
            assert link.text == items[i][0]
            assert link.get_attribute('data-value') == items[i][1]

    @pytest.mark.parametrize('typ', list(ButtonType))
    def test_displays_button_type(self, typ, bokeh_model_page):
        button = Dropdown(label="Dropdown button", menu=items, button_type=typ, css_classes=["foo"])

        page = bokeh_model_page(button)

        button_div = page.driver.find_element_by_class_name('foo')
        button = button_div.find_element_by_tag_name("button")
        assert typ in button.get_attribute('class')

    def test_server_on_change_round_trip(self, bokeh_server_page):
        def modify_doc(doc):
            source = ColumnDataSource(dict(x=[1, 2], y=[1, 1]))
            plot = Plot(plot_height=400, plot_width=400, x_range=Range1d(0, 1), y_range=Range1d(0, 1), min_border=0)
            plot.add_glyph(source, Circle(x='x', y='y', size=20))
            plot.add_tools(CustomAction(callback=CustomJS(args=dict(s=source), code=RECORD("data", "s.data"))))
            button = Dropdown(label="Dropdown button", menu=items, css_classes=["foo"])
            def cb(attr, old, new):
                if new == "item_1_value":
                    source.data = dict(x=[10, 20], y=[10, 10])
                elif new == "item_2_value":
                    source.data = dict(x=[100, 200], y=[100, 100])
                elif new == "item_3_value":
                    source.data = dict(x=[1000, 2000], y=[1000, 1000])
            button.on_change('value', cb)
            doc.add_root(column(button, plot))

        page = bokeh_server_page(modify_doc)

        button = page.driver.find_element_by_class_name('foo')
        button.click()
        item = page.driver.find_element_by_link_text("Item 1")
        item.click()

        page.click_custom_action()

        results = page.results
        assert results ==  {'data': {'x': [10, 20], 'y': [10, 10]}}

        button = page.driver.find_element_by_class_name('foo')
        button.click()
        item = page.driver.find_element_by_link_text("Item 3")
        item.click()

        page.click_custom_action()

        results = page.results
        assert results ==  {'data': {'x': [1000, 2000], 'y': [1000, 1000]}}

        button = page.driver.find_element_by_class_name('foo')
        button.click()
        item = page.driver.find_element_by_link_text("Item 2")
        item.click()

        page.click_custom_action()

        results = page.results
        assert results ==  {'data': {'x': [100, 200], 'y': [100, 100]}}

        # XXX (bev) disabled until https://github.com/bokeh/bokeh/issues/7970 is resolved
        #assert page.has_no_console_errors()

    def test_callback_property_executes(self, bokeh_model_page):
        button = Dropdown(label="Dropdown button", menu=items, css_classes=["foo"])
        button.callback = CustomJS(code=RECORD("value", "cb_obj.value"))

        page = bokeh_model_page(button)

        button = page.driver.find_element_by_class_name('foo')
        button.click()
        item = page.driver.find_element_by_link_text("Item 1")
        item.click()

        results = page.results
        assert results ==  {'value': "item_1_value"}

        button = page.driver.find_element_by_class_name('foo')
        button.click()
        item = page.driver.find_element_by_link_text("Item 3")
        item.click()

        results = page.results
        assert results ==  {'value': "item_3_value"}

        button = page.driver.find_element_by_class_name('foo')
        button.click()
        item = page.driver.find_element_by_link_text("Item 2")
        item.click()

        results = page.results
        assert results ==  {'value': "item_2_value"}

        assert page.has_no_console_errors()

    def test_js_on_change_executes(self, bokeh_model_page):
        button = Dropdown(label="Dropdown button", menu=items, css_classes=["foo"])
        button.js_on_change('value', CustomJS(code=RECORD("value", "cb_obj.value")))

        page = bokeh_model_page(button)

        button = page.driver.find_element_by_class_name('foo')
        button.click()
        item = page.driver.find_element_by_link_text("Item 1")
        item.click()

        results = page.results
        assert results ==  {'value': "item_1_value"}

        button = page.driver.find_element_by_class_name('foo')
        button.click()
        item = page.driver.find_element_by_link_text("Item 3")
        item.click()

        results = page.results
        assert results ==  {'value': "item_3_value"}

        button = page.driver.find_element_by_class_name('foo')
        button.click()
        item = page.driver.find_element_by_link_text("Item 2")
        item.click()

        results = page.results
        assert results ==  {'value': "item_2_value"}

        assert page.has_no_console_errors()
