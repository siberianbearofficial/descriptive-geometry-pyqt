def style_sheet(key, theme_manager):
    return (f"background-color: {theme_manager.get(key, 'background-color')};"
            f"border-radius: {theme_manager.get(key, 'border-radius')};")
