# Plex Poster Export
## Export your plex posters, and episode title cards to file
---
### Requirements:
- Python
- plexapi (`pip install plexapi`)
---

### Setup:
This script is written for Windows, to run on Linux a few changes are required, specifically `\\` needing to be altered to `/`      
If you don't provide your Plex URL and Plex token on line 2/3, the script will prompt you for them.   
On running the script, it will prompt you which libraries you want to run the script on.     
Enter numbers, separated by commas, & those libraries will be processed, in that order, sequentially. e.g. `4,2,8,9`     
It will then prompt for Posters, Backgrounds, Banners, Themes, Episode Art, & if you want to download all or just custom art.   
 - Note: These do not currently work
 
You will be given an option to create a Hardlink of the `poster.png` file with the Show/Movie Folder name. This is a Hardlink so it will not take up extra space, it will be names as follows
> M:\Movies\Totally Awesome Movie (1989)\Totally Awesome Movie (1989)  {edition-Director's Cut}.mp4
> 
> M:\Movies\Totally Awesome Movie (1989)\poster.png
> 
> M:\Movies\Totally Awesome Movie (1989)\Totally Awesome Movie (1989).png <HARDLINK of M:\Movies\Totally Awesome Movie (1989)\poster.png>

#### Movies
- The poster will be exported to the same directory as the media file with the name `poster.png`

#### TV Series
- The show poster will be exported to the parent directory of the show with the name `poster.png`
- The season covers will be exported to the parent directory of the show with the name `season##.png`
- The episode title cards will be exported next to each file with the name matching the video file.

At the end of the script, you can instantly run it again on another library by entering `y` (**NO LONGER** case sensitive)


I know it's not the most elegant code but it's functional :)

<sub><sup>This code has been edited with the help of ChatGPT</sup></sub>
