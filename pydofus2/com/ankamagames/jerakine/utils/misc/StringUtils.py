import re


class StringUtils:
    accents: str = "ŠŒŽšœžÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜŸÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýÿþ"
    pattern = None

    def fill(str: str, len: int, char: str, before: bool = True) -> str:
        if not char or not len(char):
            return str
        while len(str) != len:
            if before:
                str = char + str
            else:
                str += char
        return str

    def initPatterns():
        StringUtils.pattern = {
            "Š": "S",
            "Œ": "Oe",
            "Ž": "Z",
            "š": "s",
            "œ": "oe",
            "ž": "z",
            "À": "A",
            "Á": "A",
            "Â": "A",
            "Ã": "A",
            "Ä": "A",
            "Å": "A",
            "Æ": "Ae",
            "Ç": "C",
            "È": "E",
            "É": "E",
            "Ê": "E",
            "Ë": "E",
            "Ì": "I",
            "Í": "I",
            "Î": "I",
            "Ï": "I",
            "Ð": "D",
            "Ñ": "N",
            "Ò": "O",
            "Ó": "O",
            "Ô": "O",
            "Õ": "O",
            "Ö": "O",
            "Ø": "O",
            "Ù": "U",
            "Ú": "U",
            "Û": "U",
            "Ü": "U",
            "Ÿ": "Y",
            "Ý": "Y",
            "Þ": "Th",
            "ß": "ss",
            "à": "a",
            "á": "a",
            "â": "a",
            "ã": "a",
            "ä": "a",
            "å": "a",
            "æ": "ae",
            "ç": "c",
            "è": "e",
            "é": "e",
            "ê": "e",
            "ë": "e",
            "ì": "i",
            "í": "i",
            "î": "i",
            "ï": "i",
            "ð": "d",
            "ñ": "n",
            "ò": "o",
            "ó": "o",
            "ô": "o",
            "õ": "o",
            "ö": "o",
            "ø": "o",
            "ù": "u",
            "ú": "u",
            "û": "u",
            "ü": "u",
            "ý": "y",
            "ÿ": "y",
            "þ": "th",
        }

    def concatSamestr(pstr: str, pstrToConcat: str) -> str:
        firstIndex: int = pstr.find(pstrToConcat)
        previousIndex: int = 0
        currentIndex: int = firstIndex
        while currentIndex != -1:
            previousIndex = currentIndex
            currentIndex = pstr.find(pstrToConcat, previousIndex + 1)
            if currentIndex == firstIndex:
                break
            if currentIndex == previousIndex + len(pstrToConcat):
                pstr = pstr[0:currentIndex] + pstr[currentIndex + len(pstrToConcat) :]
                currentIndex -= len(pstrToConcat)
        return pstr

    def getDelimitedText(
        pText: str,
        pFirstDelimiter: str,
        pSecondDelimiter: str,
        pIncludeDelimiter: bool = False,
    ) -> list[str]:
        r = re.findall(re.escape(pFirstDelimiter) + r"(.*)" + re.escape(pSecondDelimiter), pText)
        r = [_.lstrip(pFirstDelimiter).rstrip(pSecondDelimiter) for _ in r]
        if pIncludeDelimiter:
            r = [pFirstDelimiter + _ + pSecondDelimiter for _ in r]
        return r

    def noAccent(src: str) -> str:
        if StringUtils.pattern is None:
            StringUtils.initPatterns()
        return StringUtils.decomposeUnicode(src)

    def decomposeUnicode(src: str) -> str:
        toCheck: str = src if len(StringUtils.accents) < len(src) else StringUtils.accents
        toLoop: str = StringUtils.accents if len(StringUtils.accents) < len(src) else src
        for c in toLoop:
            if c in toCheck:
                src = re.sub(c, StringUtils.pattern[c], src)
        return src

    def getDelimitedText(
        pText: str, pFirstDelimiter: str, pSecondDelimiter: str, pIncludeDelimiter: bool = False
    ) -> list[str]:
        delimitedText: str = None
        firstPart: str = None
        secondPart: str = None
        returnedArray = list[str]()
        exit: bool = False
        text: str = pText
        while not exit:
            delimitedText = StringUtils.getSingleDelimitedText(
                text, pFirstDelimiter, pSecondDelimiter, pIncludeDelimiter
            )
            if delimitedText == "":
                exit = True
            else:
                returnedArray.append(delimitedText)
                if not pIncludeDelimiter:
                    delimitedText = pFirstDelimiter + delimitedText + pSecondDelimiter
                firstPart = text[: text.index(delimitedText)]
                while pFirstDelimiter in firstPart:
                    firstPart = firstPart.replace(pFirstDelimiter, "")
                secondPart = text[text.index(delimitedText) + len(delimitedText) :]
                text = firstPart + secondPart
        return returnedArray

    def getSingleDelimitedText(
        pStringEntry: str, pFirstDelimiter: str, pSecondDelimiter: str, pIncludeDelimiter: bool = False
    ) -> str:
        firstDelimiterIndex = 0
        nextFirstDelimiterIndex = 0
        nextSecondDelimiterIndex = 0
        numFirstDelimiter = 0
        numSecondDelimiter = 0
        diff = 0
        delimitedContent = ""
        currentIndex = 0
        secondDelimiterToSkip = 0
        exit = False
        firstDelimiterIndex = pStringEntry.find(pFirstDelimiter, currentIndex)
        if firstDelimiterIndex == -1:
            return ""
        currentIndex = firstDelimiterIndex + len(pFirstDelimiter)
        while not exit:
            nextFirstDelimiterIndex = pStringEntry.find(pFirstDelimiter, currentIndex)
            nextSecondDelimiterIndex = pStringEntry.find(pSecondDelimiter, currentIndex)
            if nextSecondDelimiterIndex == -1:
                exit = True
            if nextFirstDelimiterIndex < nextSecondDelimiterIndex and nextFirstDelimiterIndex != -1:
                allIndexes = StringUtils.getAllIndexOf(
                    pFirstDelimiter,
                    pStringEntry[nextFirstDelimiterIndex + len(pFirstDelimiter) : nextSecondDelimiterIndex],
                )
                secondDelimiterToSkip += len(allIndexes)
                currentIndex = nextSecondDelimiterIndex + len(pFirstDelimiter)
            elif secondDelimiterToSkip > 1:
                currentIndex = nextSecondDelimiterIndex + len(pSecondDelimiter)
                secondDelimiterToSkip -= 1
            else:
                delimitedContent = pStringEntry[firstDelimiterIndex : nextSecondDelimiterIndex + len(pSecondDelimiter)]
                exit = True
        if delimitedContent != "":
            if not pIncludeDelimiter:
                delimitedContent = delimitedContent[len(pFirstDelimiter) :]
                delimitedContent = delimitedContent[0 : len(delimitedContent) - len(pSecondDelimiter)]
            else:
                numFirstDelimiter = len(StringUtils.getAllIndexOf(pFirstDelimiter, delimitedContent))
                numSecondDelimiter = len(StringUtils.getAllIndexOf(pSecondDelimiter, delimitedContent))
                diff = numFirstDelimiter - numSecondDelimiter
                if diff > 0:
                    while diff > 0:
                        firstDelimiterIndex = delimitedContent.find(pFirstDelimiter)
                        nextFirstDelimiterIndex = delimitedContent.find(
                            pFirstDelimiter, firstDelimiterIndex + len(pFirstDelimiter)
                        )
                        delimitedContent = delimitedContent[nextFirstDelimiterIndex]
                        diff -= 1
                elif diff < 0:
                    while diff < 0:
                        delimitedContent = delimitedContent[: delimitedContent.index(reversed(pSecondDelimiter))]
                        diff += 1
        return delimitedContent

    def getAllIndexOf(pStringLookFor: str, pWholeString: str) -> list:
        index = pWholeString.find(pStringLookFor)
        indices = []
        while index != -1:
            indices.append(index)
            index = pWholeString.find(pStringLookFor, index + 1)
        return indices
    
