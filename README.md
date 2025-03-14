# PIGEO'n'S - Program to Interactively Grade and Evaluate Objects and Scenes

![hello](imgs/hello.png)

Blender extenension to help with homework grading for course VV035 - 3D Modelling, taught at FI MUNI. Yes, we are proud of the name.

Developed by Dusan as part of semestral project, maintained by KiraaCorsac and other lectors of VV035.

Icons provided by the amazing Clair from @ccartstuff.

---

## Installation

Install from [FI MUNI Blender Extension Repository](https://muni.cz/go/pigeons-repo) (`https://muni.cz/go/pigeons-repo`). Add this as a new repository, refresh, search for an extension named PIGEO'n'S and install.  

## Use

This extension resides in the N-Panel of the 3D Viewport, in the PIGEO'n'S category. Each homework has a separate test battery. Select the appropriate battery and click "Run Tests".

![screenshot of pigeons](./docs_imgs/image.png)

Observe the pigeon to learn about the quality of your homework. 

Alternatively, if PIGEO'n'S can also be used in headless mode from the CLI like this:

```
python cli.py --hw homework5materials --homework-file C:\Users\KiraaCorsac\Downloads\Shelf.blend
```

For that, you need to set up an `.env` file. See later section for expected contetnts of the `.env` file

## Development

You are very welcomed to contribute to development of PIGEO'n'S. We can roll out changes very quickly, so if you help us fix a bug early in the semester, it's likely that students enrolled in the same semester get to see the fix :)

To submit a PR: 
- Describe what you are trying to solve
- Describe how your PR is making this software better 
- Make sure the extension builds
- Create descriptive commits
- Use black formatter (prefferably, use VS Code with `ms-python.black-formatter` extension)
- Observe the code style (fixes and enhancments welcomed)

For development, use [Blender Development VS Code extension](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development).

Set up a `.env` file that looks like this
```
BLENDER_PATH="C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"
```

Ensure correct development environment
```
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```

Build releases with
```
invoke build
invoke release
```
