A simple file manager, note organizer and text editor, featuring live [markdown](https://daringfireball.net/projects/markdown) preview


## Key features:
- Tab management
- Customization and theming 
- Image preview
- Find and Replace text


Major Markdown features that are currently not supported:
- Blockquotes
- Code blocks
- Tables
- Task lists


## Build with [Nuitka](https://github.com/Nuitka/Nuitka)
```
nuitka --standalone --disable-console --windows-icon-from-ico=resource/logo.ico --plugin-enable=pyqt6 --include-data-dir=resource=resource --include-data-dir=widget=widget --output-dir=build --output-filename=qnotes main.py
```

## Preview
<img src="preview.jpg" width="750">
