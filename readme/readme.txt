Plugin for CudaText.
Handles auto-completion command (Ctrl+Space) for HTML documents:
- inside plain text parts of HTML document, ie ouf of <...> brackets
- inside HTML comments (note: this needs CudaText 1.141.6+)

Plugin is bound to lexer names which contain "HTML" at beginning, ie it should
work for all "HTMLxxxx" lexers.

Plugin should not interfere with built-in HTML auto-completion, and not interfere
with plugin "Complete From Text" (which didn't work in HTML anyway).


Plugin has options in the config file, call menu item "Options / Settings-plugins / Complete HTML Text".
Options are: 

- 'min_len': minimal word length, words of smaller length will be ignored.
- 'max_lines': if document has bigger count of lines, ignore this document.    
- 'case_sens': case-sensitive; words starting with 'A' will be ignored when you typed 'a'.


Authors: 
- Alexey Torgashin (CudaText)
- halfbrained (https://github.com/halfbrained)
License: MIT
