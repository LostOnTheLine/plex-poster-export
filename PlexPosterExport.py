# Set variables here, otherwise you will be asked them during script run
baseurl = ''
token = ''

######################################################################################################
#                                                                                                    #
# - Movie Libraries -> Download poster and place next to video as poster.png                         #
# - TV Libraries -> Download show poster, place in root folder for show as poster.png                #
#                -> Download season poster and save to root folder as season##.png                   #
#                -> Download episode title card, place next to episode named the same as episode     #
#                                                                                                    #
######################################################################################################

import os
import platform
import logging
from logging.handlers import RotatingFileHandler
from plexapi.server import PlexServer
from plexapi.utils import download
from plexapi import video
from plexapi.exceptions import NotFound

# Setup logging
log_file = 'plex_poster_extract.log'
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=1)  # 10MB log file
logger = logging.getLogger()
logger.addHandler(handler)

if baseurl == '' and token == '' :
    baseurl = input('What is your Plex URL:  ')
    token = input('What is your Plex Token:  ')

plex = PlexServer(baseurl, token)
skipped_items = []

def download_artwork(item, artwork_url, save_path):
    if artwork_url is None:
        logger.warning(f"{item} failed Artwork = None")
        return False
    try:
        download(baseurl + artwork_url, token, save_path, item)
    except NotFound:
        logger.error(f"Not Found: {item} {artwork_url}")
        return False
    return True

def create_hardlink(original_file, hardlink_file):
    try:
        if platform.system() == 'Windows':
            os.link(original_file, hardlink_file)
        else:
            os.symlink(original_file, hardlink_file)  # Use symbolic link for Unix-like systems
        logger.info(f"Created hardlink: {hardlink_file}")
    except Exception as e:
        logger.error(f"Failed to create hardlink for {hardlink_file}: {str(e)}")

def report_skipped_items():
    if skipped_items:
        print("\nSkipped items:")
        for item in skipped_items:
            print(f"  {item['title']} - {item['reason']}")
    else:
        print("No items were skipped.")

def process_movies(movies, create_hardlink_option):
    for video in movies:
        videoTitle = video.title
        videoPath = video.media[0].parts[0].file
        videoFolder = videoPath.rpartition('\\')[0] + "\\"
        videoPoster = video.thumb
        movie_filename = os.path.basename(videoPath)
        movie_filename_without_ext = movie_filename[:movie_filename.rindex('.')]

        print(f"Downloading poster for {videoTitle}")
        if not download_artwork(videoFolder, videoPoster, "poster.png"):
            skipped_items.append({"title": videoTitle, "reason": "Missing Poster"})
            logger.info(f"Skipped movie: {videoTitle} - Missing Poster")
        elif create_hardlink_option:
            hardlink_path = os.path.join(videoFolder, f"{movie_filename_without_ext}.png")
            create_hardlink(os.path.join(videoFolder, "poster.png"), hardlink_path)

def process_shows(shows, download_episode_artwork, download_all_artwork, create_hardlink_option):
    for video in shows:
        showTitle = video.title
        showFolder = video.locations[0] + "\\"
        showPoster = video.thumb

        print(f"Downloading images for {showTitle}")
        if not download_artwork(showFolder, showPoster, "poster.png"):
            skipped_items.append({"title": showTitle, "reason": "Missing Poster"})
            logger.info(f"Skipped show: {showTitle} - Missing Poster")
        elif create_hardlink_option:
            hardlink_path = os.path.join(showFolder, f"{showTitle}.png")
            create_hardlink(os.path.join(showFolder, "poster.png"), hardlink_path)

        for season in video.seasons():
            seasonTitle = season.title
            seasonThumb = season.thumb
            seasonFolder = showFolder
            seasonNumber = str(season.index).zfill(2)
            seasonPosterName = f"season{seasonNumber}.png"

            if not download_artwork(seasonFolder, seasonThumb, seasonPosterName):
                skipped_items.append({"title": f"{showTitle} - {seasonTitle}", "reason": "Missing Season Poster"})
                logger.info(f"Skipped season: {showTitle} - {seasonTitle} - Missing Season Poster")

        if download_episode_artwork:
            for episode in video.episodes():
                episodeTitle = episode.title
                episodePath = episode.locations[0].rpartition('\\')[0] + "\\"
                episodeFile = episode.locations[0][episode.locations[0].rindex("\\")+1:][:-4]
                episodeThumb = episode.thumb

                # Check for custom artwork if required
                if not download_all_artwork and not episodeThumb:
                    continue

                if not download_artwork(episodePath, episodeThumb, episodeFile + ".png"):
                    skipped_items.append({"title": f"{showTitle} - {episodeTitle}", "reason": "Missing Episode Artwork"})
                    logger.info(f"Skipped episode: {showTitle} - {episodeTitle} - Missing Episode Artwork")

def run_script():
    # list libraries for user to select which to export from
    sectionList = [x.title for x in plex.library.sections()]
    print("\nYour Libraries: ")
    for i, title in enumerate(sectionList):
        print(f"      {i} - {title}")

    selectedLibraries = input("Enter the numbers of the libraries to export posters from (e.g. 1,3,5): ").split(',')

    # Choose the type of artwork to download
    download_posters = input("Download posters? (y/n): ").lower() == 'y'
    download_backgrounds = input("Download backgrounds? (y/n): ").lower() == 'y'
    download_banners = input("Download banners? (y/n): ").lower() == 'y'
    download_themes = input("Download themes? (y/n): ").lower() == 'y'

    # Ask if we should download episode artwork and if it should be for all or only custom
    download_episode_artwork = input("Download episode artwork? (y/n): ").lower() == 'y'
    download_all_artwork = input("Download all artwork (including defaults)? (y/n): ").lower() == 'y'
    
    # Option to create hardlink
    create_hardlink_option = input("Create hardlinks with folder name? (y/n): ").lower() == 'y'

    for libraryIndex in selectedLibraries:
        selectedLibrary = int(libraryIndex)
        selectedLibraryType = plex.library.section(sectionList[selectedLibrary]).type
        selectedLibraryItems = plex.library.section(sectionList[selectedLibrary]).search()

        if selectedLibraryType == "movie":
            if download_posters:
                process_movies(selectedLibraryItems, create_hardlink_option)

        elif selectedLibraryType == "show":
            process_shows(selectedLibraryItems, download_episode_artwork, download_all_artwork, create_hardlink_option)

    report_skipped_items()

while True:
    run_script()
    runagain = input("Would you like to run on another library (y/n)? ").lower()
    if runagain != "y":
        break
