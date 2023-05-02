def style_sheet(key, theme_manager):
    return (f"QMenuBar {{"
            f"color: {theme_manager.get(key, 'color')};"
            f"background-color: {theme_manager.get(key, 'background-color')};"
            f"}}"
            f"QMenuBar::item::selected {{"
            f"background-color: {theme_manager.get(key, 'item:selected:background-color')};"
            f"}}")
