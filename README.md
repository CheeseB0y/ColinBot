# ColinBot

**ColinBot** is a Discord bot with a variety of features including an AI chatbot, economy, gambling, and more!

## Table of contents
- [Features](#features)
  - [Chatbot](#chatbot)
  - [Economy](#economy)
  - [Gambling](#gambling)
  - [Other Features](#other)
- [Setup](#setup)
  - [Source](#source)
  - [Docker](#docker)
- [License](#license)

## Features

### Chatbot

To chat with **ColinBot** you can simply mention them like so `@colinbot` and then provide a message. **ColinBot** will respond after a short time. You can also use `!tts` with message text and **ColinBot** will respond with tts for users who have that enabled in Discord settings. Finally, **ColinBot** has a `!thoughts` command where the user can specify a number (maximum 25) of messages in the Discord chat history to look at and give their thoughts.

### Economy

**ColinBot** has a full economy function. Users can run `!daily` for their daily Colin Coin allowence. There is a `!leaderboard` where users can see how many Colin Coins they have in comparison to the rest of the Discord server. Users are also able to `!send` coins to each other as a transaction. The main purpose of the economy however is for the [Gambling](#gambling).

### Gambling

Users can gamble their Colin Coins in a variety of games including `!slots` `!blackjack` and `!baccarat`. More betting games are planned for the future.

### Other

**ColinBot** was originally a bot that would post a random picture of my friend Colin. This feature is still here `!Colin`; however, you will need to provide your own S3 bucket and images to use it. `!help` provides a comprehensive list of all available commands.

## Setup

**Colinbot** can be configured in two different ways, either run directly from source or via a docker container. The docker container is the preferred method but there is no disadvantage to downloading and running the source files. **ColinBot** has a few environment variables necessary for it's functionality but only the Discord token is requiered to get up and running. I will not be explaining how to get a discord token in depth at this time just make a discord developer account and get a bot from there. To access all the functionality of **ColinBot** you will need to set up an S3 buckit on AWS. OpenAI API access, and MongoDB. I will not be explaing how to do this at this time, if you know you know and if you don't there are plenty of tutorials online.

### Source

Running **ColinBot** from source should be very straighforward if you are familiar with python. First create a directory for **ColinBot**, it doesn't matter where. Then download the files with git using `git clone https://github.com/CheeseB0y/ColinBot.git` or download the source code from the latest release and unpack in your **ColinBot** directory. From here you will either need to create a virtual environment using venv or you will need python 1.13 installed. If you have python installed already, you can just run `pip install -r requierments.txt` to install the necessary dependancies. If you are using a virtual environment first run `python -m venv venv` to create the virtual environment and then `source venv/bin/activate` to use it in your terminal. Then you can run `pip install -r requierments.txt` and proceed as normal. Once you have all requierments installed, you must fill out the `template.env` file with all your environment variables. When you are done with that rename the file to `.env`. After all the dependancies are installed and your environment variables are set up, you can simply run `python bot.py` to start the bot.

### Docker

I will not be explaining how to set up Docker here, I will continue under the assumption that you already have Docker installed. **ColinBot** is avalible on Docker Hub at https://hub.docker.com/repository/docker/cheeseb0y/colinbot/. To download the **ColinBot** Docker container run `docker pull cheeseb0y/colinbot:latest`. After it is done pulling the Docker image you must set up your environment variables. Fill out the necessary variables using the `template.env` file and rename it to `.env` when you're done. Then when you're ready to start the **ColinBot** docker image run `docker run --env-file .env cheeseb0y/colinbot:latest`.

## License

This project is licensed under the GNU General Public License v3.0 - for more info see [LICENSE](LICENSE).
