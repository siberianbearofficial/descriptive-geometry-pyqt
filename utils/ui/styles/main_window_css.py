def style_sheet(key, theme_manager):
    return (f"background-color: {theme_manager.get(key, 'background-color')};"
            f"")
