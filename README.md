# twitterBot-ImagePoster
This is a simple twitter bot written in python that posts an image every full hour and in case of an error can send a message to your phone via a telegram bot.

### Configuration
Please create a `config.py` file that contains a `CONFIG` dictionary with the same keys as the `sample.config.py`.

### Basic Idea
Every hour the bot will chose a random image from an input folder, move it to the output folder and post it to twitter.
