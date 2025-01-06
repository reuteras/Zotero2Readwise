# Zotero ➡️ Readwise

> [!NOTE]
> This a fork of the original [Zotero2Readwise](https://github.com/e-alizadeh/Zotero2Readwise) by [e-alizadeh](https://github.com/e-alizadeh). I had some problems with the current version 0.4.5 and decided to fork the project and thereby also learn more about Zotero and Readwise.

`zotero2readwise` is a Python library that retrieves all [Zotero](https://www.zotero.org/) annotations and notes and then uploads them to your [Readwise](https://readwise.io/) account (Readwise is a paid service).

This is particularly useful for the new [Zotero PDF Reader](https://www.zotero.org/support/pdf_reader_preview) that stores all highlights in the Zotero database.

If you annotate your files outside the new Zotero PDF reader, this library may not work with your PDF annotations as those are not retrievable from the Zotero API.

This library is for you if you annotate (highlight + note) using the Zotero's PDF reader (including the one in Zotero for iOS)

Updating an existing Zotero annotation or note and re-running this library will update the corresponding Readwise highlight without creating a duplicate.

## Installation
You can install the library by running
```shell
pip install zotero2readwise
```

Note: If you do not have pip installed on your system, you can follow the instructions [here](https://pip.pypa.io/en/stable/installation/).


## Usage
Since we have to retrieve the notes from Zotero API and then upload them to the Readwise, the minimum requirements are:
* **Readwise access token** [Required]: You can get your access token from [https://readwise.io/access_token](https://readwise.io/access_token)
* **Zotero API key** [Required]: Create a new Zotero Key from [your Zotero settings](https://www.zotero.org/settings/keys/new)
* **Zotero personal or group ID** [Required]:
  * Your **personal library ID** (aka **userID**) can be found [here](https://www.zotero.org/settings/keys) next to `Your userID for use in API calls is XXXXXX`.
  * If you're using a **group library**, you can find the library ID by
    1. Go to `https://www.zotero.org/groups/`
    2. Click on the interested group.
    3. You can find the library ID from the URL link that has format like _[https://www.zotero.org/groups/](https://www.zotero.org/groups/)<group_id>/group_name_. The number between `/groups/` and `/group_name` is the libarry ID.
* **Zotero library type** [Optional]: _"user"_ (default) if using personal library and _"group"_ if using group library.

Note that if you want to retrieve annotations and notes from a group, you should provide the group ID (`zotero_library_id=<group_id>`) and set the library type to group (`zotero_library_type="group"`).

### Approach 1 (running a python script)
For this approach you can download `run.py` script (from [here](https://github.com/e-alizadeh/Zotero2Readwise/blob/master/zotero2readwise/run.py)). Run `python run.py -h` to get more information about all options.
You can simply run the script as the following:
```shell
python run.py <readwise_token> <zotero_key> <zotero_id>
```

### Approach 2 (through python terminal)
```python
from zotero2readwise.zt2rw import Zotero2Readwise

zt_rw = Zotero2Readwise(
    readwise_token="your_readwise_access_token",  # Visit https://readwise.io/access_token)
    zotero_key="your_zotero_key",  # Visit https://www.zotero.org/settings/keys
    zotero_library_id="your_zotero_id", # Visit https://www.zotero.org/settings/keys
    zotero_library_type="user", # "user" (default) or "group"
    include_annotations=True, # Include Zotero annotations -> Default: True
    include_notes=False, # Include Zotero notes -> Default: False
)
zt_rw.run()
```
Just to make sure that all files are created, you can run `save_failed_items_to_json()` from `readwise` attribute of
the class object to save any highlight that failed to upload to Readwise.
If a file or more failed to create, the filename (item title) and the corresponding Zotero
item key will be saved to a txt file.
```python
zt_rw.readwise.save_failed_items_to_json("failed_readwise_highlights.json")
```
---
## [Zotero2Readwise-Sync](https://github.com/e-alizadeh/Zotero2Readwise-Sync)

### 👉 Set up a scheduled automation once and forget about it

You can fork my repository [Zotero2Readwise-Sync](https://github.com/e-alizadeh/Zotero2Readwise-Sync) repository that contain
the cronjob (time-based Job scheduler) using GitHub Actions to automatically retrieve all your Zotero annotations/notes,
and then push them to Readwise.
You can use the forked repository without even changing a single line (of course if you're happy with the default settings!)

## Request a new feature or report a bug
Feel free to request a new feature or report a bug in GitHub issue [here](https://github.com/e-alizadeh/Zotero2Readwise/issues).


## 📫 How to reach me
<a href="https://ealizadeh.com" target="_blank"><img alt="Personal Website" src="https://img.shields.io/badge/Personal%20Website-%2312100E.svg?&style=for-the-badge&logoColor=white" /></a>
<a href="https://www.linkedin.com/in/alizadehesmaeil/" target="_blank"><img alt="LinkedIn" src="https://img.shields.io/badge/linkedin-%230077B5.svg?&style=for-the-badge&logo=linkedin&logoColor=white" /></a>
<a href="https://medium.ealizadeh.com/" target="_blank"><img alt="Medium" src="https://img.shields.io/badge/medium-%2312100E.svg?&style=for-the-badge&logo=medium&logoColor=white" /></a>
<a href="https://twitter.com/intent/follow?screen_name=es_alizadeh&tw_p=followbutton" target="_blank"><img alt="Twitter" src="https://img.shields.io/badge/twitter-%231DA1F2.svg?&style=for-the-badge&logo=twitter&logoColor=white" /></a>

<a href="https://www.buymeacoffee.com/ealizadeh" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
