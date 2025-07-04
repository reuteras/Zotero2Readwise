"""Functions and classes regarding Zotero."""
import re
from dataclasses import dataclass, field
from json import dump
from os import environ

from pyzotero.zotero import Zotero
from pyzotero.zotero_errors import ParamNotPassedError, UnsupportedParamsError

from zotero2readwise import FAILED_ITEMS_DIR


@dataclass
class ZoteroItem:
    """Zotero item class."""
    key: str
    version: int
    item_type: str
    text: str
    annotated_at: str
    annotation_url: str
    comment: str | None = None
    title: str | None = None
    tags: list[str] | None = field(init=True, default=None)
    document_tags: list[dict] | None = field(init=True, default=None)
    document_type: int | None = None
    annotation_type: str | None = None
    creators: str | None = field(init=True, default=None)
    source_url: str | None = None
    attachment_url: str | None = None
    page_label: str | None = None
    color: str | None = None
    relations: dict | None = field(init=True, default=None)

    def __post_init__(self):
        """Post init function to clean up items."""
        # Convert [{'tag': 'abc'}, {'tag': 'def'}] -->  ['abc', 'def']
        if self.tags:
            self.tags = [d_["tag"] for d_ in self.tags]

        if self.document_tags:
            self.document_tags = [d_["tag"] for d_ in self.document_tags]

        # Sample {'dc:relation': ['http://zotero.org/users/123/items/ABC', 'http://zotero.org/users/123/items/DEF']}
        if self.relations:
            self.relations = self.relations.get("dc:relation")

        if self.creators:
            et_al = " et al."
            max_length = 1024 - len(et_al)
            if len(self.creators) > max_length:
                # Reset creators_str and find the first n creators that fit in max_length
                while len(self.creators) < max_length:
                    match = re.search(r"(.*),[^,]+$", self.creators)[1]
                    self.creators = match
                self.creators += et_al

    def get_nonempty_params(self) -> dict:
        """Get nonempty parameters."""
        return {k: v for k, v in self.__dict__.items() if v}


def get_zotero_client(
    library_id: str | None = None, api_key: str | None = None, library_type: str = "user"
) -> Zotero:
    """Create a Zotero client object from Pyzotero library.

    Zotero userID and Key are available

    Parameters
    ----------
    library_id: str
        If not passed, then it looks for `ZOTERO_LIBRARY_ID` in the environment variables.
    api_key: str
        If not passed, then it looks for `ZOTERO_KEY` in the environment variables.
    library_type: str ['user', 'group']
        'user': to access your Zotero library
        'group': to access a shared group library

    Returns:
    -------
    Zotero
        a Zotero client object
    """
    if library_id is None:
        try:
            library_id = environ["ZOTERO_LIBRARY_ID"]
        except KeyError as err:
            raise ParamNotPassedError(
                "No value for library_id is found. "
                "You can set it as an environment variable `ZOTERO_LIBRARY_ID` or use `library_id` to set it."
            ) from err

    if api_key is None:
        try:
            api_key = environ["ZOTERO_KEY"]
        except KeyError as err:
            raise ParamNotPassedError(
                "No value for api_key is found. "
                "You can set it as an environment variable `ZOTERO_KEY` or use `api_key` to set it."
            ) from err

    if library_type is None:
        library_type = environ.get("LIBRARY_TYPE", "user")
    elif library_type not in ["user", "group"]:
        raise UnsupportedParamsError("library_type value can either be 'user' or 'group'.")

    return Zotero(
        library_id=library_id,
        library_type=library_type,
        api_key=api_key,
    )


