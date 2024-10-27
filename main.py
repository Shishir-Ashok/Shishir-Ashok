import os
import html
import base64
import textwrap
from github import Github
from datetime import datetime

class GitHubStats:
    def __init__(self, token):
        self.g = Github(token)
        self.user = self.g.get_user()
        
    def get_stats(self):
        # Collect GitHub statistics
        repos = list(self.user.get_repos())
        commits = sum(repo.get_commits().totalCount for repo in repos if not repo.fork)
        stars = sum(repo.stargazers_count for repo in repos)
        
        # Calculate total lines of code
        additions = 0
        deletions = 0
        for repo in repos:
            if not repo.fork:
                try:
                    stats = repo.get_stats_contributors()
                    if stats:
                        for stat in stats:
                            if stat.author.login == self.user.login:
                                additions += sum(week.additions for week in stat.weeks)
                                deletions += sum(week.deletions for week in stat.weeks)
                except:
                    continue
        
        return {
            'repos': len(repos),
            'commits': commits,
            'stars': stars,
            'followers': self.user.followers,
            'additions': additions,
            'deletions': deletions,
            'languages': self.get_languages()
        }
    
    def get_languages(self):
        languages = {}
        for repo in self.user.get_repos():
            if not repo.fork:
                repo_langs = repo.get_languages()
                for lang, count in repo_langs.items():
                    languages[lang] = languages.get(lang, 0) + count
        return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5])

def ascii_art_to_svg_text(ascii_art, x, y, color, font_size=14):
    """Convert ASCII art string to SVG text elements."""
    # Dedent the ASCII art to remove any common leading whitespace
    ascii_art = textwrap.dedent(ascii_art).strip()
    
    # Split into lines and escape HTML special characters
    lines = [html.escape(line) for line in ascii_art.split('\n')]
    
    # Convert to SVG text elements
    text_elements = []
    for i, line in enumerate(lines):
        # Preserve spaces by replacing them with their HTML entity
        line = line.replace(' ', '&#160;')
        y_pos = y + (i * font_size)
        text_elements.append(
            f'<text x="{x}" y="{y_pos}" '
            f'font-family="monospace" '
            f'font-size="{font_size}px" '
            f'fill="{color}">'
            f'{line}</text>'
        )
    
    return '\n'.join(text_elements)

