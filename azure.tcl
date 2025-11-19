
# Simplified Azure-like theme
ttk::style theme create azure -parent clam -settings {
    ttk::style configure . -background "#f2f2f2"
    ttk::style configure TFrame -background "#f2f2f2"
    ttk::style configure TLabel -background "#f2f2f2" -foreground "#000000"
    ttk::style configure TButton -padding 8 -background "#0078d7" -foreground "white" -font "Segoe UI 11 bold"
    ttk::style map TButton -background {active "#005a9e"}
}
