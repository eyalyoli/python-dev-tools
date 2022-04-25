### Python developer tools
## req-auto-cleaner
A scripts that helps in cleaning out `pip freeze`'s dump in requirements files removing unneeded dependenices.

Using `pip freeze` to create the `requirements.txt` file is bad since it that it simply dumps all installed packages with strict versions, every dependency has its own dependencies and they are included in the dump. For example, if you have lib==1.0 installed, that needs sub-lib==0.5, if you use pip freeze you'll get both, but later when you wish to update the version of lib to 2.0, most likely you'll get conflicts since lib v2.0 now uses sub-lib v1.0 not v0.5 that you require... This gets complex fast for multiple dependencies.
