# systemofadown
Check Toxicity for users/threads on reddit

Example: `python3 toxic.py -un spez 200`

Will parse spez's latest 200 comments and return an average toxicity rating. 

These are my (/u/CalicoCatalyst) current guesses at toxicity ratings:

15 = somewhat toxic

25 = pretty toxic

```
usage: toxic.py [-h] [-d] [-un] [-th] link limit

Bot To Add Titles To Images

positional arguments:
  link             username or thread to check comments of
  limit            Limit of comments to parse

optional arguments:
  -h, --help       show this help message and exit
  -d, --debug      Enable Debug Logging
  -un, --username  Declare a username parse
  -th, --thread    Declare a Link parse
  ```
