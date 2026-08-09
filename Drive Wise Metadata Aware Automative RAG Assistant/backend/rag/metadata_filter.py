class MetadataFilter:
    """
    Filters brochure chunks using vehicle metadata.
    """

    def __init__(self, metadata):
        self.metadata = metadata

    # ========================================================
    # NORMALIZE
    # ========================================================

    @staticmethod
    def normalize(value):
        """
        Convert metadata values into a consistent format.
        """

        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
        )

    # ========================================================
    # FILTER BY BRAND + MODEL
    # ========================================================

    def filter(
        self,
        brand,
        model
    ):
        """
        Return metadata indices belonging to
        the selected brand and model.
        """

        target_brand = self.normalize(
            brand
        )

        target_model = self.normalize(
            model
        )

        allowed_indices = []

        for index, item in enumerate(
            self.metadata
        ):

            item_brand = self.normalize(
                item.get(
                    "brand",
                    ""
                )
            )

            item_model = self.normalize(
                item.get(
                    "model",
                    ""
                )
            )

            if (
                item_brand == target_brand
                and item_model == target_model
            ):

                allowed_indices.append(
                    index
                )

        return allowed_indices

    # ========================================================
    # FILTER CHUNKS
    # ========================================================

    def filter_chunks(
        self,
        brand,
        model
    ):
        """
        Return the actual brochure chunks
        belonging to the selected vehicle.
        """

        indices = self.filter(
            brand=brand,
            model=model
        )

        return [
            self.metadata[index]
            for index in indices
        ]