if __name__ == "__main__":
    def testGetDelimitedText():
        string = "(((Qa=1940&Qo>13584)|Qf=1940)&PO>9935,0)"
        res = StringUtils.getDelimitedText(string, "(", ")")
        print(res)

    def testGetAllIndexOf():
        test_cases = [
            ("test", "this is a test string with test cases"),
            ("a", "banana"),
            ("xyz", "this has no match"),
            (" ", "spaces should be counted too")
        ]

        for substring, string in test_cases:
            result = StringUtils.getAllIndexOf(substring, string)
            print(f"Indices of '{substring}' in '{string}': {result}")

    def testGetSingleDelimitedText():
        # Updated Test Cases
        test_cases = [
            ("Hello [World]!", "[", "]", False, "World"),
            ("Hello [World]!", "[", "]", True, "[World]"),
            ("[Start] and [End]", "[", "]", False, "Start"),
            ("No delimiters here", "{", "}", False, ""),
            ("Empty delimiters []", "[", "]", False, ""),
            ("Nested [delimiters [like] this]", "[", "]", False, "delimiters [like] this"),
            ("Deeply [nested [delimiters [like] this] example]", "[", "]", False, "nested [delimiters [like] this] example"),
            ("Mismatched delimiters", "[", "}", False, ""),
            ("Delimiters at [the] start", "[", "]", False, "the"),
            ("Delimiters at the end [of]", "[", "]", False, "of"),
            ("[Multiple] [delimiters] in [one] string", "[", "]", False, "Multiple"),
            ("Special characters <|like|> these", "<|", "|>", False, "like"),
            ("Escaped delimiters \\[not\\] a match", "\\[", "\\]", False, "not"),
            ("Unbalanced [delimiters [like this", "[", "]", False, ""),
            ("Unbalanced delimiters like] this]", "[", "]", False, ""),
            ("Delimiters in [reverse] order]", "[", "]", False, "reverse"),
            ("Empty string", "[", "]", False, ""),
            ("Only delimiters []", "[]", "[]", False, ""),
            ("Same opening and closing delimiter [[content[[", "[", "[", False, "content"),
            ("Multiple same delimiters %%first%% and %%second%%", "%", "%", False, "first"),
            ("Overlapping delimiters [[[nested]]]", "[", "]", False, "[nested")
        ]

        # Running the tests
        for text, start_delim, end_delim, include_delim, expected in test_cases:
            result = StringUtils.getSingleDelimitedText(text, start_delim, end_delim, include_delim)
            assert result == expected, f"Test failed for '{text}'. Expected: '{expected}', Got: '{result}'"
            print(f"Test passed for '{text}'. Result: '{result}'")
        
    testGetSingleDelimitedText()