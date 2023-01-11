# Federico's Academic Website

Feel free to use this website generator. No need to ask for permission or to credit me on your site. If you do use it, I'd love to hear how it went :)

**NOTE**: while I do not ask that you credit me on your site, please respect the software license in LICENSE.md.

## Creating Your Website
1. Fill in the ```.json``` files in the ```data``` folder.
2. Run ```python3 build.py``` to build your website.
3. Open ```docs/index.html``` to admire it!

**NOTE**: don't edit ```docs/index.html```, ```docs/news.html```, ```docs/pubs.html```, or ```docs/main.css``` directly. If you want to make structural changes to your  website and you know what you are doing, then edit the build script ```build.py``` or the template files in ```templates/```. 

**NOTE**: after making changes to the ```.json``` files in ```/data```, the template files in ```templates/```, or the build script ```build.py``` remember to run ```python3 build.py``` again for your changes to take effect!

## Hosting Your Website With GitHub Pages
1. In your repo, go to ```settings -> pages``` and set ```source``` to ```/docs```.

**NOTE**: remember to remove or replace ```docs/CNAME```.