# ColinBot

**ColinBot** is a multifunctional Discord bot with a variety of features including an AI chatbot, economy, gambling, music playback, and more!

## Chatbot

**ColinBot** uses OpenAI API for its chatbot functionality. In order to use this feature you must provide an API key in the `.env` file under `OPENAI_API_KEY`. You will need credits in your OpenAI account for this to work. Once you have this configured simply @ColinBot in the Discord server to start a conversation with them.

## Economy

**ColinBot** uses MongoDB to store user economy data. You will need to provide a MongoDB URI and DB in the `.env` file under `MONGODB_URI` and `MONGODB_DB` name. This is available for free from the MongoDB website. Users can get a free 100 Colin Coins per day using `!daily`, check their balance with `!coins`, and send another user coins with `!send`. There is also a leaderboard `!leaderboard`.

## Gambling

Users can gamble their Colin Coins in a variety of games including `!slots` `!blackjack` and `!baccarat`

## Music

This feature is currently unavailable.

## Miscellaneous

**ColinBot** was originally a bot that would post a random picture of my friend Colin. This feature is still here `(!Colin)`; however, you will need to provide your own S3 bucket to use it. `!help` provides a comprehensive list of all available commands.