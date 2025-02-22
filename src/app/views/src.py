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

Welcome to **Trimshh**, the ultimate tool for automatically removing silent segments from videos. Whether you're editing podcasts, vlogs, lectures, or any other footage, this app helps you streamline your content by cutting out unnecessary pauses—saving you time and improving engagement.

### Key Features
✅ **Automatic Silence Detection** : Detects and removes silent parts with precision.  
✅ **Fast Processing** : Optimized to handle videos quickly without compromising quality.  
✅ **Customizable Thresholds** : Adjust sensitivity to control how much silence is removed.  
✅ **User-Friendly Interface** : Simple and intuitive design for easy operation.  
✅ **Batch Processing** : Edit multiple videos at once—perfect for podcasts or long recordings.  

Built with efficiency in mind, **Trimshh** leverages the power of FFmpeg to ensure high-quality output while maintaining an intuitive user experience.

For support or feedback, feel free to reach out to **superyngo@gmail.com**.
"""

LICENSE_TEXT = f"""
**Trimshh End-User License Agreement (EULA)**  

_Last Updated: 2025.2.18_  

**IMPORTANT – READ CAREFULLY:**  
This End-User License Agreement ("EULA") is a legal agreement between you (either an individual or a single entity) and WENA ("Licensor") for the software product "Trimshh" ("App"), including any associated media, printed materials, and online or electronic documentation. By installing, copying, or otherwise using the App, you agree to be bound by the terms of this EULA. If you do not agree to these terms, do not install or use the App.

---

### 1. GRANT OF LICENSE  

Subject to the terms and conditions of this EULA, Licensor hereby grants you a non-exclusive, non-transferable license to install and use the App on any device that you own or control solely for your personal or internal business purposes.  

---

### 2. RESTRICTIONS  

You agree that you will not:  
- Reverse engineer, decompile, disassemble, or otherwise attempt to discover the source code of the App, except to the extent expressly permitted by applicable law.  
- Modify, or create derivative works based on, the App in whole or in part.  
- Distribute, sell, lease, rent, sublicense, or otherwise transfer your rights under this EULA to any third party.  
- Remove or obscure any proprietary notices or labels on the App.  

---

### 3. THIRD-PARTY COMPONENTS  

This App utilizes several third-party components that are subject to their own licenses. The licenses for these components govern your use of the respective components. Notable components include:  

- **FFmpeg (Win64 Binary, compiled without GPL code):** Licensed under LGPL. Refer to the [FFmpeg website](https://ffmpeg.org/) for full details.  
- **Python Textual Package:** Licensed under the MIT License.  
- **Python textual_fspicker Package:** Licensed under the MIT License.  
- **Python Rich Package:** Licensed under the MIT License.  
- **miek770/python_uv_nuitka_tui_template:** Licensed under the MIT License.  
- **uv:** Licensed under the MIT License.  
- **mypy:** Licensed under the MIT License.  
- **Nuitka:** Licensed under the Apache-2.0 License.  
- **Inno Setup Compiler:** Distributed under the terms specified on the [Inno Setup website](http://www.jrsoftware.org/isinfo.php).  

All third-party components remain the property of their respective authors and licensors. You should review the license terms of each component to ensure your compliance.  

---

### 4. DISTRIBUTION  

This App is distributed exclusively via the Microsoft Store. Your use of the App is also subject to any additional terms and conditions imposed by Microsoft.  

---

### 5. UPDATES AND SUPPORT  

Licensor may, at its discretion, provide updates, patches, or modifications to the App exclusively through the Microsoft Store. No direct support is provided by Licensor. For any issues, users should refer to available online resources and community forums or submit feedback via the Microsoft Store as applicable.  

---

### 6. DISCLAIMER OF WARRANTIES  

THE APP IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT. LICENSOR DOES NOT WARRANT THAT THE APP WILL MEET YOUR REQUIREMENTS OR THAT ITS OPERATION WILL BE UNINTERRUPTED OR ERROR-FREE.  

---

### 7. LIMITATION OF LIABILITY  

IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, LOSS OF PROFITS, DATA, OR OTHER INTANGIBLE LOSSES) ARISING OUT OF OR IN CONNECTION WITH THE USE OR INABILITY TO USE THE APP, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.  

---

### 8. TERMINATION  

This EULA is effective until terminated. Your rights under this EULA will terminate automatically without notice if you fail to comply with any term(s) of this agreement. Upon termination, you must cease all use of the App and destroy all copies in your possession.  

---

### 9. GOVERNING LAW  

This EULA shall be governed by and construed in accordance with the laws of Taiwan. Any disputes arising under or in connection with this EULA shall be subject to the exclusive jurisdiction of the courts located in Taiwan.  

---

### 10. ENTIRE AGREEMENT  

This EULA constitutes the entire agreement between you and Licensor regarding the use of the App and supersedes all prior or contemporaneous understandings or agreements, whether written or oral, regarding such subject matter.  

---

**By installing or using Trimshh, you acknowledge that you have read, understood, and agree to be bound by the terms and conditions of this EULA.**  

For any questions regarding this license, please contact:  
📧 **superyngo@gmail.com**  
🏢 **WENA** (Company name pending registration)  

---
"""
