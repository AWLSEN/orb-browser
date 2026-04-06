# orb-browser demo recording
# Run with: vhs demo.tape

Output demo.gif
Output demo.mp4

Set FontSize 18
Set Width 1200
Set Height 600
Set Theme "Catppuccin Mocha"
Set Padding 20

Type "pip install orb-browser"
Enter
Sleep 3s

Type "orb-browser setup"
Enter
Sleep 1s
# Orb API key
Type "orb_xhi1LOyzFE5gmkA54MnIhYT7xWzY3rHQv2rd0IwM4Dc"
Enter
Sleep 500ms
# LLM key
Type "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"
Enter
Sleep 500ms
# Provider
Enter
Sleep 500ms
# Base URL
Enter
Sleep 2s

Type "orb-browser deploy"
Enter
Sleep 90s

Type@100ms 'orb-browser task "go to news.ycombinator.com and tell me the top 3 stories"'
Enter
Sleep 15s

Type "orb-browser sleep"
Enter
Sleep 3s

Type "# 💤 Browser frozen to disk. $0/hr."
Enter
Sleep 3s

Type "# ...3 days later..."
Enter
Sleep 3s

Type "orb-browser wake"
Enter
Sleep 5s

Type "orb-browser url"
Enter
Sleep 3s

Type "# Still on HN. Still logged in. 500ms wake."
Enter
Sleep 5s