def generate_svg(stats, theme='dark'):
    # Colors for different themes
    colors = {
        'dark': {
            'bg': '#0D1117',
            'text': '#C9D1D9',
            'accent': '#58A6FF',
            'secondary': '#8B949E'
        },
        'light': {
            'bg': '#FFFFFF',
            'text': '#24292F',
            'accent': '#0969DA',
            'secondary': '#57606A'
        }
    }
    c = colors[theme]
    
    # Your ASCII art goes here as a multi-line string
    ascii_art = '''                               
                                                 * **#*                         
                                          =++#+%%@#%*%#%***                     
                                     +*###*%@@%##%%@@%@#@###                    
                                 +#***@@%%#@%%%%@@@@@@@@@@%@%                   
                               *#+=*+#%@%%%%%%%%@@@@@@@@@@@@%%                  
                              ***##@@@@@@%%@@@@@@@@@@@@@@@@@##                  
                             *#%%##@@@@@@%%%%%@@%**#%@@%%@@@@%#                 
                             %%%%@@@@%%####***+=-----=+%@%@@@%*#                
                            #%%%@@@#*****+*++==-------==*@@%%%###               
                             %%@@%#++++++++====------====%%#%####               
                            *%@%%#*===++++====---------==+%%%%##                
                             %@%%#+======-=======--:----==+%%#*                 
                             #%%#====-=+*#*++====+*#%%#*#-=#%+-                 
                             %%%+==+####%##%%#*#*%%@%#*++*%@*=*+                
                          +****%+*@**%%%%%%%%@%%@%#%#@@+%*=@+=-+                
                          +#***#*=**#*####%%%@+-+#*%%##*++=++*-=                
                           %*#***=+*=+##*+**%*=---*+=====+*-:=--                
                           +#%##*===+****+*#*+-=---#*++++---=--                 
                            +=+*+++==++++***+=====++#*+===-===                  
                              +**+++++**######***#=++%#*++==                    
                                  ++***%%%%########%@%%*++=                     
                                  +*****%@%*+=--::-+==*+++                      
                                   *****##*#**==-=====+++*                      
                                    *****#********+====++                       
                                    ***##**+++++=---=+++=                       
                                     **#%#***+=++++++#+==                       
                                  =+=+**##%%%%###%%%*=====                      
                              ---*+==+++**#######**+=======----                 
                           --=#****+=++***#******++======++-===------           
                      :--*##*#%#**@++++**********++======+----=---=++++-=       
                  =--+*####*#*#***#%************++====++*+=-=------====+--=-    
               --====-=*#%*%#*#****%#######*****++++==+*===-==---=====+*+===--- 
            --=====++#+++*******#*##**+**####****+++++=++=+====---====++*==++---
          -==--=+=*==++++++*******###%#===++*******+**+++==++==-=-====++*+=+++-=
       =======*=======++*+++***####*##%%###*+++****+++*====+++=-======++**=+++=+
      +++=++========+++++++++++**#####*%%####***++++=*=====+++==-=====++**++++++
    =**++=+=======+++++++***+++++**####**##***##+=====+===+=+++=======+++*++++++
   +**#**#**=======+++++++***++====++++++++++++=====+====+++++++======++***+++++
   ++*##%%%##*+======+++++*###*++=========+++++++====+==+=+++++++====++++*#+++=+
   *++**##%%%%#*+======+++++**##*++==========++++====+=++++++++++==++++++*#*++=+
  +**++++*##%%%%*+=======+++***#**+++============++++++++++++++++++++++++***++=+
  *****+=+*#%%%@%*+++=======++**###*+++==========++++=++*+++++++++++++++**#*++=@
 =******+++*#%%%@@*++========+++*###*+*+=========+++++++**++++++++++++++**#*+++#
 ***********####%@@*++========+++**#****+++======+++=+****+++++++++++++***#*+++*
+**#####*#**###%%%@**++========+++*##***+++++++++++=++****++**++++++++******++*=
***#######***##%%%@%##+++=======+++****++++++++++++=+**********++++++++******+**
    '''
    
    # Create the SVG template
    svg = f'''
    <svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{c['bg']}" />
        
        <!-- ASCII Art Section -->
        <g>
            {ascii_art_to_svg_text(ascii_art, 50, 50, c['text'], 14)}
        </g>
        
        <!-- User Info Section -->
        <g>
            {ascii_art_to_svg_text(user_info, 50, 400, c['text'], 14)}
        </g>
        
        <!-- Stats Section -->
        <g transform="translate(450, 50)">
            <text font-family="monospace" font-size="14" fill="{c['text']}">
                <tspan x="0" dy="20">GitHub Stats:</tspan>
                <tspan x="0" dy="20">——————</tspan>
                <tspan x="0" dy="20">Repos: {stats['repos']} {{Contributed: {stats.get('contributed', 0)}}}</tspan>
                <tspan x="0" dy="20">Commits: {stats['commits']:,}</tspan>
                <tspan x="0" dy="20">Stars: {stats['stars']}</tspan>
                <tspan x="0" dy="20">Followers: {stats['followers']}</tspan>
                <tspan x="0" dy="20">Lines: {stats['additions'] + stats['deletions']:,}</tspan>
                <tspan x="0" dy="20">({stats['additions']:,}++, {stats['deletions']:,}--)</tspan>
            </text>
        </g>
        
        <!-- Update Timestamp -->
        <text x="750" y="580" text-anchor="end" font-family="monospace" font-size="10" fill="{c['secondary']}">
            Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        </text>
    </svg>
    '''
    
    return svg

def update_profile():
    token = os.getenv('GITHUB_TOKEN')
    stats = GitHubStats(token).get_stats()
    
    # Generate both theme versions
    dark_svg = generate_svg(stats, 'dark')
    light_svg = generate_svg(stats, 'light')
    
    # Update the files in the repository
    g = Github(token)
    repo = g.get_repo(f"{g.get_user().login}/{g.get_user().login}")
    
    for theme, content in [('dark', dark_svg), ('light', light_svg)]:
        filename = f'profile-{theme}.svg'
        try:
            # Try to get existing file
            file = repo.get_contents(filename)
            repo.update_file(
                filename,
                f"Update {theme} theme profile card",
                content,
                file.sha
            )
        except:
            # Create new file if it doesn't exist
            repo.create_file(
                filename,
                f"Create {theme} theme profile card",
                content
            )


if __name__ == "__main__":
    update_profile()
