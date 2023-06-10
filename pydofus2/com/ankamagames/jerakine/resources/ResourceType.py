class ResourceType:
    RESOURCE_BINARY = 1
    RESOURCE_BITMAP = 2
    RESOURCE_DX = 3
    RESOURCE_SWF = 4
    RESOURCE_SWL = 5
    RESOURCE_XML = 6
    RESOURCE_ZIP = 7
    RESOURCE_TXT = 8
    RESOURCE_ASWF = 9
    RESOURCE_MP3 = 16
    RESOURCE_SIGNED_FILE = 17
    RESOURCE_JSON = 18
    RESOURCE_NONE = 255

    @staticmethod
    def getName(type: int) -> str:
        if type == ResourceType.RESOURCE_BINARY:
            return "binary"
        elif type == ResourceType.RESOURCE_BITMAP:
            return "bitmap"
        elif type == ResourceType.RESOURCE_DX:
            return "dx"
        elif type == ResourceType.RESOURCE_SWF:
            return "swf"
        elif type == ResourceType.RESOURCE_SWL:
            return "swl"
        elif type == ResourceType.RESOURCE_XML:
            return "xml"
        elif type == ResourceType.RESOURCE_MP3:
            return "mp3"
        elif type == ResourceType.RESOURCE_SIGNED_FILE:
            return "signedFile"
        elif type == ResourceType.RESOURCE_NONE:
            return "none"
        else:
            return "unknown"
