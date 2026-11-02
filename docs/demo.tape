# Records docs/images/demo.gif's raw footage with VHS (https://github.com/charmbracelet/vhs).
# Setup: clone this repo to /tmp/qk-skills and create an empty /tmp/qk-demo. Then: vhs docs/demo.tape
# The GIF in the README is this recording cut after Claude's last line, sped up 1.5x,
# with the finished diagram appended as the final frame.
Output "demo-raw.mp4"

Set Shell "bash"
Set FontSize 15
Set Width 1280
Set Height 760
Set Padding 18
Set Theme "GitHub Dark"
Set TypingSpeed 35ms
Set Framerate 24

Hide
Type "cd /tmp/qk-demo && clear && claude --plugin-dir /tmp/qk-skills --permission-mode default --allowedTools Bash Read Write Edit Glob Grep"
Enter
Sleep 7s
# First launch in a new folder asks whether to trust it; the default is "No, exit".
Down
Enter
Sleep 6s
Show

Sleep 1s
Type "/qk-skills:diagram flowchart of how a pull request gets merged: open PR, CI runs, review, a changes-requested loop back to the author, merge. Keep it under 8 nodes. Finish with one line: Saved <relative png paths>"
Sleep 1s
Enter

Sleep 90s
