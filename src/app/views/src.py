from app import constants

CSS = """
Header {
    /* height: 3; */
    background: white;
    dock: top;
}

Footer {
    /* height: 3; */
    background: white;
    dock: bottom;
}



/* Animated button hover effects */
Button {
    background: $primary;
    transition: background 100ms;
}

Button:hover {
    background: $secondary;
    text-style: bold;
}

.HoverBorder{
    border: tall $primary
}


SelectionList:hover, Input:hover, .HoverBorder:hover, SelectCurrent:hover{
    border: tall $secondary;
}

SelectionList:focus, Input:focus, .HoverBorder:focus, Select:focus > SelectCurrent, Select.-expanded > SelectCurrent{
    border: tall $secondary;
}


Sidebar {
    background: $panel;
}


MainContent{
    background: $background;
}

MyModal{
    height:100%;
    width:100%;
    align: center middle;
    text-align: center;
    content-align: center middle;
    overflow: auto;
    overflow-x: auto;
    overflow-y: auto;
}

.MyModalContent{
    border: solid $panel;
    padding: 1 3;
    width:75%;
    height:75%; 
    overflow: auto;
    overflow-x: auto;
    overflow-y: auto;
}

.Border_Panel{
    border: $panel;
}

.Height_One{
    height: 1;
}

.Height_Three, Button, Input{
    height: 3;
} 


.MinHeight_Five{
    min-height: 5;
}

.MinHeight_Three{
    min-height: 3;
}

.MinHeight_Ten{
    min-height: 10;
}


.Action{
    width: 1fr;
    margin: 1;
    height: 3;
}
.Margin_One_Down{
    margin: 0 0 1 0;
}

.Margin_One_Right{
    margin: 0 1 0 0;
}

.H_One_FR{
    width: 1fr;
}
.H_Two_FR{
    width: 2fr;
}
.H_Three_FR{
    width: 3fr;
}
.H_Four_FR{
    width: 4fr;
}

.H_Eight_FR{
    width: 8fr;
}

.V_Half_FR{
    height: 0.5fr;
}

.V_One_FR{
    height: 1fr;
}
.V_Custom_FR{
    height: 1.3fr;
}

.V_One_Half_FR{
    height: 1.5fr;
}

.V_Two_FR{
    height: 2fr;
}
.V_Three_FR{
    height: 3fr;
}
.V_Four_FR{
    height: 4fr;
}

.V_Five_FR{
    height: 5fr;
}

.Hidden {
    display: none;
}

.ButtonA{
    margin-right: 1;
}


.ButtonB{
    margin-left: 1;
}

.Center_All {
    align: center middle;
    text-align: center;
    content-align: center middle;
}



.ScrollAuto {
    overflow: auto;
    overflow-x: auto;
    overflow-y: auto;
}


.Margin_One {
    margin: 1;
}

.Rendering{
    background: orange; 
    text-style: bold;
}

.Done {
    background: green; 
    text-style: bold; 
}



ListItem.--highlight {
    background: $accent;
}

"""

ABOUT_TEXT = f"""
# About

Welcome to **{constants.APP_NAME}**, the ultimate tool for automatically removing silent segments from videos. Whether you're editing podcasts, vlogs, lectures, or any other footage, this app helps you streamline your content by cutting out unnecessary pauses—saving you time and improving engagement.

### Key Features
✅ **Automatic Silence Detection** : Detects and removes silent parts with precision.  
✅ **Fast Processing** : Optimized to handle videos quickly without compromising quality.  
✅ **Customizable Thresholds** : Adjust sensitivity to control how much silence is removed.  
✅ **User-Friendly Interface** : Simple and intuitive design for easy operation.  
✅ **Batch Processing** : Edit multiple videos at once—perfect for podcasts or long recordings.  

Built with efficiency in mind, **{constants.APP_NAME}** leverages the power of FFmpeg to ensure high-quality output while maintaining an intuitive user experience.

For support or feedback, feel free to reach out to **{constants.CONTACT_INFO.EMAIL}**.

"""

LICENSE_TEXT = f"""
# License Information

## Application License
Copyright (c) 2025 {constants.AUTHOR}  
  
## Third-Party Licenses
This application utilizes the following third-party software, each subject to their respective licenses:

### FFmpeg (Win64 Binary)
- **License:** LGPL v2.1 (for dynamically linked usage)
- **Website:** [FFmpeg](https://ffmpeg.org)
- **Binary Provider:** [GitHub - BtbN/FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds)

### Python Textual Package
- **License:** MIT
- **Repository:** [GitHub - Textualize/textual](https://github.com/Textualize/textual)

### Python textual_fspicker Package
- **License:** MIT
- **Repository:** [GitHub - Textualize/textual-fspicker](https://github.com/Textualize/textual-fspicker)
- **Dependency:** Uses the Textual package

### Python Rich Package
- **License:** MIT
- **Repository:** [GitHub - Textualize/rich](https://github.com/Textualize/rich)
- **Included as part of Textual**

### miek770/python_uv_nuitka_tui_template
- **License:** MIT
- **Repository:** [GitHub - miek770/python_uv_nuitka_tui_template](https://github.com/Textualize/textual)
- **Dependency:** Used as a template for building

## Development and Compilation Tools
The following tools are used for development and distribution but are not part of the final distributed application:

- **uv** (Package Manager) - MIT License
- **mypy** (Type Checking) - MIT License
- **Nuitka** (Compilation to Win32 Binary) - Apache License 2.0

## Disclaimer
This software is distributed "as-is" without any warranties. The respective licenses of third-party software components apply independently. Ensure compliance with their terms when distributing or modifying this application.

For inquiries regarding licensing, please contact {constants.CONTACT_INFO.EMAIL}.
"""

Utizied = """
FFmpeg (Win64 Binary)
Python Textual Package
Python textual_fspicker Package
Python Rich Package
miek770/python_uv_nuitka_tui_template
uv
mypy
Nuitka
Inno Setup Compiler
"""
