- Command `anime` can be used to search **anime** through Jikan API on MyAnimeList
- Now command `anime` will return 5 categories of embed,
  - Overview
  - Characters
  - Relations
  - News
  - Forum

- Command `manga` can be used to search **manga** through Jikan API on MyAnimeList
- Now command `manga` will return 5 categories of embed,
  - Overview
  - Characters
  - Relations
  - News
  - Topics

- Command `animeid` and `mangaid` are required to supply entry id based on MAL website after calling the command

- Command `random` returns random entry

- Options in config.json
  - (Default: True) Detection of url in messages to return related anime/manga

  - (Default: False) Set default search API to official API (MAL) to have better accuracy
    - Get the client id from registering in https://myanimelist.net/apiconfig