class ZoteroAnnotationsNotes:
    """Class for Zotero Annotations notes."""
    def __init__(self, zotero_client: Zotero, filter_colors: list[str]):
        """Init function."""
        self.zot = zotero_client
        self.failed_items: list[dict] = []
        self._cache: dict = {}
        self._parent_mapping: dict = {}
        self.filter_colors: list[str] = filter_colors

    def get_item_metadata(self, annot: dict) -> dict:
        """Get metadata for item."""
        data = annot["data"]
        # A Zotero annotation or note must have a parent with parentItem key.
        parent_item_key = data["parentItem"]

        if parent_item_key in self._parent_mapping:
            top_item_key = self._parent_mapping[parent_item_key]
            if top_item_key in self._cache:
                return self._cache[top_item_key]
        else:
            parent_item = self.zot.item(parent_item_key)
            top_item_key = parent_item["data"].get("parentItem", None)
            self._parent_mapping[parent_item_key] = (
                top_item_key if top_item_key else parent_item_key
            )

        if top_item_key:
            top_item = self.zot.item(top_item_key)
            data = top_item["data"]
        else:
            top_item = parent_item
            data = top_item["data"]
            top_item_key = data["key"]

        metadata = {
            "title": data["title"],
            "tags": data["tags"],
            "document_type": data["itemType"],
            "source_url": top_item["links"]["alternate"]["href"],
            "creators": "",
            "attachment_url": "",
        }
        if "creators" in data:
            for creator in data["creators"]:
                if metadata["creators"] != "":
                    metadata["creators"] += ", "
                try:
                    metadata["creators"] += (
                        creator["firstName"] + " " + creator["lastName"]
                    )
                except Exception:
                    metadata["creators"] += creator["name"]
        if (
            "attachment" in top_item["links"]
            and top_item["links"]["attachment"]["attachmentType"] == "application/pdf"
        ):
            metadata["attachment_url"] = top_item["links"]["attachment"]["href"]

        self._cache[top_item_key] = metadata
        return metadata

    def format_item(self, annot: dict) -> ZoteroItem:
        """Format Zotero item."""
        data = annot["data"]
        item_type = data["itemType"]
        annotation_type = data.get("annotationType")
        metadata = self.get_item_metadata(annot)

        text = ""
        comment = ""
        if item_type == "annotation":
            if annotation_type == "highlight":
                text = data["annotationText"]
                comment = data["annotationComment"]
            elif annotation_type == "note":
                text = data["annotationComment"]
                comment = ""
            elif annotation_type == "image":
                print("Image annotations are not currently supported.")
                raise NotImplementedError(
                    "Image  annotations are not currently supported."
                )
            else:
                print(
                    f"Annotations of type {annotation_type} are not currently supported."
                )
                raise NotImplementedError(
                    f"Annotations of type {annotation_type} are not currently supported."
                )
        elif item_type == "note":
            text = data["note"]
            comment = ""
        else:
            raise NotImplementedError(
                "Only Zotero item types of 'note' and 'annotation' are supported."
            )

        if text == "":
            raise ValueError("No annotation or note data is found.")
        return ZoteroItem(
            key=data["key"],
            version=data["version"],
            item_type=item_type,
            text=text,
            annotated_at=data["dateModified"],
            annotation_url=annot["links"]["alternate"]["href"],
            attachment_url=metadata["attachment_url"],
            comment=comment,
            title=metadata["title"],
            tags=data["tags"],
            document_tags=metadata["tags"],
            document_type=metadata["document_type"],
            annotation_type=annotation_type,
            creators=metadata.get("creators"),
            source_url=metadata["source_url"],
            page_label=data.get("annotationPageLabel"),
            color=data.get("annotationColor"),
            relations=data["relations"],
        )

    def format_items(self, annots: list[dict]) -> list[ZoteroItem]:
        """Format all Zotero items."""
        formatted_annots = []
        print(
            f"ZOTERO: Start formatting {len(annots)} annotations/notes...\n"
            f"It may take some time depending on the number of annotations...\n"
            f"A complete message will show up once it's done!\n"
        )
        for annot in annots:
            try:
                if (
                    len(self.filter_colors) == 0
                    or annot["data"]["annotationColor"] in self.filter_colors
                ):
                    formatted_annots.append(self.format_item(annot))
            except Exception:
                self.failed_items.append(annot)
                continue

        finished_msg = "\nZOTERO: Formatting Zotero Items is completed!!\n\n"
        if self.failed_items:
            finished_msg += (
                f"\nNOTE: {len(self.failed_items)} Zotero annotations/notes (out of {len(annots)}) failed to format.\n"
                f"You can run `save_failed_items_to_json()` class method to save those items."
            )
        print(finished_msg)
        return formatted_annots

    def save_failed_items_to_json(self, json_filepath_failed_items: str | None = None):
        """Save failed items to json."""
        FAILED_ITEMS_DIR.mkdir(parents=True, exist_ok=True)
        if json_filepath_failed_items:
            out_filepath = FAILED_ITEMS_DIR.joinpath(json_filepath_failed_items)
        else:
            out_filepath = FAILED_ITEMS_DIR.joinpath("failed_zotero_items.json")

        with open(out_filepath, "w", encoding="utf-8") as f:
            dump(self.failed_items, f, indent=4)
        print(f"\nZOTERO: Detail of failed items are saved into {out_filepath}\n")
