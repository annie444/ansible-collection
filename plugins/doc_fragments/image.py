class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
      src:
        type: str
        required: true
        aliases:
        - image_src
        description: The source URL of the image.
      format:
        type: str
        choices:
        - png
        - jpg
        - gif
        - svg
        - webp
        - auto
        default: auto
        required: false
        description: The format of the image. Defaults to auto.
    """
