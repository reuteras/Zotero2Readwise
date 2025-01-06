"""Files for copying data from Zotero to Readwise."""
from zotero2readwise.readwise import Readwise
from zotero2readwise.zotero import ZoteroAnnotationsNotes, get_zotero_client


class Zotero2Readwise:
    """Zotero2Readwise class."""
    def __init__( # noqa PLR0913
        self,
        readwise_token: str,
        zotero_key: str,
        zotero_library_id: str,
        zotero_library_type: str = "user",
        include_annotations: bool = True,
        include_notes: bool = False,
        filter_colors: list[str] | None = None,
        since: int = 0,
    ):
        """Init function."""
        self.readwise = Readwise(readwise_token)
        self.zotero_client = get_zotero_client(
            library_id=zotero_library_id,
            library_type=zotero_library_type,
            api_key=zotero_key,
        )
        self.zotero = ZoteroAnnotationsNotes(self.zotero_client, filter_colors)
        self.include_annots = include_annotations
        self.include_notes = include_notes
        self.since = since

    def get_all_zotero_items(self) -> list[dict]:
        """Retrieves all Zotero items of the specified types (notes and/or annotations) that were modified since the specified date.

        Returns:
        A list of dictionaries representing the retrieved Zotero items.
        """
        items = []
        if self.include_annots:
            items.extend(self.retrieve_all("annotation", self.since))

        if self.include_notes:
            items.extend(self.retrieve_all("note", self.since))

        print(f"{len(items)} Zotero items are retrieved.")

        return items

    def run(self, zot_annots_notes: list[dict] | None = None) -> None:
        """Function to handle the process of getting data from Zotero to Readwise."""
        if zot_annots_notes is None:
            zot_annots_notes = self.get_all_zotero_items()

        if zot_annots_notes:
            formatted_items = self.zotero.format_items(zot_annots_notes)
        else:
            print("No items to format.")
            formatted_items = []

        if self.zotero.failed_items:
            self.zotero.save_failed_items_to_json("failed_zotero_items.json")

        if formatted_items:
            self.readwise.post_zotero_annotations_to_readwise(formatted_items)
        else:
            print("No new items.")

    def retrieve_all(self, item_type: str, since: int = 0):
        """Retrieves all items of a given type from Zotero Database since a given timestamp.

        Args:
            item_type (str): Either "annotation" or "note".
            since (int): Timestamp in seconds since the Unix epoch. Defaults to 0.

        Returns:
            List[Dict]: List of dictionaries containing the retrieved items.
        """
        if item_type not in ["annotation", "note"]:
            raise ValueError("item_type must be either 'annotation' or 'note'")

        if since == 0:
            print(f"Retrieving ALL {item_type}s from Zotero Database")
        else:
            print(f"Retrieving {item_type}s since last run from Zotero Database")

        print("It may take some time...")
        query = self.zotero_client.items(itemType=item_type, since=since)
        return self.zotero_client.everything(query)
