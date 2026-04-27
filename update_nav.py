import os
import re
import shutil

# The new unified navigation block to insert
NEW_NAV = """    <nav class="glass border-b border-white/10 p-4 md:p-6 sticky top-0 z-50">
        <div class="container mx-auto flex flex-wrap items-center justify-between gap-4">

            <div class="flex items-center gap-4">
                <a href="index.html" class="hover:opacity-80 transition-opacity">
                    <h1 class="text-2xl md:text-3xl font-black italic tracking-tighter uppercase leading-none">VPIN<span class="text-orange-500">HUB</span></h1>
                </a>
            </div>

            <div class="hidden xl:flex items-center gap-6 text-[10px] md:text-xs font-bold uppercase tracking-widest">
                <a href="https://discord.gg/rnaRKNgCjB" target="_blank" class="text-indigo-400 hover:text-indigo-300 transition-colors">Join Our Discord</a>
                <span class="text-white/20">|</span>
                <a href="competition/" class="text-orange-400 hover:text-orange-300 transition-colors">Competition</a>

                <div class="relative group py-2">
                    <button class="text-gray-300 hover:text-emerald-400 flex items-center gap-2 transition-colors focus:outline-none uppercase tracking-widest">
                        Tutorials <span class="text-[8px]">▼</span>
                    </button>
                    <div class="nav-dropdown absolute top-full left-1/2 -translate-x-1/2 mt-1 w-64 bg-slate-900 border border-white/10 rounded-xl shadow-2xl flex flex-col overflow-hidden z-50">
                        <div class="bg-white/5 px-4 py-2 border-b border-white/10">
                            <span class="text-[9px] text-gray-500 font-black">GUIDES & TUTORIALS</span>
                        </div>
                        <a href="how-to-build-a-vpin-cab.html" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>How to Build a VPIN Cab</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="how-to-update-vpin.html" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>How to Update VPIN</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="how-to-setup-altsound2.html" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>How to Setup AltSound2</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="how-to-play-pinball.html" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>How to Play Pinball</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="how-to-stream-pinball.html" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>How to Stream Pinball</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="vpx-table-tutorials.html" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>VPX Table Tutorials</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="fp-table-tutorials.html" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>FP Table Tutorials</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="fp-aio-update.html" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white flex justify-between items-center transition-colors">
                            <span>FP All-in-One</span> <span class="text-[10px]">↗</span>
                        </a>
                    </div>
                </div>

                <a href="interviews.html" class="text-gray-300 hover:text-fuchsia-400 transition-colors">Interviews</a>
                <span class="text-white/20">|</span>
                <a href="showcase.html" class="text-gray-300 hover:text-cyan-400 transition-colors">Latest Tables</a>

                <div class="relative group py-2">
                    <button class="text-gray-300 hover:text-cyan-400 flex items-center gap-2 transition-colors focus:outline-none uppercase tracking-widest">
                        Downloads <span class="text-[8px]">▼</span>
                    </button>
                    <div class="nav-dropdown absolute top-full right-0 mt-1 w-64 bg-slate-900 border border-white/10 rounded-xl shadow-2xl flex flex-col overflow-hidden z-50">
                        <div class="bg-white/5 px-4 py-2 border-b border-white/10">
                            <span class="text-[9px] text-gray-500 font-black">ESSENTIAL SOFTWARE</span>
                        </div>
                        <a href="https://www.nailbuster.com/wikipinup/doku.php?id=baller_installer" target="_blank" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>PinUp Popper 'Baller'</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="https://github.com/vpinball/vpinball/releases" target="_blank" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>VPX Latest</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="https://github.com/vpinball/b2s-backglass/releases" target="_blank" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>B2S Server Latest</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="https://github.com/freezy/dmd-extensions/releases" target="_blank" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>Freezy DMDEXT Latest</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="https://github.com/vbousquet/flexdmd/releases/" target="_blank" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>FLEX DMD Latest</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="https://configtool.vpuniverse.com/app/home" target="_blank" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white border-b border-white/5 flex justify-between items-center transition-colors">
                            <span>DOF Tool Config V3</span> <span class="text-[10px]">↗</span>
                        </a>
                        <a href="https://vpuniverse.com/files/file/14807-future-pinball-and-bam-essentials-all-in-one/" target="_blank" class="px-4 py-3 hover:bg-white/10 text-gray-300 hover:text-white flex justify-between items-center transition-colors">
                            <span>FP Latest</span> <span class="text-[10px]">↗</span>
                        </a>
                    </div>
                </div>
            </div>

            <button id="menu-btn" class="xl:hidden bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg text-white transition-colors font-bold text-sm uppercase tracking-widest">
                MENU ☰
            </button>
        </div>

        <div id="mobile-menu" class="xl:hidden flex flex-col gap-4 mt-4 pt-4 border-t border-white/10 text-xs font-bold uppercase tracking-widest px-2 pb-2">
            <a href="https://discord.gg/rnaRKNgCjB" target="_blank" class="text-indigo-400 hover:text-indigo-300">Join Our Discord</a>
            <a href="competition/" class="text-orange-400 hover:text-orange-300">Competition</a>

            <div class="pt-2 pb-2">
                <span class="text-gray-500 mb-3 block">Tutorials</span>
                <div class="flex flex-col gap-3 pl-4 border-l-2 border-white/10">
                    <a href="how-to-build-a-vpin-cab.html" class="text-gray-400 hover:text-white text-[10px]">How to Build a VPIN Cab</a>
                    <a href="how-to-update-vpin.html" class="text-gray-400 hover:text-white text-[10px]">How to Update VPIN</a>
                    <a href="how-to-setup-altsound2.html" class="text-gray-400 hover:text-white text-[10px]">How to Setup AltSound2</a>
                    <a href="how-to-play-pinball.html" class="text-gray-400 hover:text-white text-[10px]">How to Play Pinball</a>
                    <a href="how-to-stream-pinball.html" class="text-gray-400 hover:text-white text-[10px]">How to Stream Pinball</a>
                    <a href="vpx-table-tutorials.html" class="text-gray-400 hover:text-white text-[10px]">VPX Table Tutorials</a>
                    <a href="fp-table-tutorials.html" class="text-gray-400 hover:text-white text-[10px]">FP Table Tutorials</a>
                    <a href="fp-aio-update.html" class="text-gray-400 hover:text-white text-[10px]">FP All-in-One</a>
                </div>
            </div>

            <a href="interviews.html" class="text-fuchsia-400 hover:text-fuchsia-300">Interviews</a>
            <a href="showcase.html" class="text-cyan-400 hover:text-cyan-300">Latest Tables</a>

            <div class="pt-2 pb-2">
                <span class="text-gray-500 mb-3 block">Software Downloads</span>
                <div class="flex flex-col gap-3 pl-4 border-l-2 border-white/10">
                    <a href="https://www.nailbuster.com/wikipinup/doku.php?id=baller_installer" target="_blank" class="text-gray-400 hover:text-white text-[10px]">PinUp Popper 'Baller'</a>
                    <a href="https://github.com/vpinball/vpinball/releases" target="_blank" class="text-gray-400 hover:text-white text-[10px]">VPX Latest</a>
                    <a href="https://github.com/vpinball/b2s-backglass/releases" target="_blank" class="text-gray-400 hover:text-white text-[10px]">B2S Server Latest</a>
                    <a href="https://github.com/freezy/dmd-extensions/releases" target="_blank" class="text-gray-400 hover:text-white text-[10px]">Freezy DMDEXT Latest</a>
                    <a href="https://github.com/vbousquet/flexdmd/releases/" target="_blank" class="text-gray-400 hover:text-white text-[10px]">FLEX DMD Latest</a>
                    <a href="https://configtool.vpuniverse.com/app/home" target="_blank" class="text-gray-400 hover:text-white text-[10px]">DOF Tool Config V3</a>
                    <a href="https://vpuniverse.com/files/file/14807-future-pinball-and-bam-essentials-all-in-one/" target="_blank" class="text-gray-400 hover:text-white text-[10px]">FP Latest</a>
                </div>
            </div>
        </div>
    </nav>"""

# Regex pattern to find the entire <nav>...</nav> block. 
# re.DOTALL allows the '.' to match newlines so it grabs the whole block.
nav_pattern = re.compile(r'<nav.*?</nav>', re.IGNORECASE | re.DOTALL)


def update_html_files():
    # Get all .html files in the current directory
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]

    if not html_files:
        print("No HTML files found in the current directory.")
        return

    for filename in html_files:
        print(f"Processing {filename}...")

        # Read the contents of the file
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()

        # Check if a nav tag exists
        if not nav_pattern.search(content):
            print(f"  - No <nav> tag found in {filename}. Skipping.")
            continue

        # Create a backup of the original file just in case
        backup_filename = f"{filename}.bak"
        shutil.copy2(filename, backup_filename)
        print(f"  - Backup created: {backup_filename}")

        # Replace the old nav block with the new one
        updated_content = nav_pattern.sub(NEW_NAV, content)

        # Write the updated content back to the file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(updated_content)

        print(f"  - Successfully updated navigation in {filename}!")


if __name__ == "__main__":
    update_html_files()
    print("\nAll done! Check your files to ensure the navigation looks correct